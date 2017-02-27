from django.core import signing

from trashnetwork import settings


def generate_token(user_id: int):
    value = signing.dumps({'user_id': user_id}, salt=settings.SECRET_KEY)
    return value


def parse_token(token: str):
    origin_data = signing.loads(token, salt=settings.SECRET_KEY)
    return origin_data['user_id']
