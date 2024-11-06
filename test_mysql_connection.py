import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Your MySQL root password (leave blank if no password)
        database='climavista_pro',
        port=3307
    )
    if connection.is_connected():
        print("Connection successful")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        connection.close()
