import json
from application.database import get_routers_ip, get_router_notif_status

def get_routers_keyboard(user_id):
    keyboard = {
            "inline": True,  # Свойство инлайн-клавиатуры
            "buttons": []
    }
    user_routers = get_routers_ip(user_id)
    if not user_routers:
        return None
    for router in user_routers:
        keyboard["buttons"].append([
            {
                "action": {
                            "type": "text",
                            "label": f"Клиенты на роутере {router}🌐",
                            "payload": json.dumps({"command": f"show_router {router}"})
            },
                "color": "primary"  # Синяя кнопка
            }
        ])
    return json.dumps(keyboard, ensure_ascii=False)

def get_notif_keyboard(user_id):
    keyboard = {
            "inline": True,  # Свойство инлайн-клавиатуры
            "buttons": []
    }
    user_routers = get_routers_ip(user_id)
    if not user_routers:
        return None
    for router in user_routers:
        if get_router_notif_status(user_id, router):
            lbl_str = "Отключить"
            command = "disable_notif"
        else:
            lbl_str = "Включить"
            command = "enable_notif"
        keyboard["buttons"].append([
            {
                "action": {
                            "type": "text",
                            "label": f"{lbl_str} слежение за {router}🌐",
                            "payload": json.dumps({"command": f"{command} {router}"})
            },
                "color": "primary"  # Синяя кнопка
            }
        ])
    return json.dumps(keyboard, ensure_ascii=False)




