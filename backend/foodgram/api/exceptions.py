from rest_framework import status
from rest_framework.exceptions import APIException


class UserNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Пользователь не найден."
    default_code = "user_not_found"


class WrongPassword(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Введен неверный пароль."
    default_code = "wrong_password"


class InvalidData(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_data"

    def __init__(self, field):
        detail = {field: "Введено неверное значение."}
        super().__init__(detail)
