class EasyConfigError(Exception):
    pass


class SubscriptionAlreadyCanceledError(EasyConfigError):
    pass


class DuplicateSubscriptionError(EasyConfigError):
    pass


class ExtraKwArgsNotAllowedError(EasyConfigError):
    pass


class FileDefaultsNotSetError(EasyConfigError):
    pass


class FunctionCallNotAllowedError(EasyConfigError):
    def __init__(self):
        super().__init__('Call "load_config_dict" or "load_config_file" on the app config instance!')


# -----------------------------------------------------------------------------
# Errors related to environment variable replacement
# -----------------------------------------------------------------------------
class EasyConfigEnvVarError(EasyConfigError):
    pass


class CyclicEnvironmentVariableReferenceError(EasyConfigEnvVarError):
    pass
