import mysql.connector

password="root"
port=3305
database = "hms"
# def select(q):
# 	cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database,port=port)
# 	cur = cnx.cursor(dictionary=True)
# 	cur.execute(q)
# 	result = cur.fetchall()
# 	cur.close()
# 	cnx.close()
# 	return result
def select(query, params=None):
    cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database,port=port)
    cur = cnx.cursor(dictionary=True)
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()

    return result

def select_2(query, params=None):
    cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database, port=port)
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        result = cur.fetchall()
        return result
    except Exception as e:
        print("Error occurred:", str(e))
    finally:
        cur.close()
        cnx.close()

def update(q):
	cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database,port=port)
	cur = cnx.cursor(dictionary=True)
	cur.execute(q)
	cnx.commit()
	result = cur.rowcount
	cur.close()
	cnx.close()
	return result
def delete(q):
	cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database,port=port)
	cur = cnx.cursor(dictionary=True)
	cur.execute(q)
	cnx.commit()
	result = cur.rowcount
	cur.close()
	cnx.close()
	return result

        
def delete2(q, data=None):
    cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database, port=port)
    cur = cnx.cursor(dictionary=True)
    cur.execute(q, data)  # Use data as a tuple here
    cnx.commit()
    result = cur.rowcount
    cur.close()
    cnx.close()
    return result
def insert(q):
	cnx = mysql.connector.connect(user="root", password=password, host="localhost", database=database,port=port)
	cur = cnx.cursor(dictionary=True)
	cur.execute(q)
	cnx.commit()
	result = cur.lastrowid
	cur.close()
	cnx.close()
	return result