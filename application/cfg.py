import os, sys, asyncio
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger
import yaml

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def setup_path()->Path:
    if getattr(sys, 'frozen', False):
        project_root = Path(sys.executable).parent  # Берет путь папки, где РЕАЛЬНО лежит твой .exe файл
    else:
        current_file: Path = Path(__file__).absolute()  # Работает как раньше, когда запускаешь через python main.py
        project_root: Path = current_file.parent.parent
    return project_root

project_path = setup_path()

def set_logger_config():
    logger.remove()
    logger.add(
        os.path.join(project_path,"app_debug.log"),             # Имя файла лога
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", # Чистый формат
        level=LOG_LEVEL,               # Записывать всё: от DEBUG до CRITICAL
        rotation="10 MB",            # Создать новый файл, если текущий превысил 10 МБ
        retention="5 days",          # Хранить логи только за последние 5 дней
        compression="zip",           # Старые логи автоматически сжимать в ZIP-архив
        encoding="utf-8"             # Корректная запись кириллицы
    )

path_env = os.path.join(project_path, ".env")

load_dotenv(dotenv_path=path_env)

PATH_USER_CONFIG = str(os.getenv("PATH_USER_CONFIG"))
path_yml = os.path.join(project_path, PATH_USER_CONFIG)
DELAY = int(os.getenv("DELAY_CHECK_ROUTER_SECONDS"))
DELAY_OFFLINE_DEVICE_NOTIF_MINUTES = int(os.getenv("DELAY_OFFLINE_DEVICE_NOTIF_MINUTES"))
OID_ONLINE_DEVICE = os.getenv("OID_ONLINE_DEVICE")
TOKEN_MESSENGER = os.getenv("TOKEN_MESSENGER")
GROUP_ID = os.getenv("GROUP_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")

def get_user_cfg(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # yaml.safe_load защищает от выполнения вредоносного кода внутри YAML
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError as e:
        logger.critical(f"Ошибка: Файл '{file_path}' не найден.")
        raise e
    except yaml.YAMLError as exc:
        logger.critical(f"Ошибка синтаксиса в YAML-файле:\n{exc}")
        raise exc

if __name__=="__main__":
    setup_path()
    logger.debug(get_user_cfg(path_yml))