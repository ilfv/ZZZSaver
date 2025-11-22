class BaseError(Exception):
    ...


class ApiError(BaseError):
    ...


class NoInternetConnection(ApiError):
    ...


class EmptyResponce(ApiError):
    ...
