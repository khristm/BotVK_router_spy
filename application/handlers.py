from application.messenger import send_message_to_vk
from application.database import get_users, get_router_settings, get_cached_name, set_notif_status
from application.keyboards import get_routers_keyboard, get_notif_keyboard
from application.snmp import get_online_device
from loguru import logger

handlers = {}

def register_handler(command_name):
    def decorator(func):
        handlers[command_name] = func
        return func
    return decorator

async def default_handler(user_id):
    await send_message_to_vk(user_id,f""
                                     f"Поддерживаемые команды:\n\n"
                                     f"роутер или роутеры - выбрать роутер для запроса данных о клиентах online\n\n"
                                     f"слежение - отключить/включить уведомления в чат о изменении статуса активности"
                                     f"клиентов на роутере\n\n"
                                     f"инфо - информация о том как это работает")

@register_handler("инфо")
async def get_info(user_id):
    await send_message_to_vk(user_id,"Бот на python, c использованием библиотек: aiosnmp, aiovk. "
                                     "Ссылка на исходники скрипта: https://github.com/khristm/BotVK_router_spy")

@register_handler("роутеры")
async def get_users_routers(user_id):
    user = get_users(user_id)
    logger.debug(f"Юзер с вк: {user_id}, юзер в БД: {user}")
    if user:
        user_keyboard = get_routers_keyboard(user_id)
        await send_message_to_vk(user_id, "Выбери действие: ",
                                 keyboard=user_keyboard)
    else:
        await send_message_to_vk(user_id,"Не пиши сюда больше")

@register_handler("слежение")
async def notif_routers(user_id):
    user = get_users(user_id)
    logger.debug(f"Юзер с вк: {user_id}, юзер в БД: {user}")
    if user:
        user_keyboard = get_notif_keyboard(user_id)
        await send_message_to_vk(user_id, "Выбери действие: ",
                                 keyboard=user_keyboard)
    else:
        await send_message_to_vk(user_id,"Не пиши сюда больше")

@register_handler("роутер")
async def get_users_router(user_id):
    await get_users_routers(user_id)

@register_handler("show_router")
async def get_clients_online(user_id, param):
    logger.debug(f"Handler working user_id: {user_id}, router_ip: {param}")
    router_settings = get_router_settings(user_id,param)
    if router_settings:
        await send_message_to_vk(user_id,"Делаю запрос к роутеру, жди...")
        online_devices, error = await get_online_device(host=param, community=router_settings["community"],
                                                 port=router_settings["port"])
        if error:
            logger.debug(f"Ошибка при snmp запросе к роутеру {param}: {error}")
            await send_message_to_vk(user_id,f"Чёт я поламался или роутер, ошибка при запросе:\n{error}")
            return
        msg = f"Клиенты онлайн на роутере {param}:\n"
        if not online_devices:
            msg += "Нет никого..."
        i = 1
        for device in online_devices.keys():
            cached_name = get_cached_name(user_id, device)
            msg += (f"{i}. Устройство: {cached_name if cached_name else online_devices[device].description}\n"
                    f"   IP-адрес: {online_devices[device].ip_address}\n "
                    f"  MAC-адрес: {online_devices[device].mac_address}\n")
            i += 1
        await send_message_to_vk(user_id,msg)
        return
    await send_message_to_vk(user_id,f"Какая-то странная хуйня, "
                                     f"я где-то проебал настройки для запросов к роутеру {param}")

@register_handler("disable_notif")
async def disable_notif(user_id, param):
    set_notif_status(user_id, param, False)
    await send_message_to_vk(user_id,f"Уведомления о подключеных/отключенных "
                                     f"устройствах от роутера {param} отключены")

@register_handler("enable_notif")
async def disable_notif(user_id, param):
    set_notif_status(user_id, param, True)
    await send_message_to_vk(user_id,f"Уведомления о подключеных/отключенных "
                                     f"устройствах от роутера {param} включены")