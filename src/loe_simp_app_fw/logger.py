import os
import datetime
from . import helper

# Do not write the Log until the explicit initialization of the logger

class Logger:
    # Following parameters should be set at the top-level environment of the project
    _project_root_path = ""
    _log_folder_path = "" # The path of _example_config_path relative to _project_root_path
    
    # Internal variable
    _log_buffer = []
    _isInit = False
    _file_name = f"{datetime.date.today()}.log"

    @staticmethod
    def _log_location():
        return os.path.join(Logger._project_root_path, Logger._log_folder_path, Logger._file_name)

    def __init__(self, log_folder_path: str):
        Logger._log_folder_path = log_folder_path
        
        _isInit = True
        pass


    main_file_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # Checking if log folder exists. If not, create a new one.abs
    folder_name = f"{main_file_path}/log/"
    if not os.path.isfile(folder_name) and not os.path.isdir(folder_name):
        helper.create_folder_if_not_exists(folder_name)
        
    # Checking if log file exists. If not, create a new one.
    if not os.path.isfile(file_name) and not os.path.isdir(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            print("Create log file successful.")
            pass
    
    with open(file_name, "a", encoding="utf-8") as f:
        f.writelines(f"\n{datetime.datetime.now()} INIT Logger successful\n")

    @staticmethod
    def info(msg: str) -> None:
        Logger._log("INFO", msg)

    @staticmethod
    def debug(msg: str) -> None:
        Logger._log("DEBUG", msg)

    @staticmethod
    def warning(msg: str) -> None:
        Logger._log("WARNING", msg)

    @staticmethod
    def error(msg :str) -> None:
        Logger._log("ERROR", msg)

    @staticmethod
    def _log(level: str, msg: str) -> None:
        Logger.update_file_name()
        with open(Logger.file_name, "a", encoding="utf-8") as f:
            f.writelines(f"{datetime.datetime.now()} {level.upper()}: {msg}\n")
        return

    @staticmethod
    def update_file_name() -> None:
        # An API wrapper for logger._update_file_name()
        Logger.file_name = Logger._update_file_name()
        return

    @staticmethod
    def _update_file_name() -> str:
        # Automatic rotating file names
        main_file_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return f"{main_file_path}/log/{datetime.date.today()}.log"

def logger_showoff() -> None:
    # Demonstrate the logger
    print(f"Today is {datetime.date.today()}")
    Logger.info("LOGGER IS DeMoInG.")

if __name__ == "__main__":
    logger_showoff()