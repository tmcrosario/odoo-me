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

    default_responsible_id = fields.Many2one(
        comodel_name='res.users',
        string="Default Responsible",
        help=(
            "User pre-filled as responsible (user_id) when this internal dependence "
            "is selected as destination in a new movement. Editable before saving. "
            "Only applies to internal dependences (is_internal=True)."
        ),
    )
