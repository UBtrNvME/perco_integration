from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"
    work_place = fields.Many2many(
        string="Working Place",
        comodel_name="acs.zone",
        column1="employee",
        column2="zone",
        relation="employee_working_place_rel")
