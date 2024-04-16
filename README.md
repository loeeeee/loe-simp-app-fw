# loe-simp-app-fw

A super simple python app framework that includes a logger and a config manager. This framework is also useable in Jupyter Notebook.

## Example

```python
import os

from loe_simp_app_fw.config import Config
from loe_simp_app_fw.logger import Logger

Config("config.yaml", example_config_path="config-example.yaml", project_root_path=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
Logger("log", project_root_path=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
```

It will read from 

```bash
[project root path]/"config.yaml"
```

The example config is located at

```bash
[project root path]/"config-example.yaml"
```

The log file will be at

```bash
[project root path]/"log"/yyyy-mm-dd.log
```

## Usage

Logger usage

```python
Logger.debug("This is a debug message.")
Logger.info("This is a info message.")
Logger.warning("This is a warning message.")
Logger.error("This is a error message.")
```

Config usage

```python
something = Config.config["package root path"]
```

## Advance Usage

Config hot reload

```python
Config("another-config.yaml")
```

## Gitignore

```.gitignore
log/
config*.yaml
!config-example.yaml
```
