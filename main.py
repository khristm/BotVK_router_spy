from application.cfg import DELAY as DELAY_FROM_CFG, GROUP_ID
from application.snmp import get_online_device
from application.messenger import send_message_to_vk, get_messenger
from application.cfg import set_logger_config
from application.run_spy import spy
from application.handlers import handlers, default_handler
from aiovk.longpoll import BotsLongPoll
import time
import asyncio
from loguru import logger
from application.database import mok_users as users, get_router_notif_status
import json

set_logger_config()

async def start_polling():
    async with get_messenger() as vk_session:
        while True:
            try:
                poll = BotsLongPoll(session_or_api=vk_session, group_id=GROUP_ID)
                logger.debug("Поллинг включен")
                async for event in poll.iter():
                    logger.debug("Обработка события")
                    if event.get("type") == "message_new":
                        message_data = event["object"]["message"]
                        peer_id = message_data["peer_id"]
                        text = message_data["text"].strip().lower()
                        logger.debug(f"message_data в сообщении: {message_data}")
                        handler = handlers.get(text, None)
                        if handler:
                            asyncio.create_task(handler(user_id=peer_id))
                            continue
                        payload_raw = message_data.get("payload", None)
                        if payload_raw:
                            try:
                                payload = json.loads(payload_raw)
                                command, param = payload.get("command").split(" ",1)
                                if command and param:
                                    handler = handlers.get(command, None)
                                if handler:
                                    asyncio.create_task(handler(user_id=peer_id, param=param))
                                    continue
                            except Exception as exc:
                                logger.error(f"Не смогли десериализовать payload из сообщения, ошибка: {exc}, "
                                             f"payload: {payload_raw}")
                        asyncio.create_task(default_handler(peer_id))
            except Exception as exception:
                logger.critical(f"Ошибка при поллинге VK: {exception}")
                await asyncio.sleep(30)

async def start_watching_router_users_list():
    delay = 0
    while True:
        await asyncio.sleep(delay)
        start_time = time.time()
        tasks = []
        for user in users.keys():
            for router in users[user]['routers'].keys():
                if router is None:
                    continue
                notif_status_enable = get_router_notif_status(user, router)
                logger.debug(f"Статус уведомлений у роутера {router} - {notif_status_enable}")
                if get_router_notif_status(user,router):
                    tasks.append(spy(cached_devices_in_router=users[user]['routers'][router]['cached_devices'],
                                 cached_names_devices=users[user]['cached_names'],
                                 snmp_reader=get_online_device,
                                 ip_router=router,
                                 community=users[user]['routers'][router]['community'],
                                 port_snmp=users[user]['routers'][router]['port'],
                                 send_messenger=send_message_to_vk,
                                 user_id_in_messenger=user))
        await asyncio.gather(*tasks)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if DELAY_FROM_CFG - elapsed_time > 0:
            delay = DELAY_FROM_CFG - elapsed_time
        else:
            delay = 0

async def main():
    await asyncio.gather(start_polling(),start_watching_router_users_list())


if __name__ == "__main__":
    try:
        logger.info("Запуск скрипта")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.exception(e)