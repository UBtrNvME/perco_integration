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
        self.cursor.execute(self.query + self.generate_query_body_for_event())
        records = self.cursor.fetchall()
        return records

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

        return _get_time_domain_for_event(40)

    def create_attendance(self, data):
        print("nigger")
        # self.env['hr.attendance'].create(data)

    def search_employee_ids(self):
        employees = self.env['hr.employee'].search([])
        employee_ids = {}
        for employee in employees:
            employee_ids[employee.name] = employee.id
        return employee_ids

    @api.one
    def import_from_db(self):
        self.establish_connection()
        records = self.execute_query()
        employee_ids = self.search_employee_ids()
        print("nigger")
        for record in records:
            print(record)
            employee_name = record[0] + " " + record[1]
            try:
                employee_id = employee_ids[employee_name]
            except KeyError:
                print("Following employee (%s) is not present in odoo database!")
                continue
            data = {
                "employee_id": employee_id
            }
            print(data)
            self.create_attendance(data)
        self.cursor.close()
        self.connection.close()
