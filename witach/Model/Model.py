from DB.DB import DB

class Model:
    table_name = None
    
    @classmethod
    def get_all(cls):
        try:
            con, cur = DB.connect()
            sql = f"SELECT * FROM `{cls.table_name}`"
            cur.execute(sql)
            result = cur.fetchall()
            con.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    @classmethod
    def get_one(cls, id:int):
        try:
            con, cur = DB.connect()
            sql = f"SELECT * FROM `{cls.table_name}` WHERE id = %(id)s"
            cur.execute(sql, {
               "id":id 
            })
            result = cur.fetchone()
            con.close()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    @classmethod
    def delete(cls, id:int):
        try:
            con, cur = DB.connect()
            sql = f"DELETE FROM {cls.table_name} WHERE id = %(id)s"
            cur.execute(sql, {
               "id":id 
            })
            result = cur.rowcount
            con.commit()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @classmethod
    def count(cls):
        try:
            con, cur = DB.connect()
            sql = f"SELECT COUNT(*) as count FROM {cls.table_name}"
            cur.execute(sql)
            result = cur.fetchone()
            con.close()
            return result['count']
        except Exception as e:
            print(f"Error: {e}")
            return None
        

    @classmethod 
    def query_get(
        cls,
        get_params:list,
        where = [],
        tables = [],
        sorted = [],
        limit = None,
        offset = None,
        fetch_mode="all"
    ):
        try:
            sql = "SELECT "
            exec_list = []
            sql += " , ".join(get_params) + " FROM "
            if (tables):
                sql += " JOIN ".join(tables) + " "
            else:
                sql += f" {cls.table_name} "
            if where:
                sql += " WHERE "
                for option in where:
                    exec_list.append(option[2])
                    if (option[3] == "value"):
                        value = "%s"
                    elif (option[3] == "system"):
                        value = option[2]
                    logic = ""
                    if (len(option) > 4):
                        logic = option[4]
                    sql += f" {option[0]} {option[1]} {value} {logic} "
            
            if sorted:
                sql += f" ORDER BY {sorted['field']} {sorted['type']} "

            if limit:
                sql += f" LIMIT {limit} "
            if offset:
                sql += f" OFFSET {offset} "

            con, cursor = DB.connect()
            cursor.execute(sql, exec_list)
            if fetch_mode == "all":
                res = cursor.fetchall()
            elif fetch_mode == "one":
                res = cursor.fetchone()
            con.close()
            return res
        except Exception as e:
            print(e)
            return None
        
    @classmethod
    def update_col(cls, name_col, where):
        try:
            con, cur = DB.connect()
            keys = list(name_col.keys())
            params = [f"%s" for i in keys]
            zap = ",".join([f"{keys[i]} = {params[i]}" for i in range(len(keys))])
            sql = f"UPDATE {cls.table_name} SET {zap} "
            exec_list = list(name_col.values())
            if where:
                sql += " WHERE "
                for option in where:
                    exec_list.append(option[2])
                    if (option[3] == "value"):
                        value = "%s"
                    elif (option[3] == "system"):
                        value = option[2]
                    logic = ""
                    if (len(option) > 4):
                        logic = option[4]
                    sql += f" {option[0]} {option[1]} {value} {logic} "
            cur.execute(sql, exec_list)
            con.commit() 
            return cur.rowcount
        except Exception as e:
            print(e)
            return None
        
    @classmethod
    def query_add(cls, data):
        try:
            con, cur = DB.connect()
            keys = ", ".join(list(data.keys()))
            params = ", ".join([f"%s" for i in list(data.keys())])
            sql = f"INSERT INTO `{cls.table_name}` ({keys}) VALUES ({params})"
            cur.execute(sql, list(data.values()))
            con.commit()
            return cur.rowcount
        except Exception as e:
            print(e)
            return None
