from application.cfg import  get_user_cfg, path_yml
from loguru import logger

"""Модуль создан как задел под будущую БД если вдруг захочется ее сделать, пока здесь мокаю данные из .env"""

# mok_users = {
#     USER_ID_VK: {
#         'routers' : {
#             ROUTER_IP_1 : {
#                 'community' : COMMUNITY_STRING_1,
#                 'port' : PORT_SNMP_1,
#                 'cached_devices' : {},
#                 'notif' : True
#             },
#             ROUTER_IP_2 :{
#                 'community' : COMMUNITY_STRING_2,
#                 'port' : PORT_SNMP_2,
#                 'cached_devices' : {},
#                 'notif' : False
#             }},
#         'cached_names':{
#             'f8:f0:82:c2:13:00': 'Меш агент',
#             'f8:f0:82:43:f6:23': 'ТВ-приставка',
#             '10:08:c1:1e:d8:34': 'ТВ в гостиной'
#         }
#     },
# }

mok_users = get_user_cfg(path_yml)

def get_cached_name(user_id, mac):
    cached_names = mok_users[user_id]['cached_names']
    return cached_names.get(mac, None)

def get_users(user:str):
    return mok_users.get(user, None)

def get_routers_ip(user):
    return mok_users[user]["routers"].keys()

def get_router_settings(user, router):
    try:
        return mok_users[user]["routers"][router]
    except Exception as e:
        logger.exception(e)
        return None

def get_router_notif_status(user, router):
    try:
        return mok_users[user]['routers'][router]['notif']
    except Exception as e:
        logger.exception(e)
        return False

def set_notif_status(user, router, notif:bool):
    mok_users[user]['routers'][router]['notif'] = notif