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

## Documentation
[The documentation can be found at here](https://easyconfig.readthedocs.io)

## Features

- Default `.yml` file generation
- Environment variable expansion
- Support for docker secrets
- Callbacks when values of the configuration change

## Why not pydantic settings
A pydantic settings object is a non-mutable object.
With easyconfig you can create a global configuration and just import it into your modules.
When your application starts you can read the configuration e.g. from a settings file and the object values
will change the values accordingly.

Additionally, easyconfig can create a default configuration file with the specified default
values and comments of the pydantic models.
That way the users can have some guidance how to change the program behaviour.


### Expansion
It's possible to use environment variable or files for expansion. Easyconfig will load all values

# Changelog
#### 0.4.1 (2025-04-01)
- added easyconfig.Field to have proper type hint for the ``in_file`` parameter


# Changelog
#### 0.4.0 (2024-12-10)
- Minimum required python version is now 3.10
- Added preprocessor to so it's possible to move and deprecate configuration entries
- Added property to get the loaded configuration file
- Many fixes
- Updated CI and code linters

#### 0.3.2 (2024-01-10)
- Updated CI and code linters

#### 0.3.1 (2023-11-10)
- Updated dependencies and code linters

#### 0.3.0 (2023-03-17)
- Breaking: requires pydantic 2.0
- Added support for variable expansion through environment variables and docker secrets

#### 0.2.8 (2023-02-08)
- Fix for StrictBool

#### 0.2.7 (2023-01-09)
- Fixed default generation for data types that inherit from python base types

#### 0.2.6 (2022-12-21)
- Fixed an issue where the default yaml file would not be created properly when using aliases in container

#### 0.2.5 (2022-10-21)
- Marked package as PEP 561 compatible (py.typed)

#### 0.2.4 (2022-04-19)
- Default values get validated, too

#### 0.2.3 (2022-04-08)
- Added extra kwargs check for pydantic fields
- Added option to get generated yaml as a string

#### 0.2.2 (2022-03-31)
- Added convenience base classes ``AppBaseModel`` and ``BaseModel``
- Works with private attributes and class functions
- Fixed an issue where multiline comments would not be created properly
- Added an option to exclude entries from config file

#### 0.2.1 (2022-03-25)
- Allow callbacks for file defaults

#### 0.2.0 (2022-03-25)
- Switched to new and more flexible API
- File default and config default are now separated

#### 0.1.2 (2022-03-08)
- Comments get nicely intended
- Fixed an issue with nested data structures
- Allow to specify a different value for file creation

#### 0.1.1 (2022-02-26)
- Fixed an issue with dynamic defaults
- Optional values with default None will not be created in the yaml file

#### 0.1.0 (2022-01-10)
- Updated requirements

#### 0.0.2 (2021-09-16)
- Validate user defaults
- Use json representation of values to get native yaml data types
- Use enum values instead of enum types

#### 0.0.1 (2021-09-14)
- Initial release
