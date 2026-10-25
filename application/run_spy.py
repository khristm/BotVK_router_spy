from application.utils import refresh_cache_devices
from application.offline_devices import manager_offline_devices
from loguru import logger

async def spy(cached_devices_in_router, cached_names_devices, snmp_reader, ip_router, community, port_snmp,
              send_messenger, user_id_in_messenger):
    current_data, error = await snmp_reader(host=ip_router, community=community, port=port_snmp)
    enabled_devices, disabled_devices, cached_devices_in_router = refresh_cache_devices(
                                                                                cache_devices=cached_devices_in_router,
                                                                                incoming_list=current_data
                                                                            )
    if error and send_messenger and user_id_in_messenger:
        await send_messenger(message=error, user_id=user_id_in_messenger)
        return
    msg_enable_device = ''
    msg_disable_device = ''
    checked_enabled_devices = manager_offline_devices.check_online_list(enabled_devices, ip_router,
                                                                        user_id_in_messenger)
    checked_disabled_devices = manager_offline_devices.check_offline_list(disabled_devices, ip_router,
                                                                          user_id_in_messenger)
    for device in checked_enabled_devices:
        msg_enable_device += (f"✅ Устройство ℹ️{cached_names_devices.get(device.mac_address, device.description)}ℹ️, "
                              f"подключено к роутеру ✍ {ip_router}, с ip адресом: {device.ip_address}, "
                              f"MAC-адрес: {device.mac_address}\n")
    for device in checked_disabled_devices:
        msg_disable_device += (f"❌ Устройство ℹ️{cached_names_devices.get(device.mac_address, device.description)}ℹ️, "
                               f"отключено от роутера ✍ {ip_router}, "
                               f"ip адрес ранее присвоеный клиенту: {device.ip_address}, "
                               f"MAC-адрес: {device.mac_address}\n")
    if msg_enable_device:
        logger.info(msg_enable_device)
        if send_messenger and user_id_in_messenger:
            await send_messenger(message = msg_enable_device, user_id = user_id_in_messenger)
    if msg_disable_device:
        logger.info(msg_disable_device)
        if send_messenger and user_id_in_messenger:
            await send_messenger(message = msg_disable_device, user_id = user_id_in_messenger)