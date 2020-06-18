from odoo import api, models, fields


class AjacentZonesWizard(models.TransientModel):
    ajacent_zone_ids = fields.One2many(comodel_name="acs.zone", string="Adjacent Zones")
    controller_id = fields.Many2oneReference(string='Related Controller ID', index=True, required=True,
                                             model_field="acs_controller")

