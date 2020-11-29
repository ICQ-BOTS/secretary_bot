import sqlite3
import random

database = 'database.sqlite'

def init_db():
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("""
    CREATE table user (
        id integer primary key,
        first_name text,
        last_name text,
        user_id integer
    );
    """)
    cursor.execute("""
    CREATE table post (
        id integer primary key,
        text_post text,
        public text,
        author_id integer,
        is_anon text
    );
    """)
    cursor.execute("""
    CREATE table public (
        id integer primary key,
        token text,
        seq_key text,
        chat text,
        type text,
        first_message text
    );
    """)
    connect.close()

def get_post(post_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM post WHERE id="+str(post_id))
    posts = cursor.fetchall()
    connect.close()
    if posts:
        post = list(posts[0])
    else:
        return []
    if post[4] == "public":
        info = check_user(post[3])
        post[1] = post[1] + "\n\nАвтор: " + info["first_name"] + " " + info["last_name"]
    return post

def update_message(token,message):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("UPDATE public SET first_message='"+message+"' WHERE token='"+str(token)+"'")
    connect.commit()
    connect.close()

def update_сhat(token,chat):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("UPDATE public SET chat='"+chat+"' WHERE token='"+str(token)+"'")
    connect.commit()
    connect.close()

def update_type(type_chat,token):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("UPDATE public SET type='"+type_chat+"' WHERE token='"+str(token)+"'")
    connect.commit()
    connect.close()

def add_bot(token):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM public")
    try:
        new_id = str(cursor.fetchall()[-1][0] + 1)
    except:
        new_id = 1
    random_str = "qwertyuiopasdfghjklzxcvbnm123456789"
    seq_key = ""
    for i in range(0,10):
        seq_key += random_str[random.randint(0, 34)]
    cursor.execute("insert into public values ("+str(new_id)+",'"+token+"','"+seq_key+"','chat','both','none')")
    connect.commit()
    connect.close()
    return seq_key

def get_public(token):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM public WHERE token='"+str(token)+"'")
    res = cursor.fetchall()
    return res

def add_user(user_id,first_name = "",last_name= ""):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM user")
    try:
        new_id = str(cursor.fetchall()[-1][0] + 1)
    except:
        new_id = 1
    cursor.execute("insert into user values ("+str(new_id)+",'"+first_name+"','"+last_name+"',"+str(user_id)+")")
    connect.commit()
    connect.close()

def get_tokens():
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM public")
    publics = cursor.fetchall()
    connect.close()
    tokens = []
    for public in publics:
        tokens.append(public[1])
    return tokens

def check_user(user_id,token=None):
    result = {}
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id=" + str(user_id))
    res = cursor.fetchall()
    if token:
        cursor.execute("SELECT * FROM public WHERE token='"+token+"'")
        public_id = cursor.fetchall()[0][0]
        cursor.execute("SELECT * FROM admin WHERE public_id=" + str(public_id)+" and user_id="+str(user_id))
        admin = cursor.fetchall()
        try:
            if admin[0]:
                result["is_admin"] = True
            else:
                result["is_admin"] = False
        except:
            result["is_admin"] = False
    connect.close()
    try:
        if res[0]:
            result["not_exist"] = False
            result["id"] = res[0][3]
            result["first_name"] = res[0][1]
            result["last_name"] = res[0][2]
    except:
        result["not_exist"] = True
    return result

def check_public(token):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM public WHERE token='"+token+"'")
    res = cursor.fetchall()
    connect.close()
    result = {}
    try:
        if res[0]:
            result["not_exist"] = False
            result["seq_key"] = res[0][2]
            result["chat"] = res[0][3]
    except:
        result["not_exist"] = True
    return result

def add_post(text,is_anon,user_id,public):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM post")
    try:
        new_id = cursor.fetchall()[-1][0] + 1
    except:
        new_id = 1
    if new_id > 10001:
        new_id = new_id - 10000
        delete_post(new_id)
    cursor.execute("SELECT id FROM user")
    author_id = check_user(user_id)["id"]
    cursor.execute("insert into post values ("+str(new_id)+",'"+text+"','"+public+"',"+str(author_id)+",'"+is_anon+"')")
    connect.commit()
    connect.close()
    return new_id

def get_db(table):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM "+table)
    result = cursor.fetchall()
    connect.close()
    return result

def delete_post(new_id):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute("DELETE FROM public WHERE id="+str(new_id))
    connect.commit()
    connect.close()

if __name__ == '__main__': 
	init_db()
