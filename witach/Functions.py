import hashlib

class Functions:

    @staticmethod
    def create_password_hash(password:str):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def check_password(password:str, password_hash):
        return password_hash == hashlib.sha256(password.encode()).hexdigest()
    
