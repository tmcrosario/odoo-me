from odoo import api, fields, models


class DocumentExp(models.Model):
    _name = "me.document_exp"
    _inherits = {"tmc.document": "document_id"}
    _description = "Expediente Registry"

    document_id = fields.Many2one(
        "tmc.document",
        required=True,
        ondelete="cascade",
        string="Documento",
    )
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
    asunto = fields.Char(
        string="Asunto",
        help="Asunto específico del expediente"
    )
    tentative_name = fields.Char(
        string="Nombre Tentativo",
        compute="_compute_tentative_name",
        store=True,
        help="Nombre tentativo del expediente"
    )

    number = fields.Integer(required=True)  # Heredado, pero lo forzamos obligatorio aquí

    @api.depends('number', 'period')
    def _compute_tentative_name(self):
        for record in self:
            if record.number and record.period:
                record.tentative_name = f"EXP-{str(record.number).zfill(6)}-DEM/{record.period}"
            else:
                record.tentative_name = False

    @api.model
    def create(self, vals):
        doc_fields = [
            "dependence_id", "document_type_id", "number", "period", "date", "document_object"
        ]
        document_vals = {field: vals[field] for field in doc_fields if field in vals}
        vals["document_id"] = self.env["tmc.document"].create(document_vals).id
        record = super().create(vals)
        # Crear registro en RAA
        self.env["raa.registry_aa"].create({
            "document_id": record.document_id.id,
            "entry_date": record.entry_date,
        })
        return record

    def write(self, vals):
        doc_fields = [
            "dependence_id", "document_type_id", "number", "period", "date", "document_object"
        ]
        document_vals = {field: vals[field] for field in doc_fields if field in vals}
        if document_vals:
            self.document_id.write(document_vals)
        return super().write(vals)

    def unlink(self):
        for record in self:
            record.document_id.unlink()
        return super().unlink()
