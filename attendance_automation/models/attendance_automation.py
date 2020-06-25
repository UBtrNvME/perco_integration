import datetime
import logging
from collections import defaultdict

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AttendanceAutomation(models.Model):
    _inherit = "hr.attendance"

    zone_id = fields.Reference(string="Zone Reference", selection=[('acs.zone', "Access Zone")])

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Overriden method from hr_attendance base model, which cancels constaints for the attendances within child zones """
        for attendance in self:
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in:
                last_attendance_zone_id = last_attendance_before_check_in.zone_id
                attendance_zone_id = attendance.zone_id
                _logger.warn(f"last_attendance_zone_id={last_attendance_zone_id}\nattendance_zone_id={attendance_zone_id}")
                if attendance_zone_id.parent_id and attendance_zone_id.parent_id == last_attendance_zone_id:
                    pass
                else:
                    super()._check_validity()


    @staticmethod
    def _get_zone_reference(id):
        return "%s,%s" % ('acs.zone', id)

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

        return QUERY + _get_time_domain_for_event()

    def make_attendance(self, **kwargs):
        _logger.warn("make attendance")
        reader_id = kwargs["reader_id"]
        timelabel = kwargs["timelabel"]
        reader = self.env["acs.controller.reader"].search([["external_id", "=", reader_id]])
        employee = self.env["hr.employee"].browse(kwargs["employee_id"])[0]

        try_to_access_zone = self.env["acs.zone"].search([["id", "=", reader.to_zone_id]])
        coming_from_zone = self.env["acs.zone"].search([["id", "=", reader.from_zone_id]])
        last_attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
        ], order='check_in desc', limit=1)

        # ============================== #
        #  Rules
        # ============================== #
        # --------------------------------------------------------------------------
        _logger.warn("try_to_access_zone=%s"
                     "\nlast_attendance=%s"
                     "\ncoming_from_zone=%s"
                     % (try_to_access_zone, last_attendance, coming_from_zone))
        is_to_existing_place = (try_to_access_zone.id != False)
        is_from_existing_place = (coming_from_zone.id != False)
        is_accessing_child = try_to_access_zone and (try_to_access_zone.parent_id == last_attendance.zone_id)
        is_from_previous_zone = (last_attendance.zone_id == coming_from_zone)
        has_attendances = last_attendance
        # --------------------------------------------------------------------------
        if is_to_existing_place:
            if employee.job_id.id not in try_to_access_zone.permitted_roles.ids:
                return (employee.name, try_to_access_zone.name)

        # Handle for the people who has no previous attendance or coming from outside
        if not has_attendances or not is_from_existing_place:
            data = {
                "employee_id": employee.id,
                "zone_id": "acs.zone,%d" % try_to_access_zone.id
            }
            self.env["hr.attendance"].create(data)
            _logger.warn("Checking into %s" % try_to_access_zone.name)
            pass
        # Handle for the people moving within parent zone
        if is_from_existing_place and is_from_previous_zone:
            if try_to_access_zone and is_accessing_child:
                data = {
                    "employee_id": employee.id,
                    "zone_id": "acs.zone,%d" % try_to_access_zone.id
                }
                self.env["hr.attendance"].create(data)
                _logger.warn("Checking into %s" % try_to_access_zone.name)
            elif not last_attendance.check_out:
                last_attendance.write({"check_out": timelabel})
                _logger.warn("Checking out from %s" % last_attendance.zone_id.name)
            pass

    def search_employee_ids(self):
        employees = self.env['hr.employee'].search([])
        employee_ids = {}
        for employee in employees:
            employee_ids[employee.name] = employee.id
        return employee_ids

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

        mysql = self.env["mysql.connector"].search([["id", "=", data]])
        _logger.warn(mysql)
        if not mysql:
            pass

        mysql.establish_connection()
        mysql_attendances = self.sort_mysql_records(
            mysql.execute_query(self.generate_query_body_for_event())
        )

        if mysql_attendances == {}:
            pass

        odoo_attendances = self.sort_odoo_records(self.env["hr.attendance"].search(
            ["|",
             "&", ("check_in", "<=", datetime.datetime.now()), ("check_in", ">=", mysql.pivot_time),
             "&", ("check_out", "<=", datetime.datetime.now()), ("check_out", ">=", mysql.pivot_time)]
        ))
        _logger.warn("ODOO ATTENDANCES:")
        _logger.warn(odoo_attendances)
        _logger.warn("MYSQL ATTENDANCES:")
        _logger.warn(mysql_attendances)
        if mysql_attendances != {}:
            _logger.warn("Starting searching!!!")
            for employee in mysql_attendances:
                employee_id = self.get_employee_id(employee)
                _logger.warn("Employee id: %s" % (employee_id))
                _logger.warn("length of the record: %s" % len(mysql_attendances[employee]))
                if len(mysql_attendances[employee]) % 2 != 0:
                    this_employee_attendances = {}
                    valid_attendance_id = min(mysql_attendances[employee], key=int)
                    current_attendance = mysql_attendances[employee][valid_attendance_id]
                    if employee_id in odoo_attendances:
                        this_employee_attendances = odoo_attendances.pop(employee_id)
                    else:
                        _logger.warn("Creating Attendance")
                        info = self.make_attendance(reader_id=current_attendance[1],
                                                    employee_id=employee_id,
                                                    timelabel=current_attendance[0])
                        if info:
                            _logger.warn(
                                "Following user, %s, tried to access %s, without permission!" % (info))
                        continue
                    _logger.warn("This employee attendance:")
                    _logger.warn(this_employee_attendances)
                    latest_attendance_id = max(this_employee_attendances, key=int)
                    latest_attendance = this_employee_attendances[latest_attendance_id]

                    _logger.warn("\ncurrent-attendance: %s\nlatest-attendance: %s" % (
                        current_attendance, latest_attendance))
                    if latest_attendance[1] == False and current_attendance[0] - latest_attendance[0] >= datetime.timedelta(minutes=1):
                        _logger.warn("Creating Attendance")
                        info = self.make_attendance(reader_id=current_attendance[1],
                                                    employee_id=employee_id,
                                                    timelabel=current_attendance[0])
                        if info:
                            _logger.warn(
                                "Following user, %s, tried to access %s, without permission!" % (info))

                    else:
                        _logger.warn("Creating Attendance")
                        info = self.make_attendance(reader_id=current_attendance[1],
                                                    employee_id=employee_id,
                                                    timelabel=current_attendance[0])
                        if info:
                            _logger.warn(
                                "Following user, %s, tried to access %s, without permission!" % (info))
