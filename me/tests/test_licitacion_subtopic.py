from odoo import exceptions, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestLicitacionSubtopic(TransactionCase):
    """EPIC-004/TASK-004 (B1) + TASK-005 (subtema requerido) — el subtema de una Licitación
    se acota a los 2 subtipos reales (Privada/Pública), no los 23 subtemas documentales de GD,
    y es OBLIGATORIO (JUNCO deriva su process_type del subtema y no puede cerrar upstream el
    caso 'licitación sin subtema'). Concurso/directa no llevan subtema. NO se toca tmc_data
    (guardrail: junco.process_event usa licitacion.child_ids)."""

    def setUp(self):
        super().setUp()
        ref = self.env.ref
        self.licitacion = ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        self.publica = ref('tmc_data.tmc_document_topic_licitacion_publica', raise_if_not_found=False)
        self.privada = ref('tmc_data.tmc_document_topic_licitacion_privada', raise_if_not_found=False)
        self.concurso = ref('tmc_data.tmc_document_topic_concurso_precios', raise_if_not_found=False)
        self.directa = ref('tmc_data.tmc_document_topic_contratacion_directa', raise_if_not_found=False)
        if not (self.licitacion and self.publica and self.privada):
            self.skipTest("Temas de licitación de tmc_data no disponibles en esta DB")
        Dep = self.env['tmc.dependence']
        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1) or self.env['tmc.document_type'].create(
            {'name': 'EXP Test', 'abbreviation': 'EXP'})
        self.dep_dem = Dep.search([('abbreviation', '=', 'DEM')], limit=1) or Dep.create(
            {'name': 'DEM Test', 'abbreviation': 'DEM'})
        self.base = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'period': str(fields.Date.today().year),
            'intake_date': fields.Date.today(),
            'date': fields.Date.today(),
        }

    def _new_with_topic(self, topic):
        # .new() + proxy main_topic_id = el camino del form (reacciona antes de guardar).
        record = self.env['me.document_exp'].new({})
        record.main_topic_id = topic
        return record

    def _create(self, number, topic=None, subtopic=None):
        vals = dict(self.base, number=number)
        if topic:
            vals['main_topic_ids'] = [(4, topic.id)]
        if subtopic:
            vals['secondary_topic_ids'] = [(4, subtopic.id)]
        return self.env['me.document_exp'].create(vals)

    def test_licitacion_allows_only_publica_privada(self):
        record = self._new_with_topic(self.licitacion)
        # ._origin: en un record .new() el campo devuelve NewId; comparamos los persistidos.
        self.assertEqual(record.allowed_secondary_topic_ids._origin, self.publica | self.privada)
        self.assertEqual(len(record.allowed_secondary_topic_ids), 2,
                         'Licitación debe ofrecer solo 2 subtemas, no los 25 de GD')

    def test_licitacion_excludes_etapas(self):
        record = self._new_with_topic(self.licitacion)
        adj = self.env.ref('tmc_data.tmc_document_topic_licitacion_adjudicacion',
                            raise_if_not_found=False)
        if adj:
            self.assertNotIn(adj, record.allowed_secondary_topic_ids,
                             'una "etapa" no debe ofrecerse como subtema del expediente')
            # ...pero SIGUE colgando de Licitación en tmc_data (guardrail junco/GD):
            self.assertEqual(adj.parent_id, self.licitacion)

    def test_reacts_to_form_proxy_before_save(self):
        record = self.env['me.document_exp'].new({})
        record.main_topic_id = self.licitacion
        self.assertEqual(record.allowed_secondary_topic_ids._origin, self.publica | self.privada)

    def test_non_licitacion_topic_keeps_children(self):
        """No-regresión: para un tema que NO es Licitación, el subtema sigue siendo los
        hijos del tema (comportamiento anterior)."""
        root = self.env['tmc.document_topic'].create(
            {'name': 'Tema NoLic Test', 'important': True})
        child = self.env['tmc.document_topic'].create(
            {'name': 'Sub NoLic Test', 'parent_id': root.id})
        record = self._new_with_topic(root)
        self.assertEqual(record.allowed_secondary_topic_ids._origin, child)

    def test_concurso_precios_empty_subtema(self):
        """Concurso de Precios no tiene hijos → subtema vacío (la vista lo oculta)."""
        if not self.concurso:
            self.skipTest("Concurso de Precios no disponible en esta DB")
        record = self._new_with_topic(self.concurso)
        self.assertFalse(record.allowed_secondary_topic_ids)

    # --- TASK-005: subtema requerido para Licitación (backend) ---

    def test_new_licitacion_without_subtema_raises(self):
        """Una Licitación nueva sin subtema no se puede crear (JUNCO deriva el subtipo de ahí)."""
        with self.assertRaises(exceptions.ValidationError) as ctx:
            self._create(95001, topic=self.licitacion)
        self.assertIn('licitaci', str(ctx.exception).lower())

    def test_new_licitacion_with_subtema_ok(self):
        exp = self._create(95002, topic=self.licitacion, subtopic=self.publica)
        self.assertTrue(exp.is_licitacion)
        self.assertEqual(exp.secondary_topic_id, self.publica)

    def test_concurso_without_subtema_ok(self):
        """No-regresión: concurso de precios NO lleva subtema → no se exige."""
        if not self.concurso:
            self.skipTest("Concurso de Precios no disponible")
        exp = self._create(95003, topic=self.concurso)
        self.assertFalse(exp.secondary_topic_id)

    def test_contratacion_directa_without_subtema_ok(self):
        """No-regresión: contratación directa NO lleva subtema → no se exige."""
        if not self.directa:
            self.skipTest("Contratación directa no disponible")
        exp = self._create(95004, topic=self.directa)
        self.assertFalse(exp.secondary_topic_id)

    def test_reclassify_to_licitacion_requires_subtema(self):
        """Reclasificar a Licitación (write del tema) sin subtema también se rechaza."""
        exp = self._create(95005)  # sin tema
        with self.assertRaises(exceptions.ValidationError):
            exp.write({'main_topic_id': self.licitacion.id})

    def test_removing_subtema_from_licitacion_raises(self):
        """Quitarle el subtema a una Licitación (write del subtema) se rechaza."""
        exp = self._create(95006, topic=self.licitacion, subtopic=self.publica)
        with self.assertRaises(exceptions.ValidationError):
            exp.write({'secondary_topic_id': False})

    def test_legacy_licitacion_without_subtema_survives_and_is_editable(self):
        """Required SOLO para nuevas: una Licitación vieja sin subtema (creada por un camino
        que no valida) NO se rompe ante una edición ajena al tema/subtema.

        NO simplificar: la validación vive en create()/write() (no en
        @api.constrains('is_licitacion')). Si se colgara de la constraint, recomputar el
        campo stored la dispararía sobre TODAS las licitaciones en cada `-u me` y abortaría
        el update sobre estas viejas — el caso real detectado en el chequeo de datos (había 1
        en me2)."""
        exp = self._create(95007, topic=self.licitacion, subtopic=self.publica)
        # Simula el dato viejo: le sacamos el subtema por el camino del padre (_inherits),
        # sin pasar por el write() de me que valida.
        exp.document_id.sudo().write({'secondary_topic_ids': [(5, 0, 0)]})
        exp.invalidate_recordset()
        self.assertTrue(exp.is_licitacion)
        self.assertFalse(exp.secondary_topic_id)
        # Editar algo ajeno al tema/subtema NO debe dispararse.
        exp.write({'fojas': 3})
        self.assertEqual(exp.fojas, 3)
