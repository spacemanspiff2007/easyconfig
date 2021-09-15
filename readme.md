# easyconfig
![Tests Status](https://github.com/spacemanspiff2007/easyconfig/workflows/Tests/badge.svg)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/easyconfig/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/easyconfig/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easyconfig)
![PyPI](https://img.shields.io/pypi/v/easyconfig)
[![Downloads](https://pepy.tech/badge/easyconfig/month)](https://pepy.tech/project/easyconfig)

_Easy application configuration with yaml files_

## Description
Easyconfig simplifies the configuration management for small application.

Validation and parsing of the configuration file is done through [pydantic](https://pydantic-docs.helpmanual.io/)
and easyconfig builds on that.
It's possible to use all pydantic features and model features so every exotic use case should be covered.
If you have previously worked with pydantic you should feel right at home

## Usage
Instead of using ``BaseModel`` from pydantic there are different Models which have to be used:

```python
from easyconfig import ConfigModel  # Use this instead of BaseModel
from easyconfig import PathModel  # Use this for path configuration
from easyconfig import AppConfigModel  # Use this as a topmost Model
```

### Simple example

```python
from easyconfig import AppConfigModel


class MyAppSimpleConfig(AppConfigModel):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


# Create a global variable which then can be used throughout your code
CONFIG = MyAppSimpleConfig()

# Use with type hints and auto complete
print(CONFIG.port)

# Load configuration file from disk.
# If the file does not exist it will be created
# Loading will also change all values of CONFIG accordingly
CONFIG.load_file('/my/configuration/file.yml')
```
Created configuration file:
```yaml
retries: 5
url: localhost
port: 443
```

### Nested example

```python
from pydantic import Field
from easyconfig import AppConfigModel, ConfigModel


class HttpConfig(ConfigModel):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


class MyAppSimpleConfig(AppConfigModel):
    run_at: int = Field(12, alias='run at')  # use alias to load from/create a different key
    http = HttpConfig()


CONFIG = MyAppSimpleConfig()
CONFIG.load_file('/my/configuration/file.yml')

```
Created configuration file:
```yaml
run at: 12
http:
  retries: 5
  url: localhost
  port: 443
```

### Comments
It's possible to specify a description through the pydantic ``Field``.
The description will be created as a comment in the .yml file

```python
from pydantic import Field
from easyconfig import AppConfigModel


class MyAppSimpleConfig(AppConfigModel):
    retries: int = Field(5, description='Amount of retries on error')
    url: str = 'localhost'
    port: int = 443


CONFIG = MyAppSimpleConfig()
CONFIG.load_file('/my/configuration/file.yml')
```
Created configuration file:
```yaml
retries: 5  # Amount of retries on error
url: localhost
port: 443
```

### Callbacks
It's possible to register callbacks that will get executed when a value changes or
when the configuration gets loaded for the first time. A useful feature if the application allows dynamic reloading
of the configuration file (e.g. through a file watcher).

```python
from easyconfig import AppConfigModel


class MyAppSimpleConfig(AppConfigModel):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


def setup_http():
    create_my_http_client(CONFIG.url, CONFIG.port)


CONFIG = MyAppSimpleConfig()
CONFIG.load_file('/my/configuration/file.yml')

# setup_http will be automatically called if a value changes in the MyAppSimpleConfig
# during a subsequent call to CONFIG.load_file() or when the config gets loaded for the first time
sub = CONFIG.subscribe_for_changes(setup_http)

# It's possible to cancel the subscription again
sub.cancel()
```

### Model documentation

### ConfigModel
```python
from easyconfig import ConfigModel
from pydantic.fields import PrivateAttr

class MyConfigModel(ConfigModel):
    a = 10

    # Use PrivateAttr to declare variable which are not part of the configuration
    my_var: int = PrivateAttr()

    # implement this to do something when all values have been set
    def on_all_values_set(self):
        print('all values have been set')
        self.my_var = self.a * self.a
```


### PathModel

PathModel inherits from ConfigModel so everything that works for ConfigModel also works for PathModel

```python
from pathlib import Path
from easyconfig import PathModel, AppConfigModel


# Path objects will be automatically resolved to absolute paths
class PathContainer(PathModel):
    folder = Path('folder_path')
    exec = Path('./rel_path')


class MyAppSimpleConfig(AppConfigModel):
    folders = PathContainer()


CONFIG = MyAppSimpleConfig()
CONFIG.load_file('/my/configuration/file.yml')

CONFIG.folders.exec  # <-- /my/configuration/rel_path

# base path can be set per PathModel and is valid for all sub items
CONFIG.folders.set_file_path('/other/path')
CONFIG.load_file()

CONFIG.folders.exec  # <-- /other/path/rel_path
```


### AppConfigModel

AppConfigModel inherits from PathModel so everything that works for PathModel also works for AppConfigModel

```python
from easyconfig import AppConfigModel


class MyAppSimpleConfig(AppConfigModel):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


CONFIG = MyAppSimpleConfig()

# It's possible to set the file path without loading
CONFIG.set_file_path('/my/configuration/file.yml')

# Path can be omitted if it was passed once in load_file or set_file_path
CONFIG.load_file()

# It's also possible to load from a python dictionary
CONFIG.load_dict({'my': 'dict'})
```



# Changelog
#### 0.0.2 (16.09.2021)
- Validate user defaults
- Use json representation of values to get native yaml datatypes
- Use enum values instead of enum types


#### 0.0.1 (14.09.2021)
- Initial release
