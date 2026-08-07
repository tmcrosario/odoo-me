from odoo import exceptions, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestNotaOrigin(TransactionCase):
    """EPIC-004/TASK-002 — DEM + tema Nota carga jurisdicción/origen en ME.

    EPIC-004 cedió esos campos a JUNCO para TODO expediente DEM, asumiendo que todo
    DEM va a un proceso de compras. Las Notas no llegan a JUNCO (solo ofrece temas de
    compra), así que ME las carga al ingreso. Estos tests fijan la matriz y protegen
    la no-regresión de EPIC-004 para los temas de compra."""

    def setUp(self):
        super().setUp()
        self.topic_nota = self.env.ref(
            'tmc_data.tmc_document_topic_nota', raise_if_not_found=False
        )
        self.topic_licitacion = self.env.ref(
            'tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False
        )
        self.publica = self.env.ref(
            'tmc_data.tmc_document_topic_licitacion_publica', raise_if_not_found=False
        )
        if not self.topic_nota or not self.topic_licitacion:
            self.skipTest("Temas de tmc_data no disponibles en esta DB")

        Dep = self.env['tmc.dependence']
        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        ) or self.env['tmc.document_type'].create({
            'name': 'Expediente Test', 'abbreviation': 'EXP',
        })
        self.dep_dem = Dep.search([('abbreviation', '=', 'DEM')], limit=1) or Dep.create(
            {'name': 'Dependencia DEM Test', 'abbreviation': 'DEM'})
        self.dep_tmc = Dep.search([('abbreviation', '=', 'TMC')], limit=1) or Dep.create(
            {'name': 'TMC', 'abbreviation': 'TMC'})
        self.dep_mesa = Dep.search([('abbreviation', '=', 'ME')], limit=1) or Dep.create(
            {'name': 'Mesa de Entradas', 'abbreviation': 'ME'})

        # Jurisdicción válida del nomenclador (colgada de adm) para que
        # action_set_origin_from_junco pueda validarla.
        adm = self.env.ref('tmc_data.tmc_dependence_adm', raise_if_not_found=False)
        if not adm:
            self.skipTest("tmc_data.tmc_dependence_adm no disponible en esta DB")
        self.jur = Dep.create({'name': 'Jur Nota Test', 'abbreviation': 'JURNT'})
        self.env['tmc.dependence_order'].create({
            'code': 'TEST-JURNT', 'dependence_id': self.jur.id, 'parent_id': adm.id,
        })

        self.base_vals = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'period': str(fields.Date.today().year),
            'intake_date': fields.Date.today(),
            'date': fields.Date.today(),
        }

    def _vals(self, number, topic=None, **extra):
        vals = dict(self.base_vals, number=number, **extra)
        if topic:
            vals['main_topic_ids'] = [(4, topic.id)]
            # Una licitación necesita subtema (EPIC-004/TASK-005); acá se usa solo como tema
            # de compra representativo (no probamos el subtema) → le damos uno válido para
            # que create() no la rechace.
            if topic == self.topic_licitacion and self.publica:
                vals['secondary_topic_ids'] = [(4, self.publica.id)]
        return vals

    # --- is_nota ---

    def test_is_nota_true_for_nota_topic(self):
        exp = self.env['me.document_exp'].create(
            self._vals(99801, self.topic_nota, jurisdiction_dependence=self.jur.id))
        self.assertTrue(exp.is_nota)
        self.assertFalse(exp.is_licitacion)

    def test_is_nota_reacts_to_form_proxy_before_save(self):
        """is_nota debe volverse True al elegir el tema EN EL FORM, antes de guardar.

        NO simplificar a un `create` con main_topic_ids: el bug real era justo este. El
        form edita `main_topic_id` (proxy), que recién escribe en el padre al guardar; si
        is_nota solo depende de `main_topic_ids`, queda False mientras se carga, la vista
        nunca muestra jurisdicción/repartición y al guardar el backend rechaza. Detectado
        en la verificación de UI del usuario."""
        record = self.env['me.document_exp'].new(self._vals(99811))
        self.assertFalse(record.is_nota)
        record.main_topic_id = self.topic_nota
        self.assertTrue(record.is_nota)

    def test_is_nota_false_for_purchase_topic(self):
        exp = self.env['me.document_exp'].create(
            self._vals(99802, self.topic_licitacion))
        self.assertFalse(exp.is_nota)

    # --- Carga en DEM + Nota ---

    def test_dem_nota_can_load_jurisdiction(self):
        """El caso que motiva la task: una Nota del DEM carga su jurisdicción en ME."""
        exp = self.env['me.document_exp'].create(
            self._vals(99803, self.topic_nota, jurisdiction_dependence=self.jur.id))
        self.assertEqual(exp.jurisdiction_dependence, self.jur)

    def test_dem_nota_without_jurisdiction_raises(self):
        """Backend: la jurisdicción es obligatoria en DEM + Nota (la UI no alcanza)."""
        with self.assertRaises(exceptions.ValidationError) as ctx:
            self.env['me.document_exp'].create(self._vals(99804, self.topic_nota))
        # Que falle por ESTA regla y no por otra validación cualquiera.
        self.assertIn('Nota', str(ctx.exception))

    # --- No-regresión de EPIC-004 (temas de compra) ---

    def test_dem_purchase_topic_still_allows_empty_origin(self):
        """EPIC-004 intacto: un DEM de compras se sigue creando sin jurisdicción
        (la completa JUNCO después). La nueva constrains NO debe alcanzarlo."""
        exp = self.env['me.document_exp'].create(
            self._vals(99805, self.topic_licitacion))
        self.assertFalse(exp.jurisdiction_dependence)

    def test_dem_without_topic_still_allows_empty_origin(self):
        """Un DEM sin tema tampoco se ve afectado por la constrains."""
        exp = self.env['me.document_exp'].create(self._vals(99806))
        self.assertFalse(exp.jurisdiction_dependence)

    def test_junco_can_still_set_origin_on_purchase_topic(self):
        """La guarda nueva no rompe el camino de EPIC-004 para temas de compra."""
        exp = self.env['me.document_exp'].create(
            self._vals(99807, self.topic_licitacion))
        exp.action_set_origin_from_junco(self.jur.id)
        self.assertEqual(exp.jurisdiction_dependence, self.jur)

    # --- Guarda defensiva: JUNCO no pisa una Nota ---

    def test_junco_cannot_set_origin_on_nota(self):
        """Defensa en profundidad: aunque JUNCO no puede llegar por UI (su domain de
        elegibilidad excluye 'nota'), una vía ORM/import no debe pisar lo que cargó
        Mesa. Verificamos que rechaza y que NO tocó el dato."""
        otra_jur = self.env['tmc.dependence'].create(
            {'name': 'Otra Jur Test', 'abbreviation': 'OJURT'})
        self.env['tmc.dependence_order'].create({
            'code': 'TEST-OJURT', 'dependence_id': otra_jur.id,
            'parent_id': self.env.ref('tmc_data.tmc_dependence_adm').id,
        })
        exp = self.env['me.document_exp'].create(
            self._vals(99808, self.topic_nota, jurisdiction_dependence=self.jur.id))
        with self.assertRaises(exceptions.UserError) as ctx:
            exp.action_set_origin_from_junco(otra_jur.id)
        self.assertIn('Nota', str(ctx.exception))
        # Lo cargado por Mesa quedó intacto (el punto de la guarda).
        self.assertEqual(exp.jurisdiction_dependence, self.jur)

    # --- El tema puede cambiar DESPUÉS del alta (reportado en verificación de UI) ---

    def test_setting_nota_topic_after_save_requires_jurisdiction(self):
        """Poner tema Nota a un expediente YA guardado sin jurisdicción debe bloquear.

        Caso real detectado por el usuario en me2: el expediente se guardaba sin tema
        (legítimo), después se le ponía Nota y guardaba igual, quedando is_nota=True sin
        jurisdicción. Ninguna validación lo cubría: la de create() ya había pasado y
        `@api.constrains('jurisdiction_dependence')` no dispara porque ese campo no está
        en el write. Se valida en write() cuando el write toca el tema."""
        exp = self.env['me.document_exp'].create(self._vals(99812))
        self.assertFalse(exp.is_nota)
        with self.assertRaises(exceptions.ValidationError) as ctx:
            exp.write({'main_topic_id': self.topic_nota.id})
        self.assertIn('Nota', str(ctx.exception))

    def test_setting_nota_topic_after_save_with_jurisdiction_ok(self):
        """El mismo cambio de tema SÍ pasa si en el mismo write se carga la jurisdicción
        (que es como el form lo va a mandar: el campo queda editable mientras esté vacío)."""
        exp = self.env['me.document_exp'].create(self._vals(99813))
        exp.write({
            'main_topic_id': self.topic_nota.id,
            'jurisdiction_dependence': self.jur.id,
        })
        self.assertTrue(exp.is_nota)
        self.assertEqual(exp.jurisdiction_dependence, self.jur)

    def test_changing_topic_away_from_nota_after_save_is_allowed(self):
        """No endurecer de más: sacarle el tema Nota a un expediente no debe bloquear
        (deja de aplicar la regla). El subtema va porque la licitación lo requiere
        (EPIC-004/TASK-005) — lo que se prueba es que el cambio DESDE Nota se permite."""
        exp = self.env['me.document_exp'].create(
            self._vals(99814, self.topic_nota, jurisdiction_dependence=self.jur.id))
        exp.write({'main_topic_id': self.topic_licitacion.id,
                   'secondary_topic_id': self.publica.id})
        self.assertFalse(exp.is_nota)

    def test_duplicate_warning_does_not_match_itself(self):
        """El aviso de duplicado no debe dispararse contra el propio expediente.

        Se hizo visible al permitir editar la jurisdicción después del alta: el onchange
        corre sobre un registro YA guardado, se encontraba a sí mismo y avisaba "ya
        existe". Antes no se notaba porque estos campos nunca eran editables post-alta."""
        exp = self.env['me.document_exp'].create(
            self._vals(99815, self.topic_nota, jurisdiction_dependence=self.jur.id))
        exp.flush_recordset()
        spec = {f: {} for f in ('dependence_id', 'document_type_id', 'number',
                                'period', 'jurisdiction_dependence')}
        res = exp.onchange(
            {'id': exp.id, 'dependence_id': self.dep_dem.id,
             'document_type_id': self.doc_type_exp.id, 'number': 99815,
             'period': self.base_vals['period'],
             'jurisdiction_dependence': self.jur.id},
            ['jurisdiction_dependence'], spec)
        self.assertFalse(res.get('warning'),
                         'no debe avisar duplicado contra sí mismo: %s' % res.get('warning'))

    def test_operator_cannot_change_nota_origin_after_save(self):
        """El "solo al ingreso" lo garantiza el BACKEND, no la vista.

        La vista deja el campo editable a propósito (condicionar el readonly al valor en
        edición bloqueaba al usuario y hacía que Odoo no enviara el valor al guardar). La
        regla real vive en el guard de write(): un operativo no puede tocar el origen de
        un expediente ya guardado. NO relajar este test: es lo único que sostiene la
        decisión de negocio."""
        exp = self.env['me.document_exp'].create(
            self._vals(99816, self.topic_nota, jurisdiction_dependence=self.jur.id))
        operador = self.env['res.users'].create({
            'name': 'Operador Nota Test', 'login': 'operador_nota_test',
            'group_ids': [(6, 0, [self.env.ref('me.group_user').id])],
        })
        otra = self.env['tmc.dependence'].create(
            {'name': 'Otra Jur Post Test', 'abbreviation': 'OJPT'})
        with self.assertRaises(exceptions.AccessError):
            exp.with_user(operador).write({'jurisdiction_dependence': otra.id})

    # --- IDEA 4: origen del 1er movimiento automático ---

    def _first_auto_movement_to_tmc(self, exp):
        return exp.document_movement_ids.filtered(
            lambda m: m.is_automatic and m.destination_dependence_id == self.dep_tmc)[:1]

    def test_nota_first_movement_origin_is_jurisdiction(self):
        """IDEA 4: el 1er movimiento automático de una Nota sale de la jurisdicción real
        (la secretaría), no del genérico dependence_id ('Departamento Ejecutivo')."""
        exp = self.env['me.document_exp'].create(
            self._vals(99820, self.topic_nota, jurisdiction_dependence=self.jur.id))
        first = self._first_auto_movement_to_tmc(exp)
        self.assertTrue(first, 'debe existir el 1er movimiento origen→TMC')
        self.assertEqual(first.origin_dependence_id, self.jur)

    def test_purchase_first_movement_origin_is_dependence(self):
        """No-regresión: en compras (jurisdicción vacía al ingreso, la completa JUNCO
        después) el 1er movimiento sigue saliendo de dependence_id (DEM)."""
        exp = self.env['me.document_exp'].create(
            self._vals(99821, self.topic_licitacion))
        first = self._first_auto_movement_to_tmc(exp)
        self.assertTrue(first)
        self.assertEqual(first.origin_dependence_id, self.dep_dem)

    # --- Dato preexistente (protege el update de producción) ---

    def test_legacy_dem_nota_without_jurisdiction_survives_recompute(self):
        """Una Nota DEM anterior a esta regla quedó legítimamente sin jurisdicción
        (bajo EPIC-004 ME no la cargaba). El recálculo de `is_nota` NO debe hacerla
        explotar.

        NO simplificar a un `create` normal: el valor de este test está en el camino
        que usa. Si la validación se colgara de `@api.constrains('is_nota')`, recomputar
        un campo stored corre las constrains que lo listan (orm/models.py,
        `_compute_field_value`) → `-u me` abortaría sobre estos registros y la base no
        cargaría. Verificado en me2: así falló antes de mover la validación a create()."""
        exp = self.env['me.document_exp'].create(
            self._vals(99810, self.topic_licitacion))
        self.assertFalse(exp.jurisdiction_dependence)
        # Simula el dato viejo: pasa a tema Nota SIN jurisdicción por el camino del
        # padre (_inherits), no por create() — como quedaron los cargados antes.
        exp.document_id.sudo().write(
            {'main_topic_ids': [(6, 0, [self.topic_nota.id])]})
        exp.flush_recordset()
        self.assertTrue(exp.is_nota)
        self.assertFalse(exp.jurisdiction_dependence)

    # --- Borde: cambiar el tema al cargar ---

    def test_onchange_topic_away_from_nota_clears_origin(self):
        """Si al cargar se cambia el tema de Nota a uno de compras, se limpia lo tipeado:
        en temas de compra el origen es de JUNCO y debe arrancar vacío (EPIC-004)."""
        record = self.env['me.document_exp'].new(
            self._vals(99809, self.topic_nota, jurisdiction_dependence=self.jur.id))
        record.main_topic_id = self.topic_licitacion
        record._onchange_main_topic_id()
        self.assertFalse(record.jurisdiction_dependence)
