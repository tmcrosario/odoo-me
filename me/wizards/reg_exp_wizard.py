from odoo import models, fields, api

class RegExpWizard(models.TransientModel):
    _name = "reg.exp.wizard"
    _description = "Wizard para Crear Expediente como Documento"

    # Campos del wizard (datos del documento y del expediente)
    name = fields.Char(string="Nombre del Documento", required=True)
    # document_object = fields.Char(string="Objeto del Documento")
    date = fields.Date(string="Fecha del Documento", default=fields.Date.context_today)
    external_key = fields.Char(string="Clave Externa (Expediente)")
    # case_number = fields.Char(string="Número de Caso (Expediente)")

    def action_create_expediente(self):
        """Crea un nuevo documento y lo asocia como expediente."""
        # Crear el documento como expediente
        document = self.env['tmc.document'].create({
            'name': self.name,
            # 'document_object': self.document_object,
            'date': self.date,
            'document_type_id': self.env.ref('tmc_document_type_expediente').id,  # Tipo de documento "Expediente"
        })

        # Crear el expediente y asociarlo al documento
        self.env['me.registry_exp'].create({
            'document_id': document.id,
            'external_key': self.external_key,
            # 'case_number': self.case_number,
        })

        # Redirige al listado de expedientes
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expedientes',
            'res_model': 'me.registry_exp',
            'view_mode': 'tree,form',
            'target': 'current',
        }
