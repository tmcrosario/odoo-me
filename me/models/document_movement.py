from odoo import _, api, exceptions, fields, models


class Movement(models.Model):
    _name = "me.document_movement"
    _description = "Movimiento de Expediente"

    _unique_movement = models.Constraint(
        'UNIQUE(expediente_id, origin_dependence_id, destination_dependence_id, date)',
        'Ya existe un movimiento idéntico para este expediente '
        '(mismo origen, destino y fecha exacta).',
    )

    expediente_id = fields.Many2one(
        "me.document_exp", string="Expediente", required=True, ondelete="cascade"
    )
    date = fields.Datetime(
        string="Fecha", default=fields.Datetime.now, required=True
    )
    origin_dependence_id = fields.Many2one(
        "tmc.dependence", string="Dependencia Origen", required=True
    )
    destination_dependence_id = fields.Many2one(
        "tmc.dependence", string="Dependencia Destino", required=True
    )
    # notes = fields.Text(string="Observaciones")
    user_id = fields.Many2one(
        "res.users", string="Usuario", default=lambda self: self.env.user
    )

    @api.constrains('date')
    def _check_date_not_future(self):
        for record in self:
            if record.date and record.date > fields.Datetime.now():
                raise exceptions.ValidationError(
                    _("La fecha del movimiento no puede ser una fecha futura.")
                )

    @api.constrains('date', 'expediente_id')
    def _check_date_not_before_intake(self):
        for record in self:
            if (
                record.date
                and record.expediente_id
                and record.expediente_id.intake_date
                and record.date.date() < record.expediente_id.intake_date
            ):
                raise exceptions.ValidationError(
                    _("La fecha del movimiento no puede ser anterior "
                      "a la fecha de ingreso del expediente (%(intake)s).",
                      intake=record.expediente_id.intake_date)
                )