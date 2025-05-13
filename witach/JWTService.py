import jwt
import time

class JWTService:
    secret_key = "AcademyTOP"

    @classmethod
    def create_access_token(cls, data) -> str:
        payload = {
            "iat":int(time.time()),
            "exp":int(time.time()) + 60 * 60 * 24,
            "iss": 25,
            "data": data
        }
        token = jwt.encode(payload, cls.secret_key, algorithm="HS256")
        return token
    
    @classmethod
    def create_refresh_token(cls, data) -> str:
        payload = {
            "iat":int(time.time()),
            "exp":int(time.time()) + 60 * 60 * 24 * 30,
            "iss": 25,
            "data": data
        }
        token = jwt.encode(payload, cls.secret_key, algorithm="HS256")
        return token
    
    @classmethod
    def check_token(cls, token):
        try:
            payload = jwt.decode(token, cls.secret_key, algorithms="HS256")
            return {
                "status":True,
                "payload":payload
            }
        except jwt.exceptions.ExpiredSignatureError: # токен состарился
            return {
                "status":False,
                "error":"old"
            }
        except Exception as e: # другая ошибка
            return {
                "status":False,
                "error":"other"
            }








