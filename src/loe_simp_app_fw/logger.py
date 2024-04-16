import os
import datetime
from .helper import create_folder_if_not_exists, ProjectRootChanged

# Do not write the Log until the explicit initialization of the logger

class Logger:
    # Following parameters should be set at the top-level environment of the project
    _project_root_path = ""
    _log_folder_path = "" # The path of _example_config_path relative to _project_root_path
    
    # Internal variable
    _log_buffer = []
    _isInit = False
    
    @staticmethod
    def _log_location():
        file_name = f"{datetime.date.today()}.log"
        return os.path.join(Logger._project_root_path, Logger._log_folder_path, file_name)

    @staticmethod
    def _create_log_file():
        if not os.path.isfile(Logger._log_location()) and not os.path.isdir(Logger._log_location()):
            with open(Logger._log_location(), "w", encoding="utf-8") as f:
                print("Create log file successfully.")

    def __init__(self, log_folder_path: str, project_root_path: str = os.getcwd()):
        """Init Logger

        Args:
            log_folder_path (str): path to log folder relative to project root path
            project_root_path (str, optional): path to project top-level directory. Defaults to os.getcwd().

        Raises:
            ProjectRootChanged: Project root directory should not be changed once set
        """
        # Sanity check
        if Config._project_root_path and project_root_path and os.path.samefile(project_root_path, Config._project_root_path):
            Logger.error("One should not change project root path twice")
            raise ProjectRootChanged

        # Save input
        Logger._log_folder_path = log_folder_path
        Logger._project_root_path = project_root_path

        # Create log folder
        folder_name = os.path.join(Logger._project_root_path, Logger._log_folder_path)
        if not os.path.isfile(folder_name) and not os.path.isdir(folder_name):
            create_folder_if_not_exists(folder_name)

        # Save previous logs
        with open(Logger._log_location(), "a", encoding="utf-8") as f:
            f.writelines(f"\n{datetime.datetime.now()} INIT Logger successful\n")
            f.writelines("".join(Logger._log_buffer))
        
        # Empty log buffer
        Logger._log_buffer = []

        # Update flags
        _isInit = True
        print("Logger init process finished.")

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
        # Compose log
        composed_log_entry = f"{datetime.datetime.now()} {level.upper()}: {msg}\n"
        if Logger._isInit:
            # Write to file
            with open(Logger._log_location, "a", encoding="utf-8") as f:
                f.writelines(composed_log_entry)
        else:
            # Write to buffer, not file
            Logger._log_buffer.append(composed_log_entry)
            print(composed_log_entry)
        return
        

def logger_showoff() -> None:
    # Demonstrate the logger
    Logger("log")
    print(f"Today is {datetime.date.today()}")
    Logger.info("LOGGER IS DeMoInG.")

if __name__ == "__main__":
    logger_showoff()