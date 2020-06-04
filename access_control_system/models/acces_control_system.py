from odoo import fields, models, api


class Zone(models.Model):
    _name = 'acs.zone'
    _description = 'Access zones'

    name = fields.Char(string="Zone Name", translate=True)
    access_level = fields.Integer(string="Access Level", translate=True)

    parent_id = fields.Many2one(string="Parent Zone", comodel_name="acs.zone", translate=True)
    controller_ids = fields.One2many(comodel_name="acs.controller", inverse_name="zone_id",
                                     string="Controllers", translate=True)


class Controller(models.Model):
    _name = 'acs.controller'
    _description = 'Control System'

    name = fields.Char(string="Controller's Code", translate=True)
    access_level = fields.Integer(related="zone_id.access_level", translate=True)

    zone_id = fields.Many2one(comodel_name="acs.zone", string="Zones", translate=True)
    reader_ids = fields.One2many(comodel_name="acs.controller.reader", inverse_name="controller_id", translate=True)


class ControllerReader(models.Model):
    _name = "acs.controller.reader"
    _description = "Control Reader"

    name = fields.Char(string="Reader's Code", translate=True)

    controller_id = fields.Many2one(string="Controller", comodel_name="acs.controller", translate=True)
    type = fields.Selection(string="Type",
                            translate=True,
                            selection=[('enter', 'Enter'),
                                       ('exit', 'Exit')])
