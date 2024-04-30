import sys
import os

package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
src_folder_path = os.path.join(package_path, "src")
print(src_folder_path)
sys.path.append(src_folder_path)

from loe_simp_app_fw.config import Config
from loe_simp_app_fw.logger import Logger


Config("config.yaml", example_config_path="config-example.yaml", project_root_path=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

Logger.debug("Should be in both terminal and log file (later).")

Logger("log", project_root_path=os.path.dirname(os.path.dirname(os.path.realpath(__file__))), log_level="WARNING")

something = Config.config["project root path"]

Logger.debug("Should be in the log file only.")

Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")
Logger.debug("andsfijasndif")

Logger.info("Something a little bit important")
Logger.warning("Something quite important")
Logger.error("YELLING AT YOU")


Logger.info("Something a little bit important")
Logger.warning("Something quite important")
Logger.error("YELLING AT YOU")

Logger.info("Something a little bit important")
Logger.warning("Something quite important")
Logger.error("YELLING AT YOU")