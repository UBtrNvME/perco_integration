from datetime import datetime, timedelta
import pytz

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"
    work_place = fields.Many2many(
        string="Working Place",
        comodel_name="acs.zone",
        column1="employee",
        column2="zone",
        relation="employee_working_place_rel")

    @api.model
    def sort_employee_by(self):
        print("im here")
        date_now = fields.Date.today()
        print(date_now)
        time_to_attend = (datetime(year=date_now.year, month=date_now.month, day=date_now.day, hour=9, minute=0,
                                  second=0)-timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
        time_today = (datetime(year=date_now.year, month=date_now.month, day=date_now.day, hour=0, minute=0,
                              second=0)-timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
        late_employee_ids = []
        print(time_to_attend, time_today,late_employee_ids)
        employees = self.env["hr.employee"].search([])
        print(employees.ids)
        for employee in employees.ids:
            print(employee)
            todays_first_employee_attendance_before_time_to_attend = self.env["hr.attendance"].search(
                [["id", "=", employee],
                 "&",
                 ["check_in", "<=", time_to_attend],
                 ["check_in", ">", time_today]
                 ],
                limit=1)
            print(todays_first_employee_attendance_before_time_to_attend)
            if not todays_first_employee_attendance_before_time_to_attend.id:
                late_employee_ids.append(employee)
                print(late_employee_ids)

        return {
            'type'     : 'ir.actions.act_window',
            'name'     : "Late Employees",
            'view_mode': "tree,kanban,form",
            'res_model': 'hr.employee',
            'domain'   : [["id", "in", late_employee_ids]],
            'target'   : "current"
        }
