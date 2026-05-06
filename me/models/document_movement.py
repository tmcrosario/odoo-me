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
    destination_abbreviation = fields.Char(
        compute="_compute_destination_abbreviation",
        string="Destination Abbreviation",
    )
    legajo_number = fields.Char(string="File Number")

    @api.onchange('destination_dependence_id')
    def _onchange_destination_dependence_id(self):
        dest = self.destination_dependence_id
        if not dest or not dest.is_internal:
            self.user_id = False
        elif dest.default_responsible_id:
            self.user_id = dest.default_responsible_id

    @api.depends('destination_dependence_id')
    def _compute_destination_abbreviation(self):
        for record in self:
            record.destination_abbreviation = (
                record.destination_dependence_id.abbreviation or ''
            )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        # La vista pasa {'default_expediente_id': id}. super() lo resuelve en
        # defaults['expediente_id'] solo si 'expediente_id' está en fields_list.
        # El form popup de un One2many no incluye expediente_id en fields_list,
        # por lo que se lee directamente del contexto como fallback.
        expediente_id = defaults.get('expediente_id') or self._context.get('default_expediente_id')
        if expediente_id:
            need_fojas = 'fojas' in fields_list
            need_origin = 'origin_dependence_id' in fields_list
            if need_fojas or need_origin:
                last_movement = self.search(
                    [('expediente_id', '=', expediente_id)],
                    order='id desc',
                    limit=1,
                )
                if need_fojas:
                    # Pre-load fojas from the last movement snapshot, not from
                    # expediente.fojas (which reflects only the creation value).
                    defaults['fojas'] = last_movement.fojas if last_movement else 0
                if need_origin and last_movement and last_movement.destination_dependence_id:
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

    @api.constrains('destination_dependence_id', 'legajo_number')
    def _check_legajo_number_required(self):
        for record in self:
            if (
                record.destination_dependence_id
                and record.destination_dependence_id.abbreviation == 'LEG'
                and not record.legajo_number
            ):
                raise exceptions.ValidationError(
                    _("File number is required when the destination is 'Adjunto a Legajo'.")
                )

    _OPERATOR_EDITABLE_FIELDS = frozenset({'fojas', 'user_id', 'legajo_number'})

    def _is_last_manual_movement(self):
        """True if self is the last non-automatic movement of its expediente."""
        self.ensure_one()
        if self.is_automatic:
            return False
        last = self.search(
            [('expediente_id', '=', self.expediente_id.id), ('is_automatic', '=', False)],
            order='id desc',
            limit=1,
        )
        return last.id == self.id

    def write(self, vals):
        if (
            not self.env.context.get('me_create_in_progress')
            and not self.env.user.has_group('me.group_manager')
        ):
            written_fields = set(vals.keys())
            for record in self:
                if not record._is_last_manual_movement():
                    raise exceptions.AccessError(
                        _("Existing movements can only be modified by an Intake Register manager.")
                    )
                if record.user_id.id != self.env.user.id:
                    raise exceptions.AccessError(
                        _("Only the current holder of the expediente can correct a movement.")
                    )
                if not written_fields <= self._OPERATOR_EDITABLE_FIELDS:
                    raise exceptions.AccessError(
                        _("Existing movements can only be modified by an Intake Register manager.")
                    )
                if 'legajo_number' in written_fields and record.destination_abbreviation != 'LEG':
                    raise exceptions.AccessError(
                        _("File number can only be set on movements with destination 'Adjunto a Legajo'.")
                    )
        return super().write(vals)