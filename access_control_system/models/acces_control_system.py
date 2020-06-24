from odoo import api, fields, models
from odoo.http import request
from odoo.tools import logging


_logger = logging.getLogger(__name__)


class Zone(models.Model):
    _name = 'acs.zone'
    _description = 'Access zones'

    name = fields.Char(string="Zone Name", translate=True)
    permitted_roles = fields.Many2many(comodel_name="hr.job", string="Permitted Jobs", translate=True)
    description = fields.Text(string="Description", translate=True)
    parent_id = fields.Many2one(string="Parent Zone", comodel_name="acs.zone", translate=True)
    controller_id = fields.Many2one(comodel_name="acs.controller",
                                    string="Controller", translate=True)
    # adjacent_zone_ids = fields.Many2many(comodel_name="acs.zone", column1="zone1", column2="zone2",
    #                                      relation="adjacent_zone_rel", string="Adjacent Zones", translate=True)
    # exit_reader_ids = fields.One2many(comodel_name="acs.controller.reader", inverse_name="to_zone")
    # enter_reader_ids = fields.One2many(comodel_name="acs.controller.reader", inverse_name="from_zone")

    def open_readers_view(self):
        self.ensure_one()
        return {
            'type'     : 'ir.actions.act_window',
            'name'     : 'Readers View',
            'view_mode': "kanban,form",
            'res_model': 'acs.controller.reader',
            'domain'   : [('controller_id', '=', self.controller_id.id)],
            'context'  : {'default_controller_id': self.controller_id.id},
            'flags'    : {'action_buttons': True},
        }

    @api.model
    def create(self, values):
        zone = super(Zone, self).create(values)
        if values["parent_id"]:
            parent = self.env["acs.zone"].browse([values["parent_id"]])[0]
            # Setting permitted roles to the parent zone or inheriting them, in case no permits were passed
            if "permitted_roles" in zone:
                rec_permitted_roles = zone.permitted_roles.ids
                parent_permitted_roles = parent.permitted_roles.ids
                united_list_of_roles = list(set(rec_permitted_roles) | set(parent_permitted_roles))
                parent.write({"permitted_roles": [[6, 0, united_list_of_roles]]})
            else:
                zone.permitted_roles = [[6, 0, parent.permitted_roles.ids]]
            # Inheriting controller from parent zone if controller id was not passed
            if not values["controller_id"]:
                zone.controller_id = parent.controller_id.id

        # Creating readers for the zones
        self.env["acs.controller.reader"].create({"name"         : "Reader[%d,%d]" % (zone.id, zone.parent_id.id),
                                                  "controller_id": zone.controller_id.id,
                                                  "from_zone_id" : zone.id,
                                                  "to_zone_id"   : zone.parent_id.id})
        self.env["acs.controller.reader"].create({"name"         : "Reader[%d,%d]" % (zone.parent_id.id, zone.id),
                                                  "controller_id": zone.controller_id.id,
                                                  "from_zone_id" : zone.parent_id.id,
                                                  "to_zone_id"   : zone.id})

        # values["adjacent_zone_ids"] = [[4, parent.id, 0]]

        return zone

    def write(self, values):
        if "permitted_roles" in values:
            if self.parent_id:
                rec_permitted_roles = values["permitted_roles"][0][2]
                parent_permitted_roles = self.parent_id.permitted_roles.ids
                united_list_of_roles = list(set(rec_permitted_roles) | set(parent_permitted_roles))
                self.parent_id.permitted_roles = [[6, 0, united_list_of_roles]]
        if "parent_id" in values:
            parent = self.env["acs.zone"].browse([values["parent_id"]])[0]
            # values["adjacent_zone_ids"] = [[4, parent.id, 0]]
        return super(Zone, self).write(values)


class Controller(models.Model):
    _name = 'acs.controller'
    _description = 'Control System'

    name = fields.Char(string="Controller's Code", translate=True)

    zone_id = fields.One2many(comodel_name="acs.zone", string="Zones", inverse_name="controller_id", translate=True)
    reader_ids = fields.One2many(comodel_name="acs.controller.reader", inverse_name="controller_id", translate=True)


class ControllerReader(models.Model):
    _name = "acs.controller.reader"
    _description = "Control Reader"

    name = fields.Char(string="Reader's Code", translate=True)
    external_id = fields.Integer(string="External Id", )
    controller_id = fields.Many2one(string="Controller", comodel_name="acs.controller", required=True,
                                    translate=True)
    from_zone_id = fields.Integer(string="Id of the Zone from")
    to_zone_id = fields.Integer(string="Id of the Zone to")
    from_zone_name = fields.Char(string="To Zone Name", compute="_compute_from_zone_name", store=True)
    to_zone_name = fields.Char(string="From Zone Name", compute="_compute_to_zone_name", store=True)

    @staticmethod
    def __compute_zone_name(id):
        zones = request.env["acs.zone"].browse(ids=[id])
        print(zones[0].name)
        return str(zones[0].name)

    @api.depends("from_zone_id")
    def _compute_from_zone_name(self):
        for reader in self:
            reader.from_zone_name = reader.__compute_zone_name(reader.from_zone_id)

    @api.depends("to_zone_id")
    def _compute_to_zone_name(self):
        for reader in self:
            reader.to_zone_name = reader.__compute_zone_name(reader.to_zone_id)

    def get_permitted_role_ids(self):
        for reader in self:
            zone = reader.controller_id.zone_id
            return zone.permitted_roles.ids