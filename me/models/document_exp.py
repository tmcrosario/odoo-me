from odoo import _, api, exceptions, fields, models


class DocumentExp(models.Model):
    _name = "me.document_exp"
    _inherits = {"tmc.document": "document_id"}
    _description = "Expediente Registry"
    # Lista ordenada por ingreso más reciente primero; `id desc` desempata (intake_date es
    # un Date, muchos comparten día). Es el _order del modelo → default de todas las vistas
    # de lista (el <list> de Odoo no lleva orden propio en el arch).
    _order = "intake_date desc, id desc"

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
        # contratación directa y concurso de precios (junco:EPIC-011) — el porqué
        # (derivación de process_type en JUNCO) en business_rules.md (Temas raíz).
        'tmc_data.tmc_document_topic_contratacion_directa',
        'tmc_data.tmc_document_topic_concurso_precios',
    )

    allowed_exp_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        compute='_compute_allowed_exp_topic_ids',
        string='Allowed EXP Topics',
    )

    # relation= explícito: sin él colisionaría la tabla auto-inferida con allowed_exp_topic_ids
    # (mismo par de modelos me.document_exp ↔ tmc.document_topic).
    allowed_secondary_topic_ids = fields.Many2many(
        comodel_name='tmc.document_topic',
        relation='me_exp_allowed_secondary_topic_rel',
        compute='_compute_allowed_secondary_topic_ids',
        string='Allowed Secondary Topics',
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
        domain="[('id', 'in', allowed_secondary_topic_ids)]",
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

    current_legajo_number = fields.Char(
        string="Legajo Number",
        compute="_compute_current_legajo_number",
        help=(
            "Legajo file number when the expediente is currently in a Legajo: the "
            "legajo_number of the LAST movement, only when that destination is 'Adjunto "
            "a Legajo' (LEG). Empty otherwise. Non-stored (display label)."
        ),
    )

    is_licitacion = fields.Boolean(
        string="Licitación",
        compute="_compute_is_licitacion",
        store=True,
        help="True when the expediente's main topic is Licitación.",
    )

    is_nota = fields.Boolean(
        string="Nota",
        compute="_compute_is_nota",
        store=True,
        help=(
            "True when the expediente's main topic is Nota. Notas never reach JUNCO "
            "(it only offers purchase topics), so for DEM origin ME loads the "
            "jurisdiction/source itself at intake instead of ceding them (EPIC-004/TASK-002)."
        ),
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

    @api.depends('document_movement_ids.destination_dependence_id',
                 'document_movement_ids.legajo_number')
    def _compute_current_legajo_number(self):
        for record in self:
            last = record.document_movement_ids.sorted('id')[-1:]
            dest = last.destination_dependence_id if last else False
            record.current_legajo_number = (
                last.legajo_number if (dest and dest.abbreviation == 'LEG') else False
            )

    # Depende del m2m del padre Y del proxy main_topic_id para reaccionar EN VIVO en el form
    # (antes de guardar), como is_nota: así el `required` del subtema en la vista se activa al
    # elegir el tema Licitación.
    @api.depends('main_topic_ids', 'main_topic_id')
    def _compute_is_licitacion(self):
        licitacion = self.env.ref(
            'tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False
        )
        for record in self:
            record.is_licitacion = bool(licitacion and (
                licitacion in record.main_topic_ids or record.main_topic_id == licitacion
            ))

    # Depends on BOTH the stored source of truth (main_topic_ids, on the parent) and the
    # form proxy (main_topic_id): the proxy only writes through to the parent on save, so
    # without it is_nota stays False while loading and the view never reveals the
    # jurisdiction fields for a Nota (the backend would then reject the save).
    @api.depends('main_topic_ids', 'main_topic_id')
    def _compute_is_nota(self):
        nota = self.env.ref(
            'tmc_data.tmc_document_topic_nota', raise_if_not_found=False
        )
        for record in self:
            record.is_nota = bool(nota and (
                nota in record.main_topic_ids or record.main_topic_id == nota
            ))

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

    # Depende de main_topic_id (el proxy del form) para reaccionar EN VIVO al elegir el tema,
    # antes de guardar (main_topic_ids recién se escribe al guardar).
    @api.depends('main_topic_id')
    def _compute_allowed_secondary_topic_ids(self):
        Topic = self.env['tmc.document_topic']
        licitacion = self.env.ref(
            'tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False
        )
        subtipos = Topic.browse()
        if licitacion:
            for xmlid in ('tmc_data.tmc_document_topic_licitacion_publica',
                          'tmc_data.tmc_document_topic_licitacion_privada'):
                t = self.env.ref(xmlid, raise_if_not_found=False)
                if t:
                    subtipos |= t
        for record in self:
            main = record.main_topic_id
            if licitacion and main == licitacion:
                # Licitación: acotar a los 2 subtipos reales (Privada/Pública), no los 23
                # subtemas documentales de GD que cuelgan del tema — ver business_rules
                # ("Subtema acotado al tema") / brainstorming IDEA 2.
                record.allowed_secondary_topic_ids = subtipos
            elif main:
                record.allowed_secondary_topic_ids = Topic.search(
                    [('parent_id', '=', main.id)]
                )
            else:
                record.allowed_secondary_topic_ids = Topic.browse()

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
        # EPIC-004/TASK-002: al cambiar el tema DESDE Nota mientras se carga, limpiar lo
        # tipeado — si no, queda un valor colgado detrás de un campo que para entonces ya
        # es readonly/invisible (y no se envía al guardar). Qué origen carga cada tema →
        # business_rules.md (excepción Nota).
        nota = self.env.ref(
            'tmc_data.tmc_document_topic_nota', raise_if_not_found=False
        )
        if (self.dependence_id.abbreviation == 'DEM'
                and (not nota or self.main_topic_id != nota)):
            self.jurisdiction_dependence = False
            self.source_dependence_id = False

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

    def _validate_intake_not_before_document_date(self, doc_date=None):
        """El ingreso a Mesa no puede ser anterior a la fecha del documento: no puede
        entrar antes de existir.

        Se valida por DOS caminos a propósito: este método lo llama la constrains de
        `intake_date` (cuando cambia el ingreso) y `_update_document_date` (cuando cambia
        la fecha del documento). Una constrains sobre `date` NO alcanzaría: esa fecha se
        escribe con SQL directo y el ORM nunca dispara sus validaciones."""
        for record in self:
            doc = doc_date if doc_date is not None else record.date
            if record.intake_date and doc and record.intake_date < doc:
                raise exceptions.ValidationError(
                    _("The intake date (%(intake)s) cannot be earlier than the document "
                      "date (%(doc)s): the expediente cannot be received before it exists.",
                      intake=record.intake_date, doc=doc)
                )

    @api.constrains('intake_date')
    def _check_intake_date_not_before_document_date(self):
        self._validate_intake_not_before_document_date()

    @api.constrains('intake_date', 'period')
    def _check_intake_date_not_before_period(self):
        """El ingreso no puede ser anterior al período del expediente: el expediente no
        pudo entrar antes de existir su período.

        Asimétrico a propósito: un ingreso POSTERIOR al período sí es válido (un
        expediente del período anterior puede llegar a Mesa después) — lo fija
        `test_intake_date_accepts_later_year_than_period`. Solo se bloquea el caso hacia
        atrás."""
        for record in self:
            if not record.intake_date or not record.period:
                continue
            try:
                period_year = int(record.period)
            except (TypeError, ValueError):
                continue  # período inválido: lo rechaza _check_period de tmc.document
            if record.intake_date.year < period_year:
                raise exceptions.ValidationError(
                    _("The intake date (%(intake)s) cannot be earlier than the "
                      "expediente period (%(period)s).",
                      intake=record.intake_date, period=record.period)
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

    def _validate_nota_jurisdiction(self):
        """DEM + Nota: ME loads the jurisdiction itself, so it is mandatory here
        (EPIC-004/TASK-002). Backend counterpart of the view's `required`: the UI does
        not replace backend validation. Other topics keep ceding it to JUNCO, so they
        are legitimately empty at intake and must NOT be checked."""
        for record in self:
            if (record.dependence_id.abbreviation == 'DEM'
                    and record.is_nota
                    and not record.jurisdiction_dependence):
                raise exceptions.ValidationError(
                    _("The jurisdiction is required for DEM expedientes with topic Nota; "
                      "it must be loaded at intake.")
                )

    def _validate_licitacion_subtopic(self):
        """Una Licitación no puede quedar sin subtema (EPIC-004/TASK-005, pedido de junco):
        JUNCO deriva el subtipo del proceso (public_tender/private_tender) del subtema
        (Pública/Privada) y no puede cerrar upstream el caso 'licitación sin subtema'.
        Concurso de precios y contratación directa NO llevan subtema → no se validan.

        Como _validate_nota_jurisdiction: se llama desde create()/write(), NO vía
        @api.constrains('is_licitacion') — al ser stored, recomputarlo dispararía la
        constraint sobre TODAS las licitaciones en cada -u y rompería el update sobre las
        viejas sin subtema (required solo para nuevas, decisión del usuario)."""
        for record in self:
            if record.is_licitacion and not record.secondary_topic_id:
                raise exceptions.ValidationError(
                    _("A licitación requires a subtype (Pública/Privada) as its "
                      "specification.")
                )

    # Deliberately NOT @api.constrains('is_nota'): is_nota is a stored computed field, and
    # recomputing a stored field runs the constraints that list it (orm/models.py,
    # _compute_field_value). On module update is_nota is recomputed for EVERY existing
    # record, so listing it would abort the update on pre-existing DEM Notas loaded before
    # this rule (they were legitimately empty under EPIC-004). New records are covered by
    # the explicit call in create() instead: on create the ORM only runs the constraints
    # whose fields are in vals, and the whole point here is that jurisdiction is missing.
    @api.constrains('jurisdiction_dependence')
    def _check_nota_jurisdiction_required(self):
        self._validate_nota_jurisdiction()

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
        # Defensa en profundidad (EPIC-004/TASK-002): lo que impide llegar acá desde JUNCO
        # es solo un domain de VISTA; una escritura por ORM/import/API lo sortearía y
        # pisaría el origen cargado en Mesa. La regla (JUNCO no toca Notas) y la
        # coordinación con junco → business_rules.md (excepción Nota) / task card.
        if self.is_nota:
            raise exceptions.UserError(_(
                "The origin cannot be set from JUNCO on an expediente with topic Nota: "
                "its jurisdiction and source are loaded in ME at intake."
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
            domain = [
                ("dependence_id", "=", self.dependence_id.id),
                ("document_type_id", "=", self.document_type_id.id),
                ("number", "=", self.number),
                ("period", "=", self.period),
            ]
            # Excluirse a sí mismo: en un expediente YA guardado este onchange se
            # encontraba a sí mismo y avisaba "ya existe" sobre el propio registro.
            # Antes no se notaba porque estos campos no eran editables después del alta.
            own_document = self._origin.document_id
            if own_document:
                domain.append(("id", "!=", own_document.id))
            existing_doc = self.env["tmc.document"].search(domain)
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
        #
        # EPIC-015 (opción 1): me.group_user ya NO tiene create/write sobre
        # tmc.document (GD) — solo lectura. Como el _inherits crea el tmc.document
        # padre DENTRO de este super().create(), se eleva con sudo() para que el
        # operativo pueda dar de alta expedientes sin ACL de escritura en GD (la
        # única escritura GD es esta creación del padre, elevada). No se crea el
        # padre a mano (rompería la delegación). Inmediatamente se des-eleva al
        # nivel su del llamador conservando me_create_in_progress, para que los
        # movimientos y demás corran con los permisos normales del usuario.
        # El super() elevado saltea el chequeo de ACL del propio me.document_exp
        # (ir.model.access.check corta por env.su), así que se valida explícitamente
        # contra los permisos REALES del llamador ANTES de elevar. self es el recordset
        # vacío del modelo y no está elevado → chequea el permiso a nivel modelo.
        self.check_access('create')
        records = super(
            DocumentExp, self.with_context(me_create_in_progress=True).sudo()
        ).create(vals_list)
        records = records.sudo(self.env.su)

        # EPIC-004/TASK-002/005: enforced here, not via @api.constrains on the stored
        # is_nota/is_licitacion — see _validate_nota_jurisdiction for why. Runs before the
        # movements/RAA below so a rejected expediente does not leave side effects behind.
        records._validate_nota_jurisdiction()
        records._validate_licitacion_subtopic()

        # env_create retains me_create_in_progress=True so write() calls
        # triggered by movement creation (e.g. has_reentry recompute) also pass.
        env_create = records.env
        for record, date_val in zip(records, dates):
            # sudo(): el seteo de fecha es parte de la creación del tmc.document padre, que
            # ya se eleva (EPIC-015: el operativo lee GD pero no la escribe). Sin esto, el
            # check_access('write') que ahora impone _update_document_date cortaría el alta
            # del operativo. El camino gobernado por ACL real es write() (managers, sin sudo).
            record.sudo()._update_document_date(date_val)
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
                # Movimiento 1 (DEM/CM): dependencia de origen → TMC.
                # EPIC-004/TASK-002 (IDEA 4): en una Nota, ME carga la jurisdicción al
                # ingreso (obligatoria, estable, JUNCO no la toca) → el 1er movimiento
                # refleja la secretaría REAL de origen, no el genérico dependence_id. Las
                # compras siguen con dependence_id: su jurisdicción está vacía al ingreso y
                # JUNCO la completa DESPUÉS, cuando este movimiento ya existe (por eso el
                # origen es un snapshot y no la seguiría). Defensivo: cae a dependence_id.
                origin_dependence = (
                    record.jurisdiction_dependence
                    if record.is_nota and record.jurisdiction_dependence
                    else record.dependence_id
                )
                env_create['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': origin_dependence.id,
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

        # tmc.document protege la fecha por DOS lados: el create() exige que el año
        # coincida con el período, y _check_date_not_future prohíbe fechas futuras. El SQL
        # de abajo elude el ORM para escapar del PRIMERO (regla de negocio: un documento
        # viejo puede archivarse en un expediente del período actual), pero de paso también
        # eludía el SEGUNDO, que nadie quiso desactivar: quedaban pasando fechas de
        # documento futuras. Se revalida acá, que es el único embudo de escritura de la
        # fecha (create() y write() pasan por este método; un @api.constrains NO serviría:
        # el UPDATE directo no dispara validaciones del ORM).
        new_date = fields.Date.to_date(date_str)
        if new_date > fields.Date.context_today(self):
            raise exceptions.ValidationError(
                _("The document date cannot be in the future.")
            )
        # Mismo embudo, misma razón: el SQL de abajo no dispara constrains, así que la
        # coherencia ingreso >= fecha del documento se valida acá contra el valor NUEVO.
        self._validate_intake_not_before_document_date(doc_date=new_date)

        # El UPDATE crudo de abajo saltea el ORM y, con él, ir.model.access y las record
        # rules de tmc.document: sin esto, cualquiera que llegue a este método escribe la
        # fecha aunque no tenga write sobre GD. Se re-impone el ACL a mano (misma API que
        # create(), ~L751) para que la escritura quede gobernada. El alta legítima corre
        # este método bajo sudo (el seteo de fecha es parte de la creación elevada del
        # padre, EPIC-015), así que ahí pasa; el camino gobernado de verdad es write()
        # (solo managers lo alcanzan, sin sudo → se les exige el write real sobre GD).
        self.document_id.check_access('write')

        # Actualizar directamente en la base de datos para evitar la validación
        self.env.cr.execute(
            "UPDATE tmc_document SET date = %s WHERE id = %s",
            (date_str, self.document_id.id)
        )
        # Invalidar el caché en AMBOS lados. `date` es un campo delegado (_inherits): el
        # expediente lo cachea aparte del documento padre, así que invalidar solo el padre
        # dejaba pegado el valor viejo (típicamente False, leído antes de este UPDATE) y
        # `expediente.date` devolvía False aunque la DB tuviera el valor correcto.
        self.document_id.invalidate_recordset(['date'])
        self.invalidate_recordset(['date'])

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
        res = super().write(vals)

        # EPIC-004/TASK-002: el tema puede cambiar DESPUÉS del alta (un expediente
        # guardado sin tema al que luego se le pone "Nota"). Sin esto quedaba is_nota=True
        # sin jurisdicción, un estado que ninguna validación cubría. Se valida solo si el
        # write toca el tema: hacerlo siempre rompería los expedientes anteriores a esta
        # regla (quedaron legítimamente vacíos) ante cualquier edición, p.ej. agregar un
        # movimiento. Tampoco sirve @api.constrains('is_nota'): al ser stored, recomputarlo
        # dispara la constraint sobre TODOS los registros en cada `-u me`.
        touched = set(vals)
        if {'main_topic_id', 'main_topic_ids'} & touched:
            self._validate_nota_jurisdiction()
        # EPIC-004/TASK-005: reclasificar a Licitación (o quitarle el subtema a una) tampoco
        # puede dejarla sin subtema. Se valida si el write toca el tema O el subtema; igual
        # que la Nota, no rompe las licitaciones viejas sin subtema salvo que se re-toquen.
        if {'main_topic_id', 'main_topic_ids',
                'secondary_topic_id', 'secondary_topic_ids'} & touched:
            self._validate_licitacion_subtopic()
        return res

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
