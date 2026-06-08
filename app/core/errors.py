# errors.py - custom exceptions

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# BaseAppException
class BaseAppException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


# --- 400 Bad Request Errors ---


class BadRequestError(BaseAppException):
    # generic bad request - use when input is invalid
    def __init__(self, message: str = "Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, "BAD_REQUEST", message)


class DuplicateResourceError(BaseAppException):
    # raised when a unique constraint would be violated - username, email..
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(status.HTTP_400_BAD_REQUEST, "DUPLICATE_RESOURCE", message)


class InvalidCredentialsError(BaseAppException):
    # raised when login fails - vague output for security
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "INVALID_CREDENTIALS", message)


class InactiveAccountError(BaseAppException):
    # raised when a deactivated user tries to log in
    def __init__(self, message: str = "Account is inactive"):
        super().__init__(status.HTTP_403_FORBIDDEN, "INACTIVE_ACCOUNT", message)


# --- 403 Forbidden errors ---


class ForbiddenError(BaseAppException):
    # raised when a user is authenticated but not authorized for this action
    def __init__(self, message: str = "Not Authorized"):
        super().__init__(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message)


class SellerRequiredError(BaseAppException):
    # raised when a non-seller tries to create an auction
    def __init__(self, message: str = "Seller account required"):
        super().__init__(status.HTTP_403_FORBIDDEN, "SELLER_REQUIRED", message)


class AdminRequiredError(BaseAppException):
    # raised when a non-admin tries to access admin endpoints
    def __init__(self, message: str = "Admin account required"):
        super().__init__(status.HTTP_403_FORBIDDEN, "ADMIN_REQUIRED", message)


# --- 404 Not Found Errors ---


class NotFoundError(BaseAppException):
    # generic not found - use when a resource doesn't exist
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message)


# --- 422 Business rule errors ---


class AuctionNotActiveError(BaseAppException):
    # raised when someone tries to bid on a closed or cancelled auction
    def __init__(self, message: str = "Auction is not active"):
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "AUCTION_NOT_ACTIVE", message
        )


class SelfBidError(BaseAppException):
    # raised when a seller tries to bid on their own auction
    def __init__(self, message: str = "Cannot bid on your own auction"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_CONTENT, "SELF_BID", message)


class BidTooLowError(BaseAppException):
    # raised when a bid is below the minimum price
    def __init__(self, message: str = "Bid is below minimum price"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_CONTENT, "BID_TOO_LOW", message)


# --- Exception handlers ---

"""
These are registered in main.py and called automatically by FastAPI
when a matching exception is raised anywhere in the app
"""


async def app_exeption_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    # handles all custom exceptions - reuturns consistent JSON
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # handles pydantic validation errors - fires when request body fail schema validation

    errors = exc.errors()

    # extract the field bame and message from each validation error
    formatted = [
        {"field": str(err["loc"][-1]), "message": err["msg"]} for err in errors
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": {"code": "VALIDATION_ERROR", "errors": formatted}},
    )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    # handles FastAPI's built-in HTTPException — fires when OAuth2PasswordBearer
    # raises 401 for missing token before our code even runs
    # we reformat it into our consistent error shape
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {"code": "HTTP_ERROR", "message": exc.detail}},
    )
