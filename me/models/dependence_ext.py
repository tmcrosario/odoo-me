from odoo import fields, models


class Dependence(models.Model):
    _inherit = "tmc.dependence"

    is_internal = fields.Boolean(
        string="Internal",
        default=False,
        help=(
            "True when this dependence belongs to the Tribunal "
            "(internal routing unit). Used to detect institutional reentry "
            "in expediente movement sequences."
        ),
    )
