# easyconfig
![Tests Status](https://github.com/spacemanspiff2007/easyconfig/workflows/Tests/badge.svg)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/easyconfig/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/easyconfig/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easyconfig)
![PyPI](https://img.shields.io/pypi/v/easyconfig)
[![Downloads](https://pepy.tech/badge/easyconfig/month)](https://pepy.tech/project/easyconfig)

_Easy application configuration with yaml files_

## Description
Easyconfig simplifies the configuration management for (small) applications.

Validation and parsing of the configuration file is done through [pydantic](https://pydantic-docs.helpmanual.io/)
and easyconfig builds on that.
It's possible to use all pydantic features and model features so every exotic use case should be covered.
If you have previously worked with pydantic you should feel right at home

## Why not pydantic settings
A pydantic settings object is a non-mutable object.
With easyconfig you can create a global configuration and just import it into your modules.
When your application starts you can read the configuration e.g. from a settings file and the object values
will change the values accordingly.

Additionally, easyconfig can create a default configuration file with the specified default
values and comments of the pydantic models.
That way the users can have some guidance how to change the program behaviour.

## Usage
Create your models as you did before. Then pass an instance of the model to the easyconfig function.
It will create a mutable object from the model that holds the same values.

Easyconfig also provides some mixin classes, so you can have type hints for the file load functions.
These mixins are not required, they are just there to provide type hints in the IDE.

For convenience reasons you can also import ``AppBaseModel`` and ``BaseModel`` from ``easyconfig`` so you don't have to
inherit from the mixins yourself.

### Simple example

```python
from pydantic import BaseModel
from easyconfig import AppConfigMixin, create_app_config


class MySimpleAppConfig(BaseModel, AppConfigMixin):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


# Create a global variable which then can be used throughout your code
CONFIG = create_app_config(MySimpleAppConfig())

# Use with type hints and auto complete
print(CONFIG.port)

# Load configuration file from disk.
# If the file does not exist it will be created
# Loading will also change all values of CONFIG accordingly
CONFIG.load_config_file('/my/configuration/file.yml')
```
Created configuration file:
```yaml
retries: 5
url: localhost
port: 443
```

### Nested example

Nested example with the convenience base classes from easyconfig.

```python
from pydantic import Field
from easyconfig import AppBaseModel, BaseModel, create_app_config


class HttpConfig(BaseModel):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


class MyAppSimpleConfig(AppBaseModel):
    run_at: int = Field(12, alias='run at')  # use alias to load from/create a different key
    http: HttpConfig = HttpConfig()


CONFIG = create_app_config(MyAppSimpleConfig())
CONFIG.load_config_file('/my/configuration/file.yml')

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
from easyconfig import AppBaseModel, create_app_config


class MySimpleAppConfig(AppBaseModel):
    retries: int = Field(5, description='Amount of retries on error')
    url: str = 'localhost'
    port: int = 443


CONFIG = create_app_config(MySimpleAppConfig())
CONFIG.load_config_file('/my/configuration/file.yml')
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
from easyconfig import AppBaseModel, create_app_config


class MySimpleAppConfig(AppBaseModel):
    retries: int = 5
    url: str = 'localhost'
    port: int = 443


def setup_http():
    # some internal function
    create_my_http_client(CONFIG.url, CONFIG.port)


CONFIG = create_app_config(MySimpleAppConfig())
CONFIG.load_config_file('/my/configuration/file.yml')

# setup_http will be automatically called if a value changes in the MyAppSimpleConfig
# during a subsequent call to CONFIG.load_file() or when the config gets loaded for the first time
sub = CONFIG.subscribe_for_changes(setup_http)

# It's possible to cancel the subscription again
sub.cancel()
```

# Changelog
#### 0.2.2 (25.03.2022)
- Added convenience base classes ``AppBaseModel`` and ``BaseModel``
- Works with private attributes and class functions
- Fixed an issue where multiline comments would not be created properly
- Added an option to exclude entries from config file

#### 0.2.1 (25.03.2022)
- Allow callbacks for file defaults

#### 0.2.0 (25.03.2022)
- Switched to new and more flexible API
- File default and config default are now separated

#### 0.1.2 (08.03.2022)
- Comments get nicely intended
- Fixed an issue with nested data structures
- Allow to specify a different value for file creation

#### 0.1.1 (26.02.2022)
- Fixed an issue with dynamic defaults
- Optional values with default None will not be created in the yaml file

#### 0.1.0 (10.01.2022)
- Updated requirements

#### 0.0.2 (16.09.2021)
- Validate user defaults
- Use json representation of values to get native yaml data types
- Use enum values instead of enum types

#### 0.0.1 (14.09.2021)
- Initial release
