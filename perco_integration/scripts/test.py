# import mysql.connector
# from mysql.connector import Error
#
# try:
#     connection = mysql.connector.connect(host='127.0.0.1',
#                                          database='perco',
#                                          user='perco',
#                                          password='123',
#                                          port='49001')
#     sql_select_Query = "SELECT * FROM user limit "
#     cursor = connection.cursor()
#     cursor.execute(sql_select_Query)
#     records = cursor.fetchall()
#     print("Total number of rows in user is: ", cursor.rowcount)
#
#     print("\nPrinting each user record")
#     for row in records:
#         print("Id = ", row[0], )
#         print("Last Name = ", row[1])
#         print("First Name  = ", row[2])
#         print("Is Operator  = ", row[5], "\n")
#
# except Error as e:
#     print("Error reading data from MySQL table", e)
# finally:
#     if (connection.is_connected()):
#         connection.close()
#         cursor.close()
#         print("MySQL connection is closed")

import test
mysql = test.MysqlConnector()
mysql.establish_connection()
print(mysql.execute_query(mysql.generate_query_body_for_event()))
