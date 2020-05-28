from odoo import fields, api, models
import mysql.connector
import datetime
from mysql.connector import Error


class MysqlConnector(models.Model):
    _name = "mysql.connector"
    host = fields.Char(string="Host address")
    database = fields.Char(string="Database name")
    port = fields.Char(string="Database port")
    username = fields.Char(string="Username")
    password = fields.Char(string="User password")
    connection = None
    cursor = None
    query = fields.Char(string="Query")
    model_name = fields.Char(string="Model name")

    def establish_connection(self):
        self.connection = mysql.connector.connect(host=self.host,
                                                  database=self.database,
                                                  user=self.username,
                                                  password=self.password,
                                                  port=self.port)
        self.cursor = self.connection.cursor()

    def execute_query(self):
        self.cursor.execute(self.query)
        records = self.cursor.fetchall()
        return records


class MysqlConnectorAttendance(models.Model):
    _inherit = "mysql.connector"
    _name = "mysql.connector.attendance"


    def generate_query_body_for_event(self):
        def _get_time_domain_for_event(delta_hours):
            datetime_now = datetime.datetime.now()
            datetime_start = datetime_now - datetime.timedelta(hours=delta_hours)
            sql_datetime_now = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
            sql_datetime_start = datetime_start.strftime("%Y-%m-%d %H:%M:%S")
            print(sql_datetime_start, sql_datetime_now)
            return " WHERE e.db_time_label >= '%s' AND e.db_time_label <= '%s'" % (sql_datetime_start, sql_datetime_now)

        QUERY = "SELECT u.first_name, u.last_name, e.db_time_label FROM event e" \
                " LEFT JOIN user_card uc USING(identifier)" \
                " LEFT JOIN user u ON e.user_id = u.id"

        return QUERY + _get_time_domain_for_event(3)

    def create_attendance(self, data):
        self.env['hr.attendance'].create(data)

    def search_employee_ids(self):
        employees = self.env['hr.employee'].search([])
        employee_ids = {}
        for employee in employees:
            employee_ids[employee.name] = employee.id
        return employee_ids

    def import_from_db(self):
        records = self.execute_query()
        employee_ids = self.search_employee_ids()
        for record in records:
            employee_name = record[0] + " " + record[1]
            try:
                employee_id = employee_ids[employee_name]
            except KeyError:
                print("Following employee (%s) is not present in odoo database!")
                continue
            data = {
                "employee_id": employee_id
            }
            self.create_attendance(data)