import random


def generate_verify_code(length=6) -> str:
    return ''.join(random.choices('0123456789', k=length))
