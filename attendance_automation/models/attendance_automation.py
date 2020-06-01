from odoo import fields, models, api
import datetime


class AttendanceAutomation(models.Model):
    _inherit = "hr.attendance"
    _inherits = {
        "mysql.connector": "mysql_id"
    }

    mysql_ids = fields.Many2one('mysql.connector', required=True)

    def generate_query_body_for_event(self):
        def _get_time_domain_for_event(delta_minutes):
            datetime_now = datetime.datetime.now()
            datetime_start = datetime_now - datetime.timedelta(minutes=delta_minutes)
            sql_datetime_now = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
            sql_datetime_start = datetime_start.strftime("%Y-%m-%d %H:%M:%S")
            print(sql_datetime_start, sql_datetime_now)
            return " WHERE e.db_time_label >= '%s' AND e.db_time_label <= '%s'" % (sql_datetime_start, sql_datetime_now)

        QUERY = "SELECT u.first_name, u.last_name, u.middle_name e.db_time_label FROM event e" \
                " LEFT JOIN user_card uc USING(identifier)" \
                " LEFT JOIN user u ON e.user_id = u.id"

        return QUERY + _get_time_domain_for_event(1)

    def make_attendance(self, **kwargs):
        reader_id = kwargs["reader_id"]
        if self.env["acs.controller.reader"].search([["id", "=", reader_id], ["type", "=", "enter"]]):
            data = {"employee_id": kwargs["employee_id"]}
            try:
                self.env['hr.attendance'].create(data)
            except SystemError as e:
                print(e, "has been detected")
        else:
            data = {"employee_id": kwargs["employee_id"],
                    "check_out"  : kwargs["timelabel"]}
            try:
                self.env['hr.attendance'].write(data)
            except SystemError as e:
                print(e, "has been detected")

    # def search_employee_ids(self):
    #     employees = self.env['hr.employee'].search([])
    #     employee_ids = {}
    #     for employee in employees:
    #         employee_ids[employee.name] = employee.id
    #     return employee_ids

    def get_employee_id(self, employee_name):
        try:
            employee_id = self.env["hr.employee"].search([["name", "like", employee_name]]).id
        except:
            employee_id = 0
        finally:
            return employee_id

    def cron_job(self):
        records = []
        for mysql in self.mysql_ids:
            mysql.establish_connection()
            records.append(mysql.execute_query(self.generate_query_body_for_event()))
        for record in records:
            for first_name, last_name, middle_name, db_time_label, device_id in record:
                employee_id = self.get_employee_id(last_name + first_name + (middle_name if not "NULL" else ""))
                if employee_id:
                    self.make_attendance(employee_id=employee_id, timelabel=db_time_label, reader_id=device_id)
                else:
                    print("Problems creating record")
