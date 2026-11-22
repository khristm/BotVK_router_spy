from aiosnmp import Snmp
from application.cfg import OID_ONLINE_DEVICE, SNMP_TIMEOUT, SNMP_RETRIES
from application.utils import str_to_obj, decode_snmp_value
from loguru import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_snmp_agent(host, community, port):
    async with (Snmp(host=host, community=community, port=port, timeout=SNMP_TIMEOUT,
                     retries=1, validate_source_addr=False) as snmp):
     yield snmp

async def get_online_device(host, community, port):
    """Возращает словарь где ключом является мак устройства а значение объект DataSnmp"""
    online_devices = {}
    oid = OID_ONLINE_DEVICE
    logger.debug(f'host = {host}, community = {community}, port = {port}, oid = {oid}')
    async with get_snmp_agent(host, community, port) as snmp:
        while True:
            # цикл перебора ответов snmp, выход по окончании ветки OID
            snmp.timeout = SNMP_TIMEOUT
            count_retries = 1
            while True:
                # цикл для кастомных ретраев с увеличением таймаута при каждом повторном запросе
                try:
                    response = await snmp.get_next(oid)
                    break
                except Exception as e:
                    error = (f"❌Ошибка сбора данных с маршрутизатора: \n"
                             f"❌Ошибка: {e!r},\n❌IP адрес: {host},\n❌OID: {oid},\n❌Попытка: {count_retries},\n"
                             f"❌Таймаут snmp запроса: {snmp.timeout}")
                    logger.error(error)
                    if count_retries >= SNMP_RETRIES:
                        logger.exception(e)
                        return online_devices, error
                    count_retries += 1
                    snmp.timeout = snmp.timeout * 1.5
            logger.debug(f"Snmp response value: {response[0].value}, OID: {response[0].oid}")
            oid = response[0].oid
            if OID_ONLINE_DEVICE not in oid:
                return online_devices, None
            string_response = decode_snmp_value(response[0].value)
            device = str_to_obj(string_response)
            online_devices[device.mac_address] = device