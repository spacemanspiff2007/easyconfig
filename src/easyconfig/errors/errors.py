class SubscriptionAlreadyCanceledError(Exception):
    pass


class DuplicateSubscriptionError(Exception):
    pass


class ReferenceFolderMissingError(Exception):
    pass


class FunctionCallNotAllowedError(Exception):
    pass


class ModelNotProperlyInitialized(Exception):
    pass
