from passlib.context import CryptContext
import hmac
import hashlib


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_hashed_cookie(login: str, secret_key: str):
    return hmac.new(secret_key.encode(), login.encode(), hashlib.sha256).hexdigest()

# Проверка хэша куки
def verify_hashed_cookie(cookie_value: str, login: str, secret_key: str):
    return hmac.compare_digest(cookie_value, create_hashed_cookie(login, secret_key))