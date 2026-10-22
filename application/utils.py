
class DataSnmp:
    def __init__(self, mac_address, description, ip_address):
        self.mac_address = mac_address
        self.description = description
        self.ip_address = ip_address


def decode_snmp_value(value) -> str:
    """
    Конвертирует возвращаемое SNMP-значение в понятную строку.
    Если на вход пришла не байтовая строка (число или уже str), возвращает как есть.
    """
    if not isinstance(value, bytes):
        return str(value)
    # 1. Проверяем, не является ли это MAC-адресом (обычно 6 байт)
    # или специфической бинарной строкой данных
    if len(value) == 6 or any(b < 32 or b > 126 for b in value if b not in (9, 10, 13)):
        # Преобразуем в читаемый HEX-формат (например, 00:1a:2b:3c:4d:5e)
        return ':'.join(f'{b:02x}' for b in value)
    # 2. Если это обычный текст, декодируем в строку
    for encoding in ('utf-8', 'cp1251', 'latin-1'):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue
    # Если совсем ничего не помогло, отдаем сырой hex
    return value.hex()

def refresh_cache_devices(cache_devices: dict, incoming_list: dict)->tuple[list[DataSnmp], list[DataSnmp],dict]:
    enabled_devices = []
    disabled_devices = []
    for device in incoming_list.keys():
        if cache_devices.get(incoming_list[device].mac_address) is None:
            enabled_devices.append(incoming_list[device])
            cache_devices[incoming_list[device].mac_address] = incoming_list[device]
    for mac in cache_devices.keys():
        if mac not in incoming_list.keys():
            disabled_devices.append(cache_devices[mac])
    for device in disabled_devices:
        del cache_devices[device.mac_address]
    return enabled_devices, disabled_devices, cache_devices

def str_to_obj(string: str):
    list_str = string.split('|')
    ip_address = list_str[0].strip()[4:]
    mac = list_str[1].strip()[5:]
    name = list_str[2].strip()[6:]
    return DataSnmp(mac_address=mac, description=name, ip_address=ip_address)
