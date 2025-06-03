from odoo import fields, models


class RegistryExp(models.Model):
    _name = "me.registry_exp"
    _description = "Expediente Registry"

    name = fields.Char(string="Nombre")
    document_id = fields.Many2one(
        comodel_name="tmc.document",
        required=True,
        ondelete="cascade",
        string="Documento",
    )

    # Campos relacionados con el documento
    number = fields.Integer(related="document_id.number", store=True)
    period = fields.Integer(related="document_id.period", store=True)
    date = fields.Date(related="document_id.date", string="Fecha de inicio de trámite", store=True)
    document_type_id = fields.Many2one(related="document_id.document_type_id", store=True)
    dependence_id = fields.Many2one(related="document_id.dependence_id", store=True)

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
