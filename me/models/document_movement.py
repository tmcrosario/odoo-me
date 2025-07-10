from odoo import fields, models

class Movement(models.Model):
    _name = "me.document_movement"
    _description = "Movimiento de Expediente"

    expediente_id = fields.Many2one(
        "me.document_exp", string="Expediente", required=True, ondelete="cascade"
        )
    date = fields.Datetime(
        string="Fecha", default=fields.Datetime.now, required=True
        )
    origin_dependence_id = fields.Many2one(
        "tmc.dependence", string="Dependencia Origen"
        )
    destination_dependence_id = fields.Many2one(
        "tmc.dependence", string="Dependencia Destino"
        )
    # notes = fields.Text(string="Observaciones")
    user_id = fields.Many2one(
        "res.users", string="Usuario", default=lambda self: self.env.user
        )