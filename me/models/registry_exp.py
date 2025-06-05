from odoo import fields, models


class RegistryExp(models.Model):
    _name = "me.registry_exp"
    _inherit = "tmc.document_exp"
    _description = "Expediente Registry"

    # Campos específicos del expediente
    entry_date = fields.Date(
        default=fields.Date.context_today,
        required=True,
        string="Fecha de ingreso al TMC"
    )

    external_key = fields.Char(
        string="Clave Externa",
        help="lo usa la Muni para identificar los expedientes"
    )
