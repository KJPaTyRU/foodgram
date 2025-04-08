from rest_framework.serializers import ValidationError


NUMBERS = '0123456789'


def is_not_number(value):
    for i in value:
        if i not in NUMBERS:
            return True
    return False


class MaxLengthValidator:
    def __init__(self, max_length):
        self.max_length = max_length

    def __call__(self, value):
        if len(value) > self.max_length:
            raise ValidationError(
                f'Не может быть длиннее {self.max_length} символов.'
            )
