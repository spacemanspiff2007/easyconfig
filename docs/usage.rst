**************************************
Usage
**************************************

Create your models as you did before. Then pass an instance of the model to the easyconfig function.
It will create a mutable object from the model that holds the same values.

Easyconfig also provides some mixin classes, so you can have type hints for the file load functions.
These mixins are not required, they are just there to provide type hints in the IDE.

For convenience reasons you can also import ``AppBaseModel`` and ``BaseModel`` from ``easyconfig`` so you don't have to
inherit from the mixins yourself.


Simple example
--------------------------------------
.. exec_code::
    :language_output: yaml
    :caption_output: Generated yaml file

    from pydantic import BaseModel
    from easyconfig import AppConfigMixin, create_app_config


    class MySimpleAppConfig(BaseModel, AppConfigMixin):
        retries: int = 5
        url: str = 'localhost'
        port: int = 443


    # Create a global variable which then can be used throughout your code
    CONFIG = create_app_config(MySimpleAppConfig())

    # Use with type hints and auto complete
    CONFIG.port

    # Load configuration file from disk.
    # If the file does not exist it will be created
    # Loading will also change all values of CONFIG accordingly
    # ------------ skip: start ------------
    CONFIG.load_config_file('/my/configuration/file.yml')
    # ------------ skip: stop -------------
    # ------------ hide: start -------------
    print(CONFIG.generate_default_yaml())
    # ------------ hide: stop -------------


Nested example
--------------------------------------
Nested example with the convenience base classes from easyconfig.

.. exec_code::
    :language_output: yaml
    :caption_output: Generated yaml file

    from pydantic import Field
    from easyconfig import AppBaseModel, BaseModel, create_app_config


    class HttpConfig(BaseModel):
        retries: int = 5
        url: str = 'localhost'
        port: int = 443


    class MySimpleAppConfig(AppBaseModel):
        run_at: int = Field(12, alias='run at')  # use alias to load from/create a different key
        http: HttpConfig = HttpConfig()


    CONFIG = create_app_config(MySimpleAppConfig())
    # ------------ skip: start ------------
    CONFIG.load_config_file('/my/configuration/file.yml')
    # ------------ skip: stop -------------
    # ------------ hide: start -------------
    print(CONFIG.generate_default_yaml())
    # ------------ hide: stop -------------


Description and comments
--------------------------------------
It's possible to specify a description through the pydantic ``Field``.
The description will be created as a comment in the .yml file.
Note that the comments will be aligned properly

.. exec_code::
    :language_output: yaml
    :caption_output: Generated yaml file

    from pydantic import Field
    from easyconfig import AppBaseModel, create_app_config


    class MySimpleAppConfig(AppBaseModel):
        retries: int = Field(5, description='Amount of retries on error')
        url: str = Field('localhost', description='Url used for connection')
        port: int = 443


    CONFIG = create_app_config(MySimpleAppConfig())
    # ------------ skip: start ------------
    CONFIG.load_config_file('/my/configuration/file.yml')
    # ------------ skip: stop -------------
    # ------------ hide: start -------------
    print(CONFIG.generate_default_yaml())
    # ------------ hide: stop -------------


Expansion and docker secrets
--------------------------------------
It's possible to use environment variable or files for expansion.
To expand an environment variable or file use ``${NAME}`` or ``${NAME:DEFAULT}`` to specify an additional default if the
value under ``NAME`` is not set.
To load the content from a file, e.g. a docker secret specify an absolute file name.

Environment variables::

    MY_USER =USER_NAME
    MY_GROUP=USER: ${MY_USER}, GROUP: GROUP_NAME
    ENV_{_SIGN = CURLY_OPEN_WORKS
    ENV_}_SIGN = CURLY_CLOSE_WORKS


yaml file

.. exec_code::
    :language_output: yaml
    :hide_code:

    a = """
    env_var: "${MY_USER}"
    env_var_recursive: "${MY_GROUP}"
    env_var_not_found: Does not exist -> "${INVALID_NAME}"
    env_var_default: Does not exist -> "${INVALID_NAME:DEFAULT_VALUE}"
    file: "${/my_file/path.txt}"
    escaped: |
        Brackets {} or $ signs can be used as expected.
        Use $${BLA} to escape the whole expansion.
        Use $} to escape the closing bracket, e.g. use "${ENV_$}_SIGN}" for "ENV_}_SIGN"
        The { does not need to be escaped, e.g. use "${ENV_{_SIGN}" for "ENV_{_SIGN"
    """

    print(a)


.. exec_code::
    :language_output: yaml
    :hide_code:
    :caption_output: After expansion


    from io import StringIO
    from easyconfig.yaml import cmap_from_model, write_aligned_yaml, yaml_rt
    from easyconfig.expansion import expand_obj
    from easyconfig.expansion import load_file as load_file_module
    from os import environ


    a = """
    env_var: "${MY_USER}"
    env_var_recursive: "${MY_GROUP}"
    env_var_not_found: Does not exist -> "${INVALID_NAME}"
    env_var_default: Does not exist -> "${INVALID_NAME:DEFAULT_VALUE}"
    file: "${/my_file/path.txt}"
    escaped: |
        Brackets {} or $ signs can be used as expected.
        Use $${BLA} to escape the whole expansion.
        Use $} to escape the closing bracket, e.g. use "${ENV_$}_SIGN}" for "ENV_}_SIGN"
        The { does not need to be escaped, e.g. use "${ENV_{_SIGN}" for "ENV_{_SIGN"
    """

    load_file_module.read_file = lambda x: "<SECRET_CONTENT_FROM_FILE>"
    environ['MY_USER'] = 'USER_NAME'
    environ['MY_GROUP'] = 'USER: ${MY_USER}, GROUP: GROUP_NAME'
    environ['ENV_{_SIGN'] = 'CURLY_OPEN_WORKS'
    environ['ENV_}_SIGN'] = 'CURLY_CLOSE_WORKS'

    file = StringIO(a)
    cfg = yaml_rt.load(file)
    expand_obj(cfg)

    out = StringIO()
    yaml_rt.dump(cfg, out)
    print(out.getvalue())


Callbacks
--------------------------------------

It's possible to register callbacks that will get executed when a value changes or
when the configuration gets loaded for the first time.
This is especially useful feature if the application allows dynamic reloading of the configuration file
(e.g. through a file watcher).

.. exec_code::
    :language_output: yaml
    :caption_output: Generated yaml file

    from easyconfig import AppBaseModel, create_app_config

    class MySimpleAppConfig(AppBaseModel):
        retries: int = 5
        url: str = 'localhost'
        port: int = 443

    # A function that does the setup
    def setup_http():
        # some internal function
        create_my_http_client(CONFIG.url, CONFIG.port)

    CONFIG = create_app_config(MySimpleAppConfig())

    # setup_http will be automatically called if a value changes in the MyAppSimpleConfig
    # during a subsequent call to CONFIG.load_file() or
    # when the config gets loaded for the first time
    sub = CONFIG.subscribe_for_changes(setup_http)

    # It's possible to cancel the subscription again
    sub.cancel()

    # ------------ skip: start ------------
    # This will trigger the callback
    CONFIG.load_config_file('/my/configuration/file.yml')
    # ------------ skip: stop -------------
