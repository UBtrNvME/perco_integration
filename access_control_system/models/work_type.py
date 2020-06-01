from odoo import fields, models, api


class WorkType (models.Model):
    _name = 'acs.work.type'
    _description = 'Work Type'

    name = fields.Char(string="Type Name")