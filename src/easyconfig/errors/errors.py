class EasyConfigError(Exception):
    pass


class SubscriptionAlreadyCanceledError(EasyConfigError):
    pass


class DuplicateSubscriptionError(EasyConfigError):
    pass


class ReferenceFolderMissingError(EasyConfigError):
    pass


class FunctionCallNotAllowedError(EasyConfigError):
    pass


class ModelNotProperlyInitialized(EasyConfigError):
    pass
