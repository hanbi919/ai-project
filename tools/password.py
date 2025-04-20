import secrets
import string


def generate_simple_token(length=32):
    """生成随机字母数字Token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# 生成Token
your_secret_token = generate_simple_token()
print(f"你的Rasa API Token: {your_secret_token}")
