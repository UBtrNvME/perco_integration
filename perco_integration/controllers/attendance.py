import json

from odoo import http
from odoo.http import request


class AttendanceController(http.Controller):

    @http.route(['/api/v1/createAttendance'], type="json", auth="public", method=['POST'],
                csrf=False)
    def createAttendace(self, employeeName):
        values = {}
        employee = request.env['hr.employee'].sudo().search([['name', '=', employeeName]])
        data = {
            'employee_id'  : employee.id,
            'department_id': employee.department_id
        }
        if employee.id:
            to_return = request.env['hr.attendance'].sudo().create(data)
            values['success'] = True
            values['return'] = to_return.id
        else:
            values['success'] = False
            values['error_code'] = 1
            values['error_data'] = 'No data found!'

        return json.dumps(values)

    @http.route(['/api/v1/finishAttendance'], type="json", auth="public", method=['POST'],
                csrf=False)
    def finishAttendance(self, employeeName):
        from odoo import fields
        values = {}
        attendance = request.env['hr.attendance'].sudo().search([['employee_id.name', '=', employeeName]], limit=1)
        if attendance.id:
            res = attendance.write({'check_out': fields.Datetime.now()})
            values['success'] = True
            values['return'] = res
        else:
            values['success'] = False
            values['error_code'] = 1
            values['error_data'] = 'No data found!'

        return json.dumps(values)
