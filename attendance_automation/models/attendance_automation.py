from odoo import fields, models, api
import datetime
from collections import defaultdict
import logging


_logger = logging.getLogger(__name__)


class AttendanceAutomation(models.Model):
    _inherit = "hr.attendance"

    def generate_query_body_for_event(self):
        def _get_time_domain_for_event():
            datetime_now = datetime.datetime.now()
            datetime_start = datetime_now - datetime.timedelta(minutes=1)
            sql_datetime_now = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
            sql_datetime_start = datetime_start.strftime("%Y-%m-%d %H:%M:%S")
            print(sql_datetime_now)
            # return " WHERE e.db_time_label >= '%s' AND e.db_time_label <= '%s'" % (timelabels[0], timelabels[1])
            return " WHERE e.db_time_label >= '%s' AND e.db_time_label <= '%s'" % (
                sql_datetime_start, sql_datetime_now)

        QUERY = "SELECT e.id, u.first_name, u.last_name, u.middle_name, e.db_time_label, e.device_id FROM event e" \
                " LEFT JOIN user_card uc USING(identifier)" \
                " LEFT JOIN user u ON e.user_id = u.id"

        _logger.warn("QUERY:")
        _logger.warn(QUERY + _get_time_domain_for_event())

        return QUERY +_get_time_domain_for_event()

    def make_attendance(self, **kwargs):
        print("make attendance")
        reader_id = kwargs["reader_id"]
        reader = self.env["acs.controller.reader"].search([["id", "=", reader_id]])
        if reader.type == "enter":
            print("ENTER")
            data = {"employee_id": kwargs["employee_id"]}
            try:
                self.env['hr.attendance'].create(data)
            except SystemError as e:
                print(e, "has been detected")
        elif reader.type == "exit":
            print("EXIT")
            data = {"check_out": kwargs["timelabel"]}
            try:
                self.env["hr.attendance"].search([["employee_id", "=", kwargs["employee_id"]]], limit=1).write(data)
            except SystemError as e:
                print(e, "has been detected")
        else:
            print("Device with ID = %d has not been found in the system!"
                  % (reader_id if reader_id is not None else 0))

    # def search_employee_ids(self):
    #     employees = self.env['hr.employee'].search([])
    #     employee_ids = {}
    #     for employee in employees:
    #         employee_ids[employee.name] = employee.id
    #     return employee_ids

    def get_employee_id(self, employee_name):
        employee_id = 0
        try:
            employee_id = self.env["hr.employee"].search([["name", "=", employee_name.rstrip()]]).id
        except:
            pass
        finally:
            print("get_employee_id ", employee_id)
            return employee_id

    def sort_mysql_records(self, unsorted_records):
        sorted_records = defaultdict(dict)
        _logger.warn("mysql_records:")
        _logger.warn(unsorted_records)
        if unsorted_records != []:
            for id, first_name, last_name, middle_name, db_time_label, device_id in unsorted_records:
                first_name = first_name if first_name != None else ""
                middle_name = middle_name if middle_name != None else ""
                last_name = last_name if last_name != None else ""

                name = last_name + " " + first_name + " " + middle_name
                if name == "":
                    continue

                name = name if name[-1] != " " else name[:-1]
                sorted_records[name][id] = [db_time_label, device_id]
        _logger.warn("mysql_records:")
        _logger.warn(sorted_records)
        return sorted_records

    def sort_odoo_records(self, unsorted_records):
        sorted_records = defaultdict(dict)
        if unsorted_records is not None:
            for attendance in unsorted_records:
                sorted_records[attendance.employee_id.id][attendance.id] = [attendance.check_in, attendance.check_out]
        print("odoo_records ", sorted_records)
        return sorted_records

    @api.model
    def cron_job(self, data):
        _logger.warn("Cron have started!!")
        if datetime.datetime.now() > datetime.datetime.now().replace(hour=0, minute=0, second=0) \
                and datetime.datetime.now() < datetime.datetime.now().replace(hour=16, minute=0, second=0):

            # date = datetime.date.today()
            # array = [[str(date) + " 00:00:00", str(date) + " 03:00:00"],
            #          [str(date) + " 03:00:00", str(date) + " 07:00:00"],
            #          [str(date) + " 07:00:00", str(date) + " 08:00:00"],
            #          [str(date) + " 08:00:00", str(date) + " 12:00:00"]]

            # domain = [str(data[0]), str(data[1]), str(data[2])]
            mysql = self.env["mysql.connector"].search([["name_in_form_view", "=", data]])
            _logger.warn(mysql)
            if mysql:
                mysql.establish_connection()
                odoo_attendances = self.sort_odoo_records(self.env["hr.attendance"].search(
                    ["|",
                     "&", ("check_in", "<=", datetime.datetime.now()), ("check_in", ">=", mysql.pivot_time),
                     "&", ("check_out", "<=", datetime.datetime.now()), ("check_out", ">=", mysql.pivot_time)]
                ))
                mysql_attendances = self.sort_mysql_records(
                    mysql.execute_query(self.generate_query_body_for_event())
                )
                _logger.warn("ODOO ATTENDANCES:")
                _logger.warn(odoo_attendances)
                _logger.warn("MYSQL ATTENDANCES:")
                _logger.warn(mysql_attendances)
                if mysql_attendances != {}:
                    for employee in mysql_attendances:
                        employee_id = self.get_employee_id(employee)
                        try:
                            print(len(mysql_attendances[employee]))
                            if len(mysql_attendances[employee]) % 2 != 0:
                                this_employee_attendances = odoo_attendances.pop(employee_id)
                                print("cron_job ", this_employee_attendances)
                                latest_attendance_id = max(this_employee_attendances, key=int)
                                valid_attendance_id = min(mysql_attendances[employee], key=int)
                                latest_attendance = this_employee_attendances[latest_attendance_id]
                                current_attendance = mysql_attendances[employee][valid_attendance_id]
                                print("cron_job ", latest_attendance, current_attendance)
                                if latest_attendance[1] == False and current_attendance[0] - latest_attendance[
                                    0] >= datetime.timedelta(minutes=1):
                                    self.make_attendance(reader_id=current_attendance[1],
                                                         employee_id=employee_id,
                                                         timelabel=current_attendance[0] - datetime.timedelta(hours=6))
                                else:
                                    self.make_attendance(reader_id=current_attendance[1],
                                                         employee_id=employee_id,
                                                         timelabel=current_attendance[0] - datetime.timedelta(hours=6))
                        except:
                            print("Problems with following Employee")
