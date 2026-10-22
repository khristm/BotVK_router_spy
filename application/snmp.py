from aiosnmp import Snmp
from application.cfg import OID_ONLINE_DEVICE
from application.utils import str_to_obj, decode_snmp_value
from loguru import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_snmp_agent(host, community, port):
    async with (Snmp(host=host, community=community, port=port, timeout=30.0, retries=1, validate_source_addr=False)
                as snmp):
     yield snmp

async def get_online_device(host, community, port):
    """Возращает словарь где ключом является мак устройства а значение объект DataSnmp"""
    online_devices = {}
    oid = OID_ONLINE_DEVICE
    logger.debug(f'host = {host}, community = {community}, port = {port}, oid = {oid}')
    async with get_snmp_agent(host, community, port) as snmp:
        while True:
            try:
                response = await snmp.get_next(oid)
            except Exception as e:
                error = (f"❌Ошибка сбора данных с маршрутизатора: \n"
                         f"❌Ошибка: {e!r},\n❌IP адрес: {host},\n❌OID: {oid}")
                logger.error(error)
                logger.exception(e)
                return online_devices, error
            logger.debug(f"Snmp response value: {response[0].value}, OID: {response[0].oid}")
            oid = response[0].oid
            if OID_ONLINE_DEVICE not in oid:
                return online_devices, None
            string_response = decode_snmp_value(response[0].value)
            device = str_to_obj(string_response)
            online_devices[device.mac_address] = device