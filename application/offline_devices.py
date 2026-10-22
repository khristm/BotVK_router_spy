from application.utils import DataSnmp
from application.cfg import DELAY_OFFLINE_DEVICE_NOTIF_MINUTES
from datetime import datetime, timedelta
from loguru import logger

class ManagerOfflineDevices:
    def __init__(self, delay_to_notif_minutes:int):
        self.delay_to_notif_minutes = delay_to_notif_minutes
        self.cache_offline_time = {}
        self.cache_offline_devices = {}
    def __clear_cache(self, devices:list[DataSnmp]):
        """Очистка кеша отключенных устройств от устройств из списка"""
        for device in devices:
            device_in_cache = self.cache_offline_devices.get(device.mac_address)
            if device_in_cache:
                del self.cache_offline_devices[device.mac_address]
            device_time_in_cache = self.cache_offline_time.get(device.mac_address)
            if device_time_in_cache:
                del self.cache_offline_time[device.mac_address]
    def check_online_list(self, online_list: list[DataSnmp])->list[DataSnmp]:
        """Возвращает список онлайн устройств очищенный от устройств находящихся в кэше отключенных.
        Удаляет из кэша отключенных устройства из списка на входе"""
        result_online_list = []
        for device in online_list:
            if self.cache_offline_time.get(device.mac_address) is None:
                result_online_list.append(device)
        self.__clear_cache(online_list)
        return result_online_list
    def check_offline_list(self, offline_list: list[DataSnmp])->list[DataSnmp]:
        """Обработка отключенных устройств, проверяет есть ли отключенное устройство уже в кэше, если нет добавляет.
        Проверяте время прошедшее с момента отключения устройства из кэша, если прошло более заданого аргумента
        для класса, добавляет в возвращаемый список и удаляет из кэша"""
        now = datetime.now()
        result_offline_list = []
        for device in offline_list:
            cached_time_offline = self.cache_offline_time.get(device.mac_address)
            if cached_time_offline is None:
                self.cache_offline_time[device.mac_address] = now
                self.cache_offline_devices[device.mac_address] = device
        for mac in self.cache_offline_time.keys():
            cached_time_offline = self.cache_offline_time[mac]
            delta = now - cached_time_offline
            if delta > timedelta(minutes=self.delay_to_notif_minutes):
                result_offline_list.append(self.cache_offline_devices[mac])
        self.__clear_cache(result_offline_list)
        logger.debug(f"Cached offline time: {self.cache_offline_time}")
        logger.debug(f"Cached offline devices: {self.cache_offline_devices}")
        return result_offline_list

manager_offline_devices = ManagerOfflineDevices(delay_to_notif_minutes=DELAY_OFFLINE_DEVICE_NOTIF_MINUTES)