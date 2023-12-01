import sqlite3 as sql

def create_db():
    try:
        conn = sql.connect('/database.db')
        conn.execute('CREATE TABLE tb_usuario (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
        print("INFO - DATABASE - Table created correctly")
        conn.close()
    except:
        print("ERROR - DATABASE - Connection cannot be succeeded")

def drop_db():
    try:
        conn = sql.connect('database.db')
        conn.execute('DROP TABLE tb_usuario')
        print("INFO - DATABASE - Table successfully deleted!")
        conn.close()
    except:
        print("ERROR - DATABASE - Connection denied")


def add_user_and_passw(username, password):
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_usuario where username=?",[username])
            con.row_factory = sql.Row
            rows = cur.fetchall()
            if rows:
                print("Username already existing!")
                return 0, False
            else:
                con.commit()
                cur.execute("INSERT INTO tb_usuario (username,password)  VALUES (?,?)",(username,password))   
                id = cur.lastrowid
                print("User, ID:",id)
                return id, True
    except:
        print("Registration error")

def check_user_and_passw(username, password):
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_usuario where username=?",[username])
            con.row_factory = sql.Row
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    user_id = row[0]
                    usuario = row[1]
                    senha = row[2]
                if senha == password:
                    print('WARNING - DATABASE - check_user_and_pass: User and password check, authenticated user!  USER_ID:',user_id, 'USER_NAME:',usuario)
                    return 2, True, user_id
                else: 
                    print('WARNING - DATABASE - check_user_and_pass: User existing but password incorrect! USER_ID:',user_id, 'USER_NAME:',usuario)
                    return 1, False, user_id
            else:
                print("ERROR - DATABASE - check_user_and_pass: user doesn't exist!")
                return 3, False, 0
    except:
        print("ERROR - DATABASE - unable to get acess to username and password from db ")
        
def get_user_and_passw(id):
    try:
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from tb_usuario")
   
        rows = cur.fetchall()
        username = rows[id]['username']
        password = rows[id]['password']
        return username, password
    except:
        print("It was not possible to get the users!")

def get_user_id(username):
    try:
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from tb_usuario where username=?", (username,))
    
        rows = cur.fetchall()
        if rows:
            for row in rows:
                user_id = row[0]
        return user_id
    except:
        print("It was not possible to get USER_ID in the database!")
