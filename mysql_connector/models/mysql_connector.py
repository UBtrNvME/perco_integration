from odoo import fields, api, models
import mysql.connector
import datetime
from mysql.connector import Error
from odoo.osv import osv


class MysqlConnector(models.Model):
    _name = "mysql.connector"
    _sql_constraints = [
        ("name_unique",
         "UNIQUE (name)",
         "Connectors name must be unique.")
    ]

    name = fields.Char(string="Name", translate=True)
    host = fields.Char(string="Host address", translate=True, default="")
    database = fields.Char(string="Database name", translate=True, default="")
    port = fields.Char(string="Database port", translate=True, default="")
    username = fields.Char(string="Username", translate=True)
    password = fields.Char(string="User password", translate=True)
    pivot_time = fields.Datetime(string="Pivot Time")

    @api.onchange("host", "port", "database")
    def _generate_name(self):
        if self.port != "" and self.host != "" and self.database != "":
            self.name = self.database + "@" + self.host + ":" + self.port

    def establish_connection(self):
        for mc in self:
            connection = mysql.connector.connect(
                host=mc.host,
                database=mc.database,
                user=mc.username,
                password=mc.password,
                port=mc.port
            )
            cursor = connection.cursor()
            return connection, cursor

    def execute_query(self, query):
        for mc in self:
            connection, cursor = mc.establish_connection()
            try:
                cursor.execute(query)
                return cursor.fetchall()
            except Error:
                return None
            finally:
                connection.disconnect()
                cursor.close()

    def check_connection(self, host, user, port, database, password):
        is_valid = True
        try:
            connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                port=port,
                password=password
            )
            connection.disconnect()
        except mysql.connector.InterfaceError:
            is_valid = False
        finally:
            return is_valid

    # def close_connection(self):
    #     for mc in self:
    #         try:
    #             mc.cursor.close()
    #             mc.connection.disconnect()
    #         except:
    #             pass

    @api.model
    def create(self, values):
        mc = super(MysqlConnector, self).create(values)
        # values["name"] = values["database"] + "@" + values["host"] + ":" + values["port"]
        # Validating connection
        if mc.check_connection(values["host"], values["username"], values["port"], values["database"],
                               values["password"]):
            return mc
        else:
            raise osv.except_osv(("Test Connection"), ("Connection you are trying to establish doesn't exist!"))
