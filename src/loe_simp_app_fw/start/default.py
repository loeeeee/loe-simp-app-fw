class ProjectConfig:
    configuration: str = \
"""
import os

from typing import ClassVar
from loe_simp_app_fw import BaseConfig, FrameworkConfig, Logger, NotInitialized

#---------------------------------------------------------------

# Modify the framework config location if necessary
FrameworkConfig.load(os.path.abspath("./config-framework.yaml"))


class ProjectConfig(BaseConfig):
    # Add tunable here
    example_tunable: ClassVar[str] = "ExAmPlE"

#---------------------------------------------------------------

if FrameworkConfig.developer_mode:
    # Skip loading the config
    '''
    Developer mode force the usage of the default configuration of ProjectConfig,
        i.e., the one above, rather than the one in config-project.yaml
    '''
    Logger.warning(f"Project config is now in developer mode, settings from config-project.yaml will be ignored")
else:
    # Load the config
    try:
        ProjectConfig.load(FrameworkConfig.project_config_path)
    except NotInitialized:
        Logger.warning(f"Cannot find project config file at {FrameworkConfig.project_config_path}.")
        ProjectConfig.dump_example(FrameworkConfig.project_config_path)
        Logger.info(f"Successfully create example project config at {FrameworkConfig.project_config_path}")

# Combine two config
class Config(ProjectConfig, FrameworkConfig):
    pass

# Init logger
Logger(Config.log_directory, project_root_path = Config.project_directory, log_level = Config.log_level, buffering = Config.log_buffer_size)

Logger.info("Configuration finish initialization")
"""

    main: str = \
"""
from loe_simp_app_fw import Logger
from .configuration import Config

"""


class GitIgnore:
    python = \
"""
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/
"""
    
    this = \
"""
# Loe's Simple App Framework
playground*
database*
config*.yaml
!config-example.yaml
raw
middleware
.cache*
perf/
temp
"""