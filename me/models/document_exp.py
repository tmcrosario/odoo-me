from odoo import _, api, exceptions, fields, models


class DocumentExp(models.Model):
    _name = "me.document_exp"
    _inherits = {"tmc.document": "document_id"}
    _description = "Expediente Registry"

    document_id = fields.Many2one(
        "tmc.document",
        required=True,
        ondelete="cascade",
        string="Document",
    )

    # Field for filtering jurisdiction (first-level nodes 1.XX.00 in the nomenclator)
    allowed_jurisdiction_ids = fields.Many2many(
        'tmc.dependence',
        compute='_compute_allowed_jurisdictions',
        string='Allowed Jurisdictions',
    )

    # Expediente-specific fields
    external_key = fields.Char(
        string="External Key",
        help="Used by the municipality to identify expedientes"
    )
    jurisdiction_dependence = fields.Many2one(
        'tmc.dependence',
        string="Jurisdiction",
        help=(
            "Jurisdiction dependence for this expediente. For DEM origin it is left "
            "empty at intake and written later by JUNCO via "
            "action_set_origin_from_junco() (EPIC-004). TMC/CM auto-assign it in create()."
        ),
    )
    source_dependence_id = fields.Many2one(
        'tmc.dependence',
        string="Source Dependence",
        help="Specific dependence within the jurisdiction that originated the expediente",
    )
    allowed_sub_dependence_ids = fields.Many2many(
        'tmc.dependence',
        compute='_compute_allowed_sub_dependences',
        string='Allowed Source Dependences',
    )
    fojas = fields.Integer(
        string="Page Count",
        default=0,
        help="Number of pages in the expediente"
    )
    # asunto = fields.Char(
    #     string="Asunto",
    #     help="Asunto específico del expediente"
    # )

    # Temas raíz permitidos para expedientes (EXP) en este módulo.
    # Se resuelven por XML ID para no depender de nombres ni de dependence_id.
    _EXP_ROOT_TOPIC_XMLIDS = (
        'tmc_data.tmc_document_topic_licitacion',
        'tmc_data.tmc_document_topic_nota',
    )

    allowed_exp_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        compute='_compute_allowed_exp_topic_ids',
        string='Allowed EXP Topics',
    )

    # Proxy Many2one fields for subject selection (topic + subtopic).
    # Wrap main_topic_ids and secondary_topic_ids from tmc.document (Many2many)
    # to provide single-value selection in the UI without modifying the base model.
    main_topic_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        string='Subject',
        compute='_compute_main_topic_id',
        inverse='_set_main_topic_id',
        domain="[('parent_id', '=', False), ('id', 'in', allowed_exp_topic_ids)]",
    )
    secondary_topic_id = fields.Many2one(
        comodel_name='tmc.document_topic',
        string='Specification',
        compute='_compute_secondary_topic_id',
        inverse='_set_secondary_topic_id',
        domain="[('parent_id', '=', main_topic_id)]",
    )

    # NO re-declarar number aquí. Re-declararlo rompe el mecanismo _inherits:
    # el campo deja de ser proxy y Odoo no lo pasa a tmc.document en create(),
    # dejando tmc.document.number = 0 y generando name = "Unnamed Document".
    # El required se define en la vista (required="1" en el campo).
    # number = fields.Integer(required=True)

    intake_date = fields.Date(
        string="Intake Date",
        required=True,
        help="Date when the expediente was physically received at the Intake Register",
    )

    is_valid = fields.Boolean(
        compute="_compute_is_valid",
        string="Valid Expediente",
        help="Indicates whether the expediente has all basic fields filled"
    )

    is_origin_complete = fields.Boolean(
        compute="_compute_is_origin_complete",
        string="Complete Origin",
    )

    dependence_abbreviation = fields.Char(
        compute="_compute_dependence_abbreviation",
        string="Origin Abbreviation",
    )

    computed_name = fields.Char(
        compute="_compute_name",
        string="Expediente Name",
        help="Expediente name computed in real time"
    )

    document_movement_ids = fields.One2many(
        "me.document_movement", "expediente_id", string="Movements"
    )

    has_reentry = fields.Boolean(
        string="Has Reentry",
        compute="_compute_has_reentry",
        store=True,
        help=(
            "True when the expediente has left the Tribunal at least once "
            "(movement to an external dependence) and then returned "
            "(subsequent movement to an internal dependence)."
        ),
    )

    is_currently_internal = fields.Boolean(
        string="Currently at Tribunal",
        compute="_compute_is_currently_internal",
        store=True,
        help=(
            "True when the last registered movement of the expediente has a "
            "destination that belongs to the Tribunal (is_internal=True)."
        ),
    )

    is_licitacion = fields.Boolean(
        string="Licitación",
        compute="_compute_is_licitacion",
        store=True,
        help="True when the expediente's main topic is Licitación.",
    )

    current_holder_id = fields.Many2one(
        comodel_name='res.users',
        string="Current Holder",
        compute="_compute_current_holder_id",
        store=True,
        help=(
            "The user designated as responsible in the last registered movement "
            "(movement with the highest id). False when no movements exist."
        ),
    )

    @api.depends('document_movement_ids.user_id')
    def _compute_current_holder_id(self):
        for record in self:
            last = record.document_movement_ids.sorted('id')[-1:]
            record.current_holder_id = last.user_id if last else False

    current_location_dependence_id = fields.Many2one(
        comodel_name='tmc.dependence',
        string="Destination Office",
        compute="_compute_current_location_dependence_id",
        store=True,
        help=(
            "Current internal location office: destination dependence of the last "
            "registered movement, only when that destination is internal "
            "(is_internal=True). False when there are no movements or the expediente "
            "has left the Tribunal (last movement to a non-internal dependence)."
        ),
    )

    @api.depends(
        'document_movement_ids.destination_dependence_id',
        'document_movement_ids.destination_dependence_id.is_internal',
    )
    def _compute_current_location_dependence_id(self):
        for record in self:
            last = record.document_movement_ids.sorted('id')[-1:]
            dest = last.destination_dependence_id if last else False
            # Solo ubicación interna: si el expediente ya salió del Tribunal (último
            # destino no interno), no interesa dónde fue → queda vacío.
            record.current_location_dependence_id = (
                dest if (dest and dest.is_internal) else False
            )

    @api.depends('document_movement_ids.destination_dependence_id.is_internal')
    def _compute_is_currently_internal(self):
        for record in self:
            last = record.document_movement_ids.sorted('id')[-1:]
            record.is_currently_internal = bool(
                last and last.destination_dependence_id.is_internal
            )

    @api.depends('main_topic_ids')
    def _compute_is_licitacion(self):
        licitacion = self.env.ref(
            'tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False
        )
        for record in self:
            record.is_licitacion = bool(licitacion and licitacion in record.main_topic_ids)

    @api.depends('document_movement_ids.destination_dependence_id.is_internal')
    def _compute_has_reentry(self):
        for record in self:
            saw_exit = False
            reentry = False
            for movement in record.document_movement_ids.sorted('id'):
                dest = movement.destination_dependence_id
                if not dest:
                    continue
                if not dest.is_internal:
                    saw_exit = True
                elif saw_exit:
                    reentry = True
                    break
            record.has_reentry = reentry

    @api.depends()
    def _compute_allowed_exp_topic_ids(self):
        topics = self.env['tmc.document_topic']
        for xmlid in self._EXP_ROOT_TOPIC_XMLIDS:
            topic = self.env.ref(xmlid, raise_if_not_found=False)
            if topic:
                topics |= topic
        for record in self:
            record.allowed_exp_topic_ids = topics

    @api.depends('main_topic_ids')
    def _compute_main_topic_id(self):
        for record in self:
            record.main_topic_id = record.main_topic_ids[:1]

    def _set_main_topic_id(self):
        for record in self:
            # Write directly to the tmc.document parent via sudo. Assigning
            # record.main_topic_ids = [...] would route through the ORM's
            # _inverse_related, which calls tmc.document.write() with the
            # current user — failing for operators (perm_write=0 on tmc.document).
            # The ME write() guard is the security boundary: operators only reach
            # this inverse after the guard has passed.
            record.document_id.sudo().write({
                'main_topic_ids': [(6, 0, [record.main_topic_id.id])] if record.main_topic_id else [(6, 0, [])]
            })

    @api.depends('secondary_topic_ids')
    def _compute_secondary_topic_id(self):
        for record in self:
            record.secondary_topic_id = record.secondary_topic_ids[:1]

    def _set_secondary_topic_id(self):
        for record in self:
            record.document_id.sudo().write({
                'secondary_topic_ids': [(6, 0, [record.secondary_topic_id.id])] if record.secondary_topic_id else [(6, 0, [])]
            })

    @api.onchange('main_topic_id')
    def _onchange_main_topic_id(self):
        self.secondary_topic_id = False

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'document_type_id' not in defaults or not defaults.get('document_type_id'):
            exp_type = self.env['tmc.document_type'].search(
                [('abbreviation', '=', 'EXP')], limit=1
            )
            if exp_type:
                defaults['document_type_id'] = exp_type.id
        return defaults

    @api.depends()
    def _compute_allowed_jurisdictions(self):
        adm = self.env.ref('tmc_data.tmc_dependence_adm', raise_if_not_found=False)
        if adm:
            orders = self.env['tmc.dependence_order'].search([('parent_id', '=', adm.id)])
            jurisdictions = orders.mapped('dependence_id')
        else:
            jurisdictions = self.env['tmc.dependence'].browse()
        for record in self:
            record.allowed_jurisdiction_ids = jurisdictions

    @api.depends('jurisdiction_dependence')
    def _compute_allowed_sub_dependences(self):
        """Computar las reparticiones hijas de la jurisdicción seleccionada"""
        for record in self:
            if record.jurisdiction_dependence:
                sub_orders = self.env['tmc.dependence_order'].search([
                    ('parent_id', '=', record.jurisdiction_dependence.id)
                ])
                record.allowed_sub_dependence_ids = sub_orders.mapped('dependence_id')
            else:
                record.allowed_sub_dependence_ids = self.env['tmc.dependence'].browse()

    _ALLOWED_DEPENDENCE_ABBREVIATIONS = frozenset({'DEM', 'TMC', 'CM'})

    def _validate_number(self, number):
        """Raise ValidationError if number is outside the valid range 1–999999."""
        if not (1 <= number <= 999999):
            raise exceptions.ValidationError(
                _("Expediente number must be between 1 and 999,999 (6 digits maximum).")
            )

    def _validate_dependence(self, dependence_id_val):
        """Valida que la dependencia de origen sea DEM, TMC o CM."""
        if not dependence_id_val:
            return
        dep = self.env['tmc.dependence'].browse(dependence_id_val)
        if dep.abbreviation not in self._ALLOWED_DEPENDENCE_ABBREVIATIONS:
            raise exceptions.ValidationError(_(
                "The origin dependence '%(dep)s' is not allowed. "
                "Only DEM, TMC and CM are accepted.",
                dep=dep.abbreviation,
            ))

    @api.constrains('intake_date')
    def _check_intake_date_not_future(self):
        for record in self:
            if record.intake_date and record.intake_date > fields.Date.today():
                raise exceptions.ValidationError(
                    _("Intake date cannot be in the future.")
                )

    @api.depends('dependence_id', 'number', 'period')
    def _compute_is_origin_complete(self):
        for record in self:
            record.is_origin_complete = bool(
                record.dependence_id and record.number and record.period
            )

    @api.depends('dependence_id')
    def _compute_dependence_abbreviation(self):
        for record in self:
            record.dependence_abbreviation = record.dependence_id.abbreviation or ''

    @api.depends('dependence_id', 'document_type_id', 'number', 'period', 'jurisdiction_dependence')
    def _compute_is_valid(self):
        """Computar si el expediente tiene todos los campos básicos completos"""
        for record in self:
            record.is_valid = bool(
                record.dependence_id and 
                record.document_type_id and 
                record.number and 
                record.period and
                record.jurisdiction_dependence
            )

    @api.depends('dependence_id', 'number', 'period')
    def _compute_name(self):
        """Computar el nombre del expediente en tiempo real"""
        for record in self:
            if record.dependence_id and record.number and record.period:
                dep_abbr = record.dependence_id.abbreviation
                record.computed_name = f"EXP-{str(record.number).zfill(6)}-{dep_abbr}/{record.period}"
            else:
                record.computed_name = "Unnamed Document"

    @api.onchange('jurisdiction_dependence')
    def _onchange_jurisdiction_dependence(self):
        """Limpiar repartición al cambiar jurisdicción para evitar datos inconsistentes"""
        self.source_dependence_id = False

    @api.constrains('source_dependence_id', 'jurisdiction_dependence')
    def _check_source_dependence_required(self):
        for record in self:
            if (record.allowed_sub_dependence_ids
                    and not record.source_dependence_id
                    and record.dependence_id.abbreviation not in ('CM', 'TMC')):
                raise exceptions.ValidationError(
                    _("The source dependence is required "
                      "when the selected jurisdiction has sub-dependences available.")
                )

    def action_set_origin_from_junco(self, jurisdiction_id, source_id=False):
        """Single controlled entry point for JUNCO to write the origin of a DEM
        expediente (EPIC-004 / D-4).

        JUNCO calls this instead of writing directly because write() rejects any
        non-manager write that is not a movement. Scope (DEM only) and values (against
        the nomenclador in tmc.dependence_order) are validated here, BEFORE elevating,
        so the security boundary stays in ME. Only jurisdiction_dependence and
        source_dependence_id are written. Idempotent: re-calling with the same values
        is a safe no-op write (used from JUNCO's inverse, which may run on every save).
        """
        self.ensure_one()
        if self.dependence_id.abbreviation != 'DEM':
            raise exceptions.UserError(_(
                "The origin can only be set from JUNCO on DEM expedientes "
                "(this expediente's origin is %s).",
                self.dependence_id.abbreviation or _("undefined"),
            ))
        jurisdiction = self.env['tmc.dependence'].browse(jurisdiction_id)
        if jurisdiction not in self.allowed_jurisdiction_ids:
            raise exceptions.UserError(_(
                "Invalid jurisdiction: it is not a valid DEM jurisdiction in the "
                "nomenclador."
            ))
        # Sub-dependences valid for the jurisdiction being set (mirror of
        # _compute_allowed_sub_dependences, computed for that jurisdiction).
        valid_sources = self.env['tmc.dependence_order'].search(
            [('parent_id', '=', jurisdiction.id)]
        ).mapped('dependence_id')
        if valid_sources:
            if not source_id:
                raise exceptions.UserError(_(
                    "A source dependence is required: the selected jurisdiction has "
                    "sub-dependences."
                ))
            if self.env['tmc.dependence'].browse(source_id) not in valid_sources:
                raise exceptions.UserError(_(
                    "Invalid source dependence: it is not a sub-dependence of the "
                    "selected jurisdiction."
                ))
        elif source_id:
            raise exceptions.UserError(_(
                "The selected jurisdiction has no sub-dependences; a source dependence "
                "must not be provided."
            ))
        # Boundary validated above. sudo() grants ORM write permission; the
        # me_origin_from_junco context flag passes the write() guard, restricted there
        # to exactly these two fields.
        self.with_context(me_origin_from_junco=True).sudo().write({
            'jurisdiction_dependence': jurisdiction.id,
            'source_dependence_id': source_id or False,
        })
        return True

    @api.onchange('dependence_id')
    def _onchange_dependence(self):
        """Set document_type_id and auto-assign jurisdiction for TMC/CM."""
        self.document_type_id = False
        if self.dependence_id:
            exp_type = self.env['tmc.document_type'].search([
                ('abbreviation', '=', 'EXP')
            ], limit=1)
            if exp_type:
                self.document_type_id = exp_type
            abbr = self.dependence_id.abbreviation
            if abbr == 'TMC':
                self.jurisdiction_dependence = self.dependence_id
            elif abbr == 'CM':
                self.jurisdiction_dependence = self.dependence_id
                self.source_dependence_id = False
            else:
                self.jurisdiction_dependence = False
        else:
            self.jurisdiction_dependence = False
        return {
            'domain': {
                'document_type_id': [('abbreviation', '=', 'EXP')]
            }
        }

    @api.onchange('number')
    def _onchange_number(self):
        if self.number and not (1 <= self.number <= 999999):
            return {
                'warning': {
                    'title': _('Invalid Number'),
                    'message': _("Expediente number must be between 1 and 999,999 (6 digits maximum)."),
                }
            }

    @api.onchange('dependence_id', 'document_type_id', 'period', 'number', 'jurisdiction_dependence')
    def _onchange_document_data(self):
        """Validar que el expediente no exista cuando se completan los campos básicos"""
        if self.dependence_id and self.document_type_id and self.number and self.period and self.jurisdiction_dependence:
            # Verificar si ya existe un documento con estos datos
            existing_doc = self.env["tmc.document"].search([
                ("dependence_id", "=", self.dependence_id.id),
                ("document_type_id", "=", self.document_type_id.id),
                ("number", "=", self.number),
                ("period", "=", self.period)
            ])
            if existing_doc:
                return {
                    'warning': {
                        'title': _('Existing Expediente'),
                        'message': _('An expediente with this data already exists. Please verify the information.')
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        # Validate and extract date before calling super().
        # tmc.document.create() expects date as a string and runs a period-match
        # check; passing a datetime.date object or mismatched year raises UserError.
        # We bypass it entirely by removing date from vals and applying it via SQL
        # after creation — same pattern as write() / _update_document_date().
        dates = []
        for vals in vals_list:
            if not vals.get('date'):
                raise exceptions.ValidationError(
                    _("The document date is required.")
                )
            dates.append(vals.pop('date'))
            if 'number' in vals:
                self._validate_number(vals['number'])
            if 'dependence_id' in vals:
                self._validate_dependence(vals['dependence_id'])
            # Auto-assign jurisdiction_dependence for TMC and CM when not provided.
            # The form onchange handles the UI case; this backup covers API calls.
            if not vals.get('jurisdiction_dependence'):
                dep_id = vals.get('dependence_id')
                if dep_id:
                    dep = self.env['tmc.dependence'].browse(dep_id)
                    if dep.abbreviation in ('TMC', 'CM'):
                        vals['jurisdiction_dependence'] = dep.id

        # Call the parent create() with me_create_in_progress in the context so
        # any write() within the ORM chain (e.g. _inherits field sync, stored
        # computed-field flush) passes the non-manager guard in write().
        # The flag is scoped only to this super() call; we strip it from the
        # returned records so callers do NOT inherit it (which would silently
        # bypass the guard on all subsequent operations on the returned objects).
        # _inherits maneja la creación de tmc.document automáticamente.
        # No crear tmc.document manualmente — rompe el mecanismo de delegación.
        records = super(
            DocumentExp, self.with_context(me_create_in_progress=True)
        ).create(vals_list)

        # env_create retains me_create_in_progress=True so write() calls
        # triggered by movement creation (e.g. has_reentry recompute) also pass.
        env_create = records.env
        for record, date_val in zip(records, dates):
            record._update_document_date(date_val)
        tmc_dependence = env_create['tmc.dependence'].search([('abbreviation', '=', 'TMC')], limit=1)
        mesa_entrada_dependence = env_create['tmc.dependence'].search([('abbreviation', '=', 'ME')], limit=1)
        for record in records:
            # Crear registro en RAA (acoplamiento implícito — raa no está en __manifest__.py).
            # sudo() necesario: la creación RAA es un efecto interno del sistema;
            # el usuario no necesita permisos en raa.registry_aa para crear expedientes.
            env_create["raa.registry_aa"].sudo().create({
                "document_id": record.document_id.id,
            })
            # Movimientos automáticos de ingreso.
            # Si el expediente proviene de TMC, el origen ya es TMC, por lo que el
            # movimiento origen→TMC sería TMC→TMC (sin sentido): se genera solo TMC→ME.
            # El 1er movimiento usa la dependencia de origen (dependence_id), NO la
            # jurisdicción (EPIC-004, opción A): así el 1er pase DEM→TMC se crea al
            # ingresar aunque la jurisdicción quede vacía (la completa JUNCO después).
            origin_is_tmc = (
                tmc_dependence and
                record.dependence_id == tmc_dependence
            )
            if not origin_is_tmc and tmc_dependence:
                # Movimiento 1 (DEM/CM): dependencia de origen → TMC
                env_create['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': record.dependence_id.id,
                    'destination_dependence_id': tmc_dependence.id,
                    'user_id': self.env.uid,
                    'fojas': record.fojas,
                    'is_automatic': True,
                })
            # Movimiento final: TMC → Mesa de Entradas (siempre, si existen ambas dependencias)
            if tmc_dependence and mesa_entrada_dependence:
                env_create['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': tmc_dependence.id,
                    'destination_dependence_id': mesa_entrada_dependence.id,
                    'user_id': self.env.uid,
                    'fojas': record.fojas,
                    'is_automatic': True,
                })

        # Return records in the CALLER's environment (without me_create_in_progress)
        # so subsequent operations on the returned objects are correctly guarded.
        return records.with_env(self.env)

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
        self.document_id.invalidate_recordset(['date'])

    def write(self, vals):
        if 'number' in vals:
            self._validate_number(vals['number'])
        if (
            not self.env.context.get('me_create_in_progress')
            and not self.env.user.has_group('me.group_manager')
        ):
            # Controlled origin write from JUNCO (EPIC-004 / D-4). action_set_origin_from_junco()
            # validates scope (DEM) and values before reaching here; this branch only
            # confirms the write is restricted to the two origin fields, so the context
            # flag can never become a general bypass of the guard below.
            if self.env.context.get('me_origin_from_junco'):
                if not set(vals.keys()) <= {'jurisdiction_dependence', 'source_dependence_id'}:
                    raise exceptions.AccessError(_(
                        "The JUNCO origin write may only set the jurisdiction and source."
                    ))
                return super().write(vals)
            movement_cmds = vals.get('document_movement_ids', [])
            _editable = self.env['me.document_movement']._OPERATOR_EDITABLE_FIELDS
            is_only_create_cmds = (
                set(vals.keys()) == {'document_movement_ids'}
                and movement_cmds
                and all(cmd[0] == 0 for cmd in movement_cmds)
            )
            is_only_update_cmds = (
                set(vals.keys()) == {'document_movement_ids'}
                and movement_cmds
                and all(
                    isinstance(cmd, (list, tuple))
                    and len(cmd) >= 3
                    and cmd[0] == 1
                    and isinstance(cmd[2], dict)
                    and set(cmd[2].keys()) <= _editable
                    for cmd in movement_cmds
                )
            )
            if is_only_create_cmds:
                for record in self:
                    last_mov = self.env['me.document_movement'].search(
                        [('expediente_id', '=', record.id)],
                        order='id desc',
                        limit=1,
                    )
                    if last_mov and last_mov.user_id.id != self.env.user.id:
                        raise exceptions.AccessError(_(
                            "Only the current holder of the expediente can register a new movement."
                        ))
            elif is_only_update_cmds:
                pass  # me.document_movement.write() enforces poseedor and last-manual checks
            else:
                raise exceptions.AccessError(_(
                    "Existing expedientes can only be modified by an Intake Register manager."
                ))
        if 'dependence_id' in vals:
            self._validate_dependence(vals['dependence_id'])
        # Separar la fecha del resto de campos
        date_in_vals = 'date' in vals
        date_val = vals.pop('date', None) if date_in_vals else None
        if date_in_vals and not date_val:
            raise exceptions.ValidationError(
                _("The document date is required.")
            )
        
        doc_fields = [
            "dependence_id", "document_type_id", "number", "period", "document_object"
        ]
        # Pop delegated fields from vals so super().write() does not try a second
        # write to tmc.document without sudo (which would fail for operators).
        document_vals = {field: vals.pop(field) for field in doc_fields if field in vals}

        # sudo() scoped only to this call: the ME guard above is the security boundary.
        # tmc.document.user has perm_write=0, so operators can't reach this directly;
        # only managers and the create() chain (me_create_in_progress) pass the guard.
        if document_vals:
            self.document_id.sudo().write(document_vals)

        # Actualizar la fecha usando el método personalizado
        if date_val is not None:
            self._update_document_date(date_val)

        # Llamar al super().write() solo con campos propios de me_document_exp
        return super().write(vals)

    def unlink(self):
        for record in self:
            # Capturar document antes de cualquier eliminación.
            # raa.unlink() puede cascade-eliminar tmc.document y luego me.document_exp,
            # por lo que acceder a record.document_id después lanzaría MissingError.
            document = record.document_id
            # Eliminar raa.registry_aa antes de tmc.document para evitar
            # violación de la FK constraint (raa.document_id RESTRICT).
            raa = self.env['raa.registry_aa'].search(
                [('document_id', '=', document.id)]
            )
            raa.unlink()
            # raa.unlink() puede haber eliminado tmc.document (si estaba vacío);
            # solo eliminar manualmente si aún existe.
            if document.exists():
                document.unlink()
        return super().unlink()
