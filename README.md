# loe-simp-app-fw
A super simple python app framework that includes a logger and a config management

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