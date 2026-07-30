from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestLicitacionSubtopic(TransactionCase):
    """IDEA 2 / recorte B1 — el subtema de una Licitación se acota a los 2 subtipos reales
    (Privada/Pública), no los 23 subtemas documentales de GD que cuelgan del tema. JUNCO
    deriva su process_type de este subtema (verificado y confirmado con junco). NO se toca
    tmc_data: las 23 etapas siguen colgando de Licitación (guardrail: junco.process_event
    usa licitacion.child_ids)."""

    def setUp(self):
        super().setUp()
        ref = self.env.ref
        self.licitacion = ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        self.publica = ref('tmc_data.tmc_document_topic_licitacion_publica', raise_if_not_found=False)
        self.privada = ref('tmc_data.tmc_document_topic_licitacion_privada', raise_if_not_found=False)
        self.concurso = ref('tmc_data.tmc_document_topic_concurso_precios', raise_if_not_found=False)
        if not (self.licitacion and self.publica and self.privada):
            self.skipTest("Temas de licitación de tmc_data no disponibles en esta DB")

    def _new_with_topic(self, topic):
        # .new() + proxy main_topic_id = el camino del form (reacciona antes de guardar).
        record = self.env['me.document_exp'].new({})
        record.main_topic_id = topic
        return record

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
