from odoo import fields, api, models
import mysql.connector
import datetime
from mysql.connector import Error


class MysqlConnector(models.AbstractModel):
    _name = "mysql.connector"
    host = fields.Char(string="Host address")
    database = fields.Char(string="Database name")
    port = fields.Char(string="Database port")
    username = fields.Char(string="Username")
    password = fields.Char(string="User password")
    connection = None
    cursor = None

    def establish_connection(self):
        self.connection = mysql.connector.connect(host=self.host,
                                                  database=self.database,
                                                  user=self.username,
                                                  password=self.password,
                                                  port=self.port)
        self.cursor = self.connection.cursor()

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
        except Error:
            records = False
        finally:
            return records

    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.disconnect()
        except:
            pass