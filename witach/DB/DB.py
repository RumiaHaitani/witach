from mysql.connector import (connection)

class DB:
    @staticmethod
    def connect():
        try:
            cnx = connection.MySQLConnection(user='root', password='',
                                 host='127.0.0.1',
                                 database='witach')
            cursor = cnx.cursor(dictionary=True)
            return cnx, cursor
        except:
            return None