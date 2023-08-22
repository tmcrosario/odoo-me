from odoo import _, fields, models


class RegistryExp(models.Model):
    _name = "me.registry_exp"
    _description = "sarasasasasa"

    entry_date = fields.Date(default=fields.Date.context_today, required=True)

