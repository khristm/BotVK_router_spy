import asyncio
import random
from aiovk import API, TokenSession, drivers
from contextlib import asynccontextmanager
from application.cfg import TOKEN_MESSENGER
from loguru import logger
import aiohttp
import json



@asynccontextmanager
async def get_messenger():
    connector = aiohttp.TCPConnector(ssl=False)
    custom_driver = drivers.HttpDriver(session=aiohttp.ClientSession(connector=connector))
    async with TokenSession(TOKEN_MESSENGER, driver=custom_driver) as session:
        vk = API(session)
        yield vk

async def send_message_to_vk(user_id, message, keyboard=None):
    async with get_messenger() as vk:
        try:
            await vk.messages.send(
                peer_id=user_id,
                message=message,
                random_id=random.randint(1, 10000),
                keyboard=keyboard if keyboard else json.dumps([])
            )
        except Exception as e:
            logger.critical(f"Error sending message to vk, user_id: {user_id}, exception: {e}")
