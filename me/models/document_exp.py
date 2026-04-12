from odoo import _, api, exceptions, fields, models


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
    
    # Campo para filtrar dependencias permitidas
    allowed_dependence_ids = fields.Many2many(
        'tmc.dependence',
        compute='_compute_allowed_dependencies',
        string='Dependencias Permitidas'
    )

    # Campos específicos del expediente
    external_key = fields.Char(
        string="Clave Externa",
        help="lo usa la Muni para identificar los expedientes"
    )
    jurisdiction_dependence = fields.Many2one(
        'tmc.dependence',
        string="Jurisdicción",
        required=True,
        help="Dependencia de jurisdicción del expediente"
    )
    source_dependence_id = fields.Many2one(
        'tmc.dependence',
        string="Repartición",
        help="Repartición específica dentro de la jurisdicción que origina el expediente",
    )
    allowed_sub_dependence_ids = fields.Many2many(
        'tmc.dependence',
        compute='_compute_allowed_sub_dependences',
        string='Reparticiones Permitidas',
    )
    fojas = fields.Integer(
        string="Número de fojas",
        help="Número de fojas del expediente"
    )
    # asunto = fields.Char(
    #     string="Asunto",
    #     help="Asunto específico del expediente"
    # )

    # NO re-declarar number aquí. Re-declararlo rompe el mecanismo _inherits:
    # el campo deja de ser proxy y Odoo no lo pasa a tmc.document en create(),
    # dejando tmc.document.number = 0 y generando name = "Unnamed Document".
    # El required se define en la vista (required="1" en el campo).
    # number = fields.Integer(required=True)

    intake_date = fields.Date(
        string="Fecha de Ingreso",
        required=True,
        help="Fecha en que el expediente fue recibido físicamente en Mesa de Entradas",
    )

    is_valid = fields.Boolean(
        compute="_compute_is_valid",
        string="Expediente Válido",
        help="Indica si el expediente tiene todos los campos básicos completos"
    )

    is_origin_complete = fields.Boolean(
        compute="_compute_is_origin_complete",
        string="Origen Completo",
    )

    computed_name = fields.Char(
        compute="_compute_name",
        string="Nombre del Expediente",
        help="Nombre del expediente generado en tiempo real"
    )

    document_movement_ids = fields.One2many(
        "me.document_movement", "expediente_id", string="Movimientos"
    )

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
        for record in self:
            allowed_deps = self.env['tmc.dependence'].search([
                ('abbreviation', 'in', ['DEM', 'TMC', 'CM'])
            ])
            record.allowed_dependence_ids = allowed_deps

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

    @api.constrains('intake_date')
    def _check_intake_date_not_future(self):
        for record in self:
            if record.intake_date and record.intake_date > fields.Date.today():
                raise exceptions.ValidationError(
                    _("La fecha de ingreso no puede ser una fecha futura.")
                )

    @api.depends('dependence_id', 'number', 'period')
    def _compute_is_origin_complete(self):
        for record in self:
            record.is_origin_complete = bool(
                record.dependence_id and record.number and record.period
            )

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
                record.computed_name = "Documento sin nombre"

    @api.onchange('jurisdiction_dependence')
    def _onchange_jurisdiction_dependence(self):
        """Limpiar repartición al cambiar jurisdicción para evitar datos inconsistentes"""
        self.source_dependence_id = False

    @api.onchange('dependence_id')
    def _onchange_dependence(self):
        """Configurar el tipo de documento cuando se selecciona dependencia"""
        self.document_type_id = False
        if self.dependence_id:
            # Buscar el tipo de documento "Expediente"
            exp_type = self.env['tmc.document_type'].search([
                ('abbreviation', '=', 'EXP')
            ], limit=1)
            if exp_type:
                self.document_type_id = exp_type
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
                        'title': 'Expediente existente',
                        'message': 'Ya existe un expediente con estos datos. Verifique la información.'
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        # _inherits maneja la creación de tmc.document automáticamente.
        # No crear tmc.document manualmente — rompe el mecanismo de delegación.
        records = super().create(vals_list)
        tmc_dependence = self.env['tmc.dependence'].search([('abbreviation', '=', 'TMC')], limit=1)
        mesa_entrada_dependence = self.env['tmc.dependence'].search([('abbreviation', '=', 'ME')], limit=1)
        for record in records:
            # Crear registro en RAA (acoplamiento implícito — raa no está en __manifest__.py)
            self.env["raa.registry_aa"].create({
                "document_id": record.document_id.id,
            })
            # Crear el primer movimiento automáticamente: jurisdicción → TMC
            if record.jurisdiction_dependence and tmc_dependence:
                self.env['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': record.jurisdiction_dependence.id,
                    'destination_dependence_id': tmc_dependence.id,
                    'user_id': self.env.uid,
                })
            # Crear el segundo movimiento automáticamente: TMC → Mesa de Entradas
            if tmc_dependence and mesa_entrada_dependence:
                self.env['me.document_movement'].create({
                    'expediente_id': record.id,
                    'date': fields.Datetime.now(),
                    'origin_dependence_id': tmc_dependence.id,
                    'destination_dependence_id': mesa_entrada_dependence.id,
                    'user_id': self.env.uid,
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
