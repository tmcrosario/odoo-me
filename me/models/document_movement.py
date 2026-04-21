from odoo import _, api, exceptions, fields, models


class Movement(models.Model):
    _name = "me.document_movement"
    _description = "Expediente Movement"

    _unique_movement = models.Constraint(
        'UNIQUE(expediente_id, origin_dependence_id, destination_dependence_id, date)',
        'An identical movement already exists for this expediente '
        '(same origin, destination and exact date).',
    )

    expediente_id = fields.Many2one(
        "me.document_exp", string="Expediente", required=True, ondelete="cascade"
    )
    date = fields.Datetime(
        string="Date", default=fields.Datetime.now, required=True
    )
    origin_dependence_id = fields.Many2one(
        "tmc.dependence", string="Origin Dependence", required=True
    )
    destination_dependence_id = fields.Many2one(
        "tmc.dependence", string="Destination Dependence", required=True
    )
    fojas = fields.Integer(
        string="Page Count",
        default=0,
        help="Total page count of the expediente at the time of this movement (snapshot)",
    )
    is_automatic = fields.Boolean(
        default=False,
        help="True when the movement was automatically generated upon expediente creation",
    )
    # notes = fields.Text(string="Notes")
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        help="Odoo user responsible for the expediente at the destination of this movement",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        # La vista pasa {'default_expediente_id': id}. super() lo resuelve en
        # defaults['expediente_id'] solo si 'expediente_id' está en fields_list.
        # La lista inline de la UI no incluye expediente_id en fields_list, por lo
        # que se lee directamente del contexto como fallback.
        expediente_id = defaults.get('expediente_id') or self._context.get('default_expediente_id')
        if expediente_id:
            if 'fojas' in fields_list:
                expediente = self.env['me.document_exp'].browse(expediente_id)
                defaults['fojas'] = expediente.fojas
            if 'origin_dependence_id' in fields_list:
                last_movement = self.search(
                    [('expediente_id', '=', expediente_id)],
                    order='id desc',
                    limit=1,
                )
                if last_movement and last_movement.destination_dependence_id:
                    defaults['origin_dependence_id'] = (
                        last_movement.destination_dependence_id.id
                    )
        return defaults

    @api.constrains('date')
    def _check_date_not_future(self):
        for record in self:
            if record.date and record.date > fields.Datetime.now():
                raise exceptions.ValidationError(
                    _("Movement date cannot be in the future.")
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
                    _("Movement date cannot be earlier than "
                      "the expediente intake date (%(intake)s).",
                      intake=record.expediente_id.intake_date)
                )