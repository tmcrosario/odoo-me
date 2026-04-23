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

    # Field for filtering allowed dependences (origin: DEM, TMC, CM)
    allowed_dependence_ids = fields.Many2many(
        'tmc.dependence',
        compute='_compute_allowed_dependencies',
        string='Allowed Dependences'
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
        required=True,
        help="Jurisdiction dependence for this expediente"
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
            record.main_topic_ids = [(6, 0, [record.main_topic_id.id])] if record.main_topic_id else [(5, 0, 0)]

    @api.depends('secondary_topic_ids')
    def _compute_secondary_topic_id(self):
        for record in self:
            record.secondary_topic_id = record.secondary_topic_ids[:1]

    def _set_secondary_topic_id(self):
        for record in self:
            record.secondary_topic_ids = [(6, 0, [record.secondary_topic_id.id])] if record.secondary_topic_id else [(5, 0, 0)]

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
    def _compute_allowed_dependencies(self):
        """Computar las dependencias permitidas para expedientes"""
        allowed_deps = self.env['tmc.dependence'].search([
            ('abbreviation', 'in', ['DEM', 'TMC', 'CM'])
        ])
        for record in self:
            record.allowed_dependence_ids = allowed_deps

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
        # _inherits maneja la creación de tmc.document automáticamente.
        # No crear tmc.document manualmente — rompe el mecanismo de delegación.
        records = super().create(vals_list)
        for record, date_val in zip(records, dates):
            record._update_document_date(date_val)
        tmc_dependence = self.env['tmc.dependence'].search([('abbreviation', '=', 'TMC')], limit=1)
        mesa_entrada_dependence = self.env['tmc.dependence'].search([('abbreviation', '=', 'ME')], limit=1)
        for record in records:
            # Crear registro en RAA (acoplamiento implícito — raa no está en __manifest__.py).
            # sudo() necesario: la creación RAA es un efecto interno del sistema;
            # el usuario no necesita permisos en raa.registry_aa para crear expedientes.
            self.env["raa.registry_aa"].sudo().create({
                "document_id": record.document_id.id,
            })
            # Movimientos automáticos de ingreso.
            # Si el expediente proviene de TMC, jurisdiction_dependence == TMC,
            # por lo que el movimiento jurisdicción→TMC sería TMC→TMC (sin sentido).
            # En ese caso se genera únicamente el movimiento TMC→ME.
            origin_is_tmc = (
                tmc_dependence and
                record.dependence_id == tmc_dependence
            )
            if not origin_is_tmc and record.jurisdiction_dependence and tmc_dependence:
                # Movimiento 1 (solo para DEM/CM): jurisdicción → TMC
                self.env['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': record.jurisdiction_dependence.id,
                    'destination_dependence_id': tmc_dependence.id,
                    'user_id': self.env.uid,
                    'fojas': record.fojas,
                    'is_automatic': True,
                })
            # Movimiento final: TMC → Mesa de Entradas (siempre, si existen ambas dependencias)
            if tmc_dependence and mesa_entrada_dependence:
                self.env['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': tmc_dependence.id,
                    'destination_dependence_id': mesa_entrada_dependence.id,
                    'user_id': self.env.uid,
                    'fojas': record.fojas,
                    'is_automatic': True,
                })
        return records

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
        if 'fojas' in vals and not self.env.user.has_group('me.group_manager'):
            raise exceptions.ValidationError(_(
                "The page count of the expediente cannot be modified after creation. "
                "Variations must be recorded through movements. "
                "Only an Intake Register manager can correct this value."
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
