import sys
import os

package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
src_folder_path = os.path.join(package_path, "src")
print(src_folder_path)
sys.path.append(src_folder_path)

from loe_simp_app_fw.config import Config
from loe_simp_app_fw.logger import Logger

Config._project_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
Config._example_config_path = "config-example.yaml"

Config(config_path="config.yaml")