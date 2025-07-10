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
    external_key = fields.Char(
        string="Clave Externa",
        help="lo usa la Muni para identificar los expedientes"
    )
    fojas = fields.Integer(
        string="Número de fojas",
        help="Número de fojas del expediente"
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

    document_movement_ids = fields.One2many(
        "me.document_movement", "expediente_id", string="Movimientos"
    )

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
        })
        return record

    def _update_document_date(self, date_val):
        """Actualizar la fecha del documento padre evitando la validación problemática"""
        if date_val is None:
            return
            
        # Convertir a string si es necesario
        if hasattr(date_val, 'strftime'):
            date_str = date_val.strftime('%Y-%m-%d')
        elif hasattr(date_val, 'year'):
            date_str = f"{date_val.year}-{date_val.month:02d}-{date_val.day:02d}"
        else:
            date_str = str(date_val)
        
        # Actualizar directamente en la base de datos para evitar la validación
        self.env.cr.execute(
            "UPDATE tmc_document SET date = %s WHERE id = %s",
            (date_str, self.document_id.id)
        )

    def write(self, vals):
        # Separar la fecha del resto de campos
        date_val = vals.pop('date', None) if 'date' in vals else None
        
        doc_fields = [
            "dependence_id", "document_type_id", "number", "period", "document_object"
        ]
        document_vals = {field: vals[field] for field in doc_fields if field in vals}
        
        # Actualizar el documento padre sin la fecha
        if document_vals:
            self.document_id.write(document_vals)
        
        # Actualizar la fecha usando el método personalizado
        if date_val is not None:
            self._update_document_date(date_val)
        
        # Llamar al super().write() sin el campo date
        return super().write(vals)

    def unlink(self):
        for record in self:
            record.document_id.unlink()
        return super().unlink()
