from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    """
    Custom exception for when a user is not found.
    """
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class AlreadyExistsException(HTTPException):
    """
    Custom exception for when a user with the given email already exists.
    """
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class InvalidCredentialsException(HTTPException):
    """
    Custom exception for invalid authentication credentials.
    """
    def __init__(self, detail: str = "Incorrect username or password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class UnauthorizedException(HTTPException):
    """
    Custom exception for unauthorized access.
    """
    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class BadRequestException(HTTPException):
    """
    Custom exception for input related issues.
    """
    def __init__(self, detail: str = "Something went wrong with the input data."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class InternalErrorException(HTTPException):
    """
    Custom exception for input related issues.
    """
    def __init__(self, detail: str = "Something went wrong, kindly check after sometime"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

