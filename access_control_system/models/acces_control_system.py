from odoo import fields, models, api


class Zone(models.Model):
    _name = 'acs.zone'
    _description = 'Access zones'

    name = fields.Char(string="Zone Name")
    access_level = fields.Integer(string="Access Level")

    controller_ids = fields.One2many(comodel_name="acs.controller", inverse_name="zone_id",
                                     string="Controllers")


class Controller(models.Model):
    _name = 'acs.controller'
    _description = 'Control System'

    name = fields.Char(string="Controller's Code")

    access_level = fields.Integer(related="zone_id.access_level")

    zone_id = fields.Many2one(comodel_name="acs.zone", string="Zones")
    reader_ids = fields.One2many(comodel_name="acs.controller.reader", inverse_name="controller_id")


class ControllerReader(models.Model):
    _name = "acs.controller.reader"
    _description = "Control Reader"

    name = fields.Char(string="Reader's Code")

    controller_id = fields.Many2one(string="Controller", comodel_name="acs.controller")
    type = fields.Selection(string="Type",
                            selection={"enter": "Enter",
                                       "exit" : "Exit"})
