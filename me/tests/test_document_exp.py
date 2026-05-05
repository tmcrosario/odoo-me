from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDocumentExp(TransactionCase):

    def setUp(self):
        super().setUp()

        # tmc.document_type: buscar o crear tipo 'EXP'
        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        # tmc.dependence origen del expediente: buscar o crear 'DEM'
        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        # tmc.dependence jurisdicción (específica de test, nombre no usable en producción)
        self.dep_jur = self.env['tmc.dependence'].search(
            [('name', '=', 'Jurisdiccion ME Test')], limit=1
        )
        if not self.dep_jur:
            self.dep_jur = self.env['tmc.dependence'].create({
                'name': 'Jurisdiccion ME Test',
                'abbreviation': 'JURME',
            })

        # tmc.dependence TMC: necesaria para movimiento automático 1 (jurisdicción → TMC)
        self.dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        if not self.dep_tmc:
            self.dep_tmc = self.env['tmc.dependence'].create({
                'name': 'TMC',
                'abbreviation': 'TMC',
            })

        # tmc.dependence Mesa de Entradas: necesaria para movimiento automático 2 (TMC → ME)
        self.dep_mesa = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'ME')], limit=1
        )
        if not self.dep_mesa:
            self.dep_mesa = self.env['tmc.dependence'].create({
                'name': 'Mesa de Entradas',
                'abbreviation': 'ME',
            })

        self.current_year = str(fields.Date.today().year)

        # Vals base para expediente válido.
        # Número alto (99991) para evitar conflictos con datos reales existentes.
        self.valid_vals = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 99991,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': fields.Date.today(),
            'date': fields.Date.today(),
        }

    def test_create_expediente_basic(self):
        """
        Verifica que la creación de un expediente completo:
        - crea el registro me.document_exp
        - crea automáticamente tmc.document vía _inherits (document_id asignado)
        - los campos base se guardan en tmc.document correctamente
        - is_valid se computa True con los 5 campos básicos presentes
        """
        expediente = self.env['me.document_exp'].create(self.valid_vals)

        self.assertTrue(expediente.id)
        self.assertTrue(expediente.document_id.id)
        self.assertEqual(expediente.document_id.dependence_id, self.dep_dem)
        self.assertEqual(expediente.document_id.number, 99991)
        self.assertEqual(expediente.document_id.period, self.current_year)
        self.assertTrue(expediente.is_valid)

    def test_create_generates_two_movements(self):
        """
        Verifica que al crear un expediente se generan exactamente 2 movimientos automáticos:
        - movimiento 1: jurisdiction_dependence → TMC
        - movimiento 2: TMC → Mesa de Entradas
        Condición: ambas dependencias deben existir en la base (garantizado por setUp).
        """
        expediente = self.env['me.document_exp'].create(self.valid_vals)
        movements = expediente.document_movement_ids

        self.assertEqual(len(movements), 2)

        origins = movements.mapped('origin_dependence_id')
        destinations = movements.mapped('destination_dependence_id')

        self.assertIn(self.dep_jur, origins)
        self.assertIn(self.dep_tmc, origins)
        self.assertIn(self.dep_tmc, destinations)
        self.assertIn(self.dep_mesa, destinations)

    def test_create_tmc_generates_one_movement(self):
        """
        Cuando dependence_id = TMC, create() genera exactamente 1 movimiento automático:
        TMC → Mesa de Entradas.
        No debe crearse el movimiento TMC → TMC (origen == destino, sin sentido funcional).
        """
        tmc_vals = dict(
            self.valid_vals,
            number=99992,
            dependence_id=self.dep_tmc.id,
            jurisdiction_dependence=self.dep_tmc.id,
            source_dependence_id=self.dep_mesa.id,
        )
        expediente = self.env['me.document_exp'].create(tmc_vals)
        movements = expediente.document_movement_ids

        self.assertEqual(len(movements), 1)
        mov = movements[0]
        self.assertEqual(mov.origin_dependence_id, self.dep_tmc)
        self.assertEqual(mov.destination_dependence_id, self.dep_mesa)

    def test_create_tmc_no_self_movement(self):
        """
        Cuando dependence_id = TMC, no debe existir ningún movimiento
        con origin == destination == TMC.
        """
        tmc_vals = dict(
            self.valid_vals,
            number=99993,
            dependence_id=self.dep_tmc.id,
            jurisdiction_dependence=self.dep_tmc.id,
            source_dependence_id=self.dep_mesa.id,
        )
        expediente = self.env['me.document_exp'].create(tmc_vals)
        self_movements = expediente.document_movement_ids.filtered(
            lambda m: m.origin_dependence_id == m.destination_dependence_id
        )
        self.assertFalse(self_movements)

    def test_invalid_number_raises(self):
        """
        Verifica que la creación falla si number=0.
        La constraint _check_number en tmc.document rechaza number=0 para tipo EXP.
        """
        vals_numero_invalido = dict(self.valid_vals, number=0)
        with self.assertRaises(UserError):
            self.env['me.document_exp'].create(vals_numero_invalido)

    def test_create_registers_in_raa(self):
        """
        Verifica que al crear un expediente se crea automáticamente
        un registro raa.registry_aa vinculado al tmc.document del expediente.
        """
        expediente = self.env['me.document_exp'].create(self.valid_vals)
        raa = self.env['raa.registry_aa'].search(
            [('document_id', '=', expediente.document_id.id)]
        )
        self.assertEqual(len(raa), 1)
        self.assertEqual(raa.document_id, expediente.document_id)

    def test_unlink_cascades_to_tmc_document(self):
        """
        Verifica que al eliminar un expediente también se elimina el tmc.document
        vinculado. El unlink() de me.document_exp llama explícitamente a
        document_id.unlink() antes de super() para manejar la delegación _inherits.
        """
        expediente = self.env['me.document_exp'].create(self.valid_vals)
        doc_id = expediente.document_id.id
        expediente.unlink()
        doc_still_exists = self.env['tmc.document'].search(
            [('id', '=', doc_id)]
        )
        self.assertFalse(doc_still_exists)

    def test_is_valid_false_without_jurisdiction(self):
        """
        Verifica que is_valid=False cuando falta jurisdiction_dependence.
        Usa env.new() para crear un registro en memoria sin tocar la DB,
        evitando restricciones required=True del ORM en campos obligatorios.
        """
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 1,
            'period': self.current_year,
            # jurisdiction_dependence ausente → is_valid debe ser False
        })
        self.assertFalse(record.is_valid)

    def test_is_origin_complete_true(self):
        """is_origin_complete = True con dependence_id, number y period presentes."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_dem.id,
            'number': 1,
            'period': self.current_year,
        })
        self.assertTrue(record.is_origin_complete)

    def test_is_origin_complete_false_missing_number(self):
        """is_origin_complete = False si falta number."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_dem.id,
            'period': self.current_year,
        })
        self.assertFalse(record.is_origin_complete)

    def test_is_origin_complete_false_missing_period(self):
        """is_origin_complete = False si falta period."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_dem.id,
            'number': 1,
        })
        self.assertFalse(record.is_origin_complete)

    def test_is_origin_complete_false_missing_dependence(self):
        """is_origin_complete = False si falta dependence_id."""
        record = self.env['me.document_exp'].new({
            'number': 1,
            'period': self.current_year,
        })
        self.assertFalse(record.is_origin_complete)

    def test_intake_date_future_raises(self):
        """intake_date no puede ser fecha futura — debe lanzar ValidationError."""
        future_date = fields.Date.today() + timedelta(days=1)
        vals = dict(self.valid_vals, number=99992, intake_date=future_date)
        with self.assertRaises(ValidationError):
            self.env['me.document_exp'].create(vals)

    def test_intake_date_accepts_different_year_than_period(self):
        """intake_date no se valida contra period — año distinto debe aceptarse."""
        past_year_date = date(2024, 1, 15)
        vals = dict(self.valid_vals, number=99993, period='2023', intake_date=past_year_date)
        expediente = self.env['me.document_exp'].create(vals)
        self.assertEqual(expediente.intake_date, past_year_date)

    def test_intake_date_stored_correctly(self):
        """intake_date se persiste correctamente en el registro."""
        today = fields.Date.today()
        expediente = self.env['me.document_exp'].create(
            dict(self.valid_vals, number=99994, intake_date=today)
        )
        self.assertEqual(expediente.intake_date, today)

    def test_computed_name_after_phase1_complete(self):
        """computed_name se genera al completar dependence_id, number y period,
        sin necesidad de jurisdiction_dependence ni document_type_id."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_dem.id,
            'number': 42,
            'period': self.current_year,
        })
        expected = f"EXP-{str(42).zfill(6)}-DEM/{self.current_year}"
        self.assertEqual(record.computed_name, expected)

    def test_computed_name_empty_when_phase1_incomplete(self):
        """computed_name es cadena vacía si falta algún campo de Fase 1."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_dem.id,
            'number': 42,
            # period ausente
        })
        self.assertEqual(record.computed_name, "Unnamed Document")

    def test_tmc_has_thirteen_internal_dependences_in_nomenclator(self):
        """
        Verifica que TMC tiene exactamente 13 dependencias internas en
        tmc.dependence_order con parent_id = TMC (rango 1.13.80–1.13.99).
        Requiere que los datos de odoo-tmc-data estén cargados.
        """
        dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        self.assertTrue(dep_tmc, "La dependencia TMC debe existir")

        internal_orders = self.env['tmc.dependence_order'].search([
            ('parent_id', '=', dep_tmc.id),
            ('code', '>=', '1.13.80'),
            ('code', '<=', '1.13.99'),
        ])
        self.assertEqual(
            len(internal_orders), 13,
            f"Se esperan 13 dependencias internas de TMC, encontradas: {len(internal_orders)}"
        )

    def test_source_dependence_optional_on_create(self):
        """source_dependence_id es opcional — crear expediente sin él no falla."""
        expediente = self.env['me.document_exp'].create(self.valid_vals)
        self.assertFalse(expediente.source_dependence_id)

    def test_dependence_invalid_abbreviation_raises(self):
        """
        Crear un expediente con una dependencia cuya abbreviation no está
        en ['DEM', 'TMC', 'CM'] debe lanzar ValidationError.
        """
        dep_invalid = self.env['tmc.dependence'].create({
            'name': 'Dependencia Invalida Test',
            'abbreviation': 'INV',
        })
        vals = dict(self.valid_vals, number=99990, dependence_id=dep_invalid.id)
        with self.assertRaises(ValidationError):
            self.env['me.document_exp'].create(vals)

    def test_dependence_valid_abbreviations_accepted(self):
        """
        Crear expedientes con abbreviation DEM, TMC y CM no lanza error.
        DEM ya existe en setUp. TMC y CM se buscan o crean.
        """
        dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        dep_cm = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'CM')], limit=1
        )
        if not dep_cm:
            dep_cm = self.env['tmc.dependence'].create({
                'name': 'Concejo Municipal Test',
                'abbreviation': 'CM',
            })

        for number, dep in [(99988, self.dep_dem), (99989, dep_tmc), (99987, dep_cm)]:
            exp = self.env['me.document_exp'].create(
                dict(self.valid_vals, number=number, dependence_id=dep.id)
            )
            self.assertTrue(exp.id)

    def test_tmc_internal_dependences_include_expected_abbreviations(self):
        """
        Verifica que las dependencias internas de TMC incluyen las abreviaciones
        esperadas: ME, VOC, SEC, FC, CF, DIC, DAL, DAT, DCD, DAF, AFC.
        """
        dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        self.assertTrue(dep_tmc, "La dependencia TMC debe existir")

        internal_orders = self.env['tmc.dependence_order'].search([
            ('parent_id', '=', dep_tmc.id),
            ('code', '>=', '1.13.80'),
            ('code', '<=', '1.13.99'),
        ])
        found_abbreviations = set(internal_orders.mapped('dependence_id.abbreviation'))
        expected_abbreviations = {'ME', 'VOC', 'SEC', 'FC', 'CF', 'DIC', 'DAL', 'DAT', 'DCD', 'DAF', 'AFC', 'ARCH', 'LEG'}
        self.assertEqual(found_abbreviations, expected_abbreviations)


@tagged('post_install', '-at_install')
class TestSourceDependence(TransactionCase):
    """Tests para source_dependence_id y allowed_sub_dependence_ids en me.document_exp."""

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        # Jurisdicción de prueba aislada (no interfiere con datos reales)
        self.dep_jur_test = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Source Test',
            'abbreviation': 'JSRC',
        })
        # Otra jurisdicción para testear cambio de jurisdicción
        self.dep_jur_alt = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Alt Test',
            'abbreviation': 'JALT',
        })

        # Reparticiones hijas de dep_jur_test
        self.dep_child_a = self.env['tmc.dependence'].create({
            'name': 'Reparticion Child A',
            'abbreviation': 'RCA',
        })
        self.dep_child_b = self.env['tmc.dependence'].create({
            'name': 'Reparticion Child B',
            'abbreviation': 'RCB',
        })
        # Repartición que NO es hija de dep_jur_test
        self.dep_unrelated = self.env['tmc.dependence'].create({
            'name': 'Reparticion Unrelated',
            'abbreviation': 'RCU',
        })

        # Registros en tmc.dependence_order: child_a y child_b bajo dep_jur_test
        self.env['tmc.dependence_order'].create({
            'code': '9.99.01',
            'parent_id': self.dep_jur_test.id,
            'dependence_id': self.dep_child_a.id,
        })
        self.env['tmc.dependence_order'].create({
            'code': '9.99.02',
            'parent_id': self.dep_jur_test.id,
            'dependence_id': self.dep_child_b.id,
        })

        self.current_year = str(fields.Date.today().year)

        self.base_vals = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 99995,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur_test.id,
            'intake_date': fields.Date.today(),
            'date': fields.Date.today(),
            'source_dependence_id': self.dep_child_a.id,
        }

    def test_allowed_sub_dependence_ids_returns_children(self):
        """
        allowed_sub_dependence_ids retorna las dependencias hijas de la
        jurisdicción seleccionada, consultando tmc.dependence_order por parent_id.
        Usa un record guardado para evitar el problema de NewId en new() records.
        """
        expediente = self.env['me.document_exp'].create(self.base_vals)
        self.assertIn(self.dep_child_a, expediente.allowed_sub_dependence_ids)
        self.assertIn(self.dep_child_b, expediente.allowed_sub_dependence_ids)
        self.assertNotIn(self.dep_unrelated, expediente.allowed_sub_dependence_ids)

    def test_allowed_sub_dependence_ids_empty_without_jurisdiction(self):
        """allowed_sub_dependence_ids es vacío cuando no hay jurisdicción seleccionada."""
        record = self.env['me.document_exp'].new({})
        self.assertFalse(record.allowed_sub_dependence_ids)

    def test_source_dependence_cleared_on_jurisdiction_change(self):
        """
        Al cambiar jurisdiction_dependence, source_dependence_id se limpia
        para evitar datos inconsistentes entre jurisdicción y repartición.
        """
        record = self.env['me.document_exp'].new({
            'jurisdiction_dependence': self.dep_jur_test.id,
            'source_dependence_id': self.dep_child_a.id,
        })
        self.assertEqual(record.source_dependence_id, self.dep_child_a)

        record.jurisdiction_dependence = self.dep_jur_alt
        record._onchange_jurisdiction_dependence()

        self.assertFalse(record.source_dependence_id)

    def test_create_with_source_dependence_persists(self):
        """source_dependence_id se persiste correctamente al crear el expediente."""
        vals = dict(self.base_vals, source_dependence_id=self.dep_child_a.id)
        expediente = self.env['me.document_exp'].create(vals)
        self.assertEqual(expediente.source_dependence_id, self.dep_child_a)


@tagged('post_install', '-at_install')
class TestSecondaryTopics(TransactionCase):
    """
    Tests para #013 — Selección de subtema en el campo asunto.
    Verifica el comportamiento de secondary_topic_ids heredado de tmc.document
    vía _inherits en me.document_exp.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Topics Test',
            'abbreviation': 'JTOP',
        })

        # Tema raíz de prueba aislado
        self.topic_root = self.env['tmc.document_topic'].create({
            'name': 'Tema Raiz Test',
            'important': True,
        })
        # Subtema bajo el tema raíz
        self.topic_sub = self.env['tmc.document_topic'].create({
            'name': 'Subtema Test A',
            'parent_id': self.topic_root.id,
        })
        # Segundo tema raíz sin subtemas
        self.topic_root_no_sub = self.env['tmc.document_topic'].create({
            'name': 'Tema Sin Subtemas',
            'important': True,
        })

        self.current_year = str(fields.Date.today().year)

        self.base_vals = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 99996,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': fields.Date.today(),
            'date': fields.Date.today(),
        }

    def test_create_without_secondary_topic_does_not_fail(self):
        """secondary_topic_ids es opcional — crear expediente sin él no falla."""
        expediente = self.env['me.document_exp'].create(self.base_vals)
        self.assertFalse(expediente.secondary_topic_ids)

    def test_create_with_secondary_topic_persists(self):
        """secondary_topic_ids se persiste correctamente al crear el expediente."""
        vals = dict(
            self.base_vals,
            number=99997,
            main_topic_ids=[(4, self.topic_root.id)],
            secondary_topic_ids=[(4, self.topic_sub.id)],
        )
        expediente = self.env['me.document_exp'].create(vals)
        self.assertIn(self.topic_sub, expediente.secondary_topic_ids)

    def test_secondary_topic_filters_to_children_of_main(self):
        """
        secondary_topic_ids del modelo tiene domain [('parent_id', 'in', main_topic_ids)].
        Verificamos que el subtema creado pertenece al tema raíz correcto.
        """
        self.assertEqual(self.topic_sub.parent_id, self.topic_root)

    def test_onchange_main_topic_clears_unrelated_secondary(self):
        """
        Al cambiar main_topic_ids, secondary_topic_ids se limpia si el subtema
        no pertenece al nuevo tema.
        _onchange_main_topic_ids está definido en tmc.document (_inherits no hereda
        métodos en me.document_exp). Se testea directamente sobre tmc.document,
        que es la capa donde el onchange opera cuando se dispara desde la UI.
        """
        doc = self.env['tmc.document'].new({
            'main_topic_ids': [(4, self.topic_root.id)],
            'secondary_topic_ids': [(4, self.topic_sub.id)],
        })
        self.assertTrue(doc.secondary_topic_ids)

        # Cambiar main_topic_ids a vacío y ejecutar el onchange
        doc.main_topic_ids = self.env['tmc.document_topic']
        doc._onchange_main_topic_ids()

        self.assertFalse(doc.secondary_topic_ids)

    def test_secondary_topic_empty_when_no_subtopics_exist(self):
        """
        Si el tema seleccionado no tiene subtemas, secondary_topic_ids
        queda vacío — el campo aparece pero sin opciones disponibles.
        """
        record = self.env['me.document_exp'].new({
            'main_topic_ids': [(4, self.topic_root_no_sub.id)],
        })
        # No hay subtemas de topic_root_no_sub — secondary sigue vacío
        self.assertFalse(record.secondary_topic_ids)


@tagged('post_install', '-at_install')
class TestTopicProxyFields(TransactionCase):
    """
    Tests para los campos proxy main_topic_id y secondary_topic_id en me.document_exp.
    Estos campos Many2one envuelven los Many2many subyacentes de tmc.document,
    proporcionando selección única de tema y subtema sin modificar el modelo base.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Proxy Test',
            'abbreviation': 'JPXY',
        })

        self.topic_root = self.env['tmc.document_topic'].create({
            'name': 'Tema Proxy Test',
            'important': True,
        })
        self.topic_sub = self.env['tmc.document_topic'].create({
            'name': 'Subtema Proxy A',
            'parent_id': self.topic_root.id,
        })
        self.topic_root_alt = self.env['tmc.document_topic'].create({
            'name': 'Tema Alt Proxy',
            'important': True,
        })

        self.current_year = str(fields.Date.today().year)

        self.base_vals = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 99998,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': fields.Date.today(),
            'date': fields.Date.today(),
        }

    def test_main_topic_id_computes_from_main_topic_ids(self):
        """main_topic_id retorna el primer elemento de main_topic_ids."""
        expediente = self.env['me.document_exp'].create(dict(
            self.base_vals,
            main_topic_ids=[(6, 0, [self.topic_root.id])],
        ))
        self.assertEqual(expediente.main_topic_id, self.topic_root)

    def test_secondary_topic_id_computes_from_secondary_topic_ids(self):
        """secondary_topic_id retorna el primer elemento de secondary_topic_ids."""
        expediente = self.env['me.document_exp'].create(dict(
            self.base_vals,
            number=99999,
            main_topic_ids=[(6, 0, [self.topic_root.id])],
            secondary_topic_ids=[(6, 0, [self.topic_sub.id])],
        ))
        self.assertEqual(expediente.secondary_topic_id, self.topic_sub)

    def test_set_main_topic_id_writes_to_main_topic_ids(self):
        """Asignar main_topic_id (inverse) actualiza main_topic_ids subyacente."""
        expediente = self.env['me.document_exp'].create(self.base_vals)
        expediente.main_topic_id = self.topic_root
        self.assertIn(self.topic_root, expediente.main_topic_ids)

    def test_set_secondary_topic_id_writes_to_secondary_topic_ids(self):
        """Asignar secondary_topic_id (inverse) actualiza secondary_topic_ids subyacente."""
        expediente = self.env['me.document_exp'].create(dict(
            self.base_vals,
            main_topic_ids=[(6, 0, [self.topic_root.id])],
        ))
        expediente.secondary_topic_id = self.topic_sub
        self.assertIn(self.topic_sub, expediente.secondary_topic_ids)

    def test_onchange_main_topic_id_clears_secondary(self):
        """Al cambiar main_topic_id, secondary_topic_id se limpia vía onchange."""
        record = self.env['me.document_exp'].new({
            'main_topic_ids': [(4, self.topic_root.id)],
            'secondary_topic_ids': [(4, self.topic_sub.id)],
        })
        self.assertTrue(record.secondary_topic_id)

        record.main_topic_id = self.topic_root_alt
        record._onchange_main_topic_id()

        self.assertFalse(record.secondary_topic_id)

    def test_secondary_topic_id_empty_when_no_main(self):
        """secondary_topic_id es False cuando no hay tema principal seleccionado."""
        record = self.env['me.document_exp'].new({})
        self.assertFalse(record.main_topic_id)
        self.assertFalse(record.secondary_topic_id)

    def test_allowed_exp_topic_ids_contains_licitacion_and_nota(self):
        """
        allowed_exp_topic_ids incluye exactamente los temas raíz Licitación y Nota,
        resueltos por XML ID (tmc_data.tmc_document_topic_licitacion y _nota).
        Requiere que los datos de tmc_data estén instalados.
        """
        record = self.env['me.document_exp'].new({})
        topic_names = record.allowed_exp_topic_ids.mapped('name')
        self.assertIn('Licitación', topic_names)
        self.assertIn('Nota', topic_names)

    def test_allowed_exp_topic_ids_excludes_other_root_topics(self):
        """
        allowed_exp_topic_ids no incluye temas raíz ajenos a EXP.
        El tema de prueba topic_root (creado en setUp, sin XML ID) no debe aparecer.
        """
        record = self.env['me.document_exp'].new({})
        self.assertNotIn(self.topic_root, record.allowed_exp_topic_ids)


@tagged('post_install', '-at_install')
class TestRequiredFields017(TransactionCase):
    """Tests para #017 — Campos obligatorios en Fase 2 del expediente.

    Cubre las reglas:
    - date: required, validación manual en create() y write()
    - fojas: default=0, required en vista; 0 es valor válido
    - source_dependence_id: required condicional cuando la jurisdicción
      tiene hijos en tmc.dependence_order
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        # Jurisdicción sin hijos en el nomenclador
        self.dep_jur_no_children = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Sin Hijos 017',
            'abbreviation': 'JSH017',
        })

        # Jurisdicción con hijos en el nomenclador
        self.dep_jur_with_children = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Con Hijos 017',
            'abbreviation': 'JCH017',
        })
        self.dep_sub = self.env['tmc.dependence'].create({
            'name': 'Sub Dependencia 017',
            'abbreviation': 'SUB017',
        })
        self.env['tmc.dependence_order'].create({
            'code': '9.98.01',
            'parent_id': self.dep_jur_with_children.id,
            'dependence_id': self.dep_sub.id,
        })

        self.topic_root = self.env['tmc.document_topic'].create({
            'name': 'Tema Root 017',
            'important': True,
        })

        self.current_year = str(fields.Date.today().year)
        self.today = fields.Date.today()

        # Vals base válidos (jurisdiction sin hijos)
        self.base_vals = {
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 88890,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur_no_children.id,
            'intake_date': self.today,
            'date': self.today,
        }

    def test_create_without_date_raises(self):
        """Crear expediente sin date lanza ValidationError."""
        vals = dict(self.base_vals, number=88891)
        del vals['date']
        with self.assertRaises(ValidationError):
            self.env['me.document_exp'].create(vals)

    def test_create_with_date_does_not_raise(self):
        """Crear expediente con date válida no falla."""
        exp = self.env['me.document_exp'].create(dict(self.base_vals, number=88892))
        self.assertTrue(exp.id)

    def test_date_persists_after_create(self):
        """La fecha debe persistirse y leerse correctamente via ORM después de create().

        Regresión: _update_document_date() actualizaba la DB via SQL pero no invalidaba
        el cache ORM. La relectura del campo retornaba False (valor cacheado antes del
        UPDATE), vaciando visualmente la fecha en el formulario tras el save.
        """
        exp = self.env['me.document_exp'].create(dict(self.base_vals, number=88897))
        self.assertEqual(exp.date, self.today)

    def test_create_with_fojas_zero_does_not_raise(self):
        """Crear expediente con fojas=0 no falla (0 es valor válido)."""
        exp = self.env['me.document_exp'].create(dict(self.base_vals, number=88893, fojas=0))
        self.assertTrue(exp.id)
        self.assertEqual(exp.fojas, 0)

    def test_create_jurisdiction_with_children_without_source_raises(self):
        """Crear expediente con jurisdicción que tiene hijos y sin
        source_dependence_id lanza ValidationError."""
        vals = dict(
            self.base_vals,
            number=88894,
            jurisdiction_dependence=self.dep_jur_with_children.id,
        )
        with self.assertRaises(ValidationError):
            self.env['me.document_exp'].create(vals)

    def test_create_jurisdiction_without_children_no_source_does_not_raise(self):
        """Crear expediente con jurisdicción sin hijos y sin source_dependence_id
        no falla (conditional required — no hay opciones disponibles)."""
        exp = self.env['me.document_exp'].create(dict(self.base_vals, number=88895))
        self.assertTrue(exp.id)
        self.assertFalse(exp.source_dependence_id)

    def test_create_jurisdiction_with_children_and_source_does_not_raise(self):
        """Crear expediente con jurisdicción con hijos y source_dependence_id
        válido no falla."""
        exp = self.env['me.document_exp'].create(dict(
            self.base_vals,
            number=88896,
            jurisdiction_dependence=self.dep_jur_with_children.id,
            source_dependence_id=self.dep_sub.id,
        ))
        self.assertTrue(exp.id)
        self.assertEqual(exp.source_dependence_id, self.dep_sub)

    def test_main_topic_id_available_regardless_of_dependence(self):
        """
        main_topic_id no filtra por dependence_id.document_topic_ids.
        El mismo tema raíz debe ser seleccionable para expedientes de
        cualquier dependencia (DEM, TMC, CM): los temas EXP son independientes
        del organismo de origen.
        """
        dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        dep_cm = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'CM')], limit=1
        )
        if not dep_cm:
            dep_cm = self.env['tmc.dependence'].create({
                'name': 'Concejo Municipal Test',
                'abbreviation': 'CM',
            })

        for dep in (self.dep_dem, dep_tmc, dep_cm):
            expediente = self.env['me.document_exp'].create(dict(
                self.base_vals,
                dependence_id=dep.id,
                main_topic_ids=[(6, 0, [self.topic_root.id])],
            ))
            self.assertEqual(
                expediente.main_topic_id,
                self.topic_root,
                f"El tema debe ser seleccionable para dependencia {dep.abbreviation}",
            )


@tagged('post_install', '-at_install')
class TestDocumentTopicsTMC(TransactionCase):
    """
    Tests para #014 — Nomenclador de temas y subtemas para expedientes del TMC.
    Verifica que los temas y subtemas cargados en odoo-tmc-data están disponibles
    para la dependencia TMC.
    Requiere que los datos de odoo-tmc-data estén instalados.
    """

    def setUp(self):
        super().setUp()
        self.dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )

    def test_tmc_has_licitacion_and_nota_topics(self):
        """
        Para dependence_id = TMC, document_topic_ids incluye al menos
        tmc_document_topic_licitacion y tmc_document_topic_nota.
        """
        self.assertTrue(self.dep_tmc, "La dependencia TMC debe existir")
        topic_names = self.dep_tmc.document_topic_ids.mapped('name')
        self.assertIn('Licitación', topic_names)
        self.assertIn('Nota', topic_names)

    def test_licitacion_subtopics_include_expected(self):
        """
        Los subtemas de Licitación incluyen los 5 esperados:
        Pública, Privada, Documentación, Descargo, Impugnación.
        """
        licitacion = self.env['tmc.document_topic'].search(
            [('name', '=', 'Licitación'), ('parent_id', '=', False)], limit=1
        )
        self.assertTrue(licitacion, "El tema raíz 'Licitación' debe existir")
        subtopic_names = licitacion.child_ids.mapped('name')
        for expected in ('Pública', 'Privada', 'Documentación', 'Descargo', 'Impugnación'):
            self.assertIn(
                expected, subtopic_names,
                f"El subtema '{expected}' debe existir bajo Licitación"
            )

    def test_nota_subtopics_include_all_four(self):
        """
        Los subtemas de Nota incluyen los 4 definidos:
        Externa, Interna, Originada en el TMC, Informe.
        """
        nota = self.env['tmc.document_topic'].search(
            [('name', '=', 'Nota'), ('parent_id', '=', False)], limit=1
        )
        self.assertTrue(nota, "El tema raíz 'Nota' debe existir")
        subtopic_names = nota.child_ids.mapped('name')
        for expected in ('Externa', 'Interna', 'Originada en el TMC', 'Informe'):
            self.assertIn(
                expected, subtopic_names,
                f"El subtema '{expected}' debe existir bajo Nota"
            )

    def test_nota_is_root_topic(self):
        """Nota es un tema raíz (parent_id = False)."""
        nota = self.env['tmc.document_topic'].search(
            [('name', '=', 'Nota'), ('parent_id', '=', False)], limit=1
        )
        self.assertTrue(nota, "El tema raíz 'Nota' debe existir sin parent")
        self.assertFalse(nota.parent_id)

    def test_nota_subtopics_have_nota_as_parent(self):
        """
        Cada subtema de Nota tiene parent_id apuntando al tema raíz 'Nota'.
        Verifica la integridad de la jerarquía.
        """
        nota = self.env['tmc.document_topic'].search(
            [('name', '=', 'Nota'), ('parent_id', '=', False)], limit=1
        )
        self.assertTrue(nota)
        for subtopic_name in ('Externa', 'Interna', 'Originada en el TMC', 'Informe'):
            subtopic = self.env['tmc.document_topic'].search(
                [('name', '=', subtopic_name), ('parent_id', '=', nota.id)], limit=1
            )
            self.assertTrue(
                subtopic,
                f"El subtema '{subtopic_name}' debe existir con parent_id = Nota"
            )


@tagged('post_install', '-at_install')
class TestFojasLock(TransactionCase):
    """Tests para #018 — matriz de permisos de me y restricción de fojas.

    Regla: fojas puede cargarse al crear el expediente. Una vez creado,
    solo me.group_manager puede modificar el valor.
    me.group_user tiene perm_write=0 en me.document_exp → AccessError antes
    de llegar al check de fojas.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        # Jurisdicción sin hijos para no disparar constraint de source_dependence_id
        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Fojas Lock Test',
            'abbreviation': 'JFLK',
        })

        self.current_year = str(fields.Date.today().year)
        self.today = fields.Date.today()

        self.expediente = self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 66661,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 3,
        })

        # Gestor ME: CRUD en me.document_exp y me.document_movement.
        # implied_ids: me.group_user → tmc.group_user; tmc.group_manager (para write en tmc.document)
        self.manager_user = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Gestor ME Test',
            'login': 'manager_fojas_lock_test@test.com',
            'group_ids': [(6, 0, [self.env.ref('me.group_manager').id])],
        })

        # Operador ME: R_C_ en me.document_exp y me.document_movement.
        # implied_ids: tmc.group_user (para crear tmc.document via _inherits)
        self.operator_user = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Operador ME Test',
            'login': 'operator_fojas_lock_test@test.com',
            'group_ids': [(6, 0, [self.env.ref('me.group_user').id])],
        })

    def test_create_with_fojas_works(self):
        """Crear expediente con fojas cargado no lanza error."""
        self.assertEqual(self.expediente.fojas, 3)

    def test_manager_can_write_fojas(self):
        """me.group_manager puede corregir fojas post-creación."""
        self.expediente.with_user(self.manager_user).write({'fojas': 10})
        self.assertEqual(self.expediente.fojas, 10)

    def test_admin_can_write_fojas(self):
        """Usuario con base.group_system puede modificar fojas (implica me.group_manager)."""
        # El usuario de test (uid=1) pertenece a base.group_system
        self.expediente.write({'fojas': 10})
        self.assertEqual(self.expediente.fojas, 10)

    def test_manager_can_write_other_fields(self):
        """me.group_manager puede editar campos que no son fojas."""
        self.expediente.with_user(self.manager_user).write({
            'document_object': 'Referencia de prueba',
        })
        self.assertEqual(self.expediente.document_object, 'Referencia de prueba')

    def test_operator_cannot_write_fojas(self):
        """me.group_user no puede modificar expedientes existentes — recibe AccessError."""
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_user).write({'fojas': 10})

    def test_operator_can_create_expediente(self):
        """me.group_user puede crear expedientes (perm_create=1)."""
        new_exp = self.env['me.document_exp'].with_user(self.operator_user).create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 77771,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 5,
        })
        self.assertEqual(new_exp.fojas, 5)

    def test_operator_can_create_new_expediente(self):
        """me.group_user puede crear expedientes nuevos sin AccessError.

        Verifica que el flag me_create_in_progress permite que write() interno
        del flujo de create() (ORM _inherits sync, computed-field flush) no
        quede bloqueado por el guard de no-managers.
        """
        new_exp = self.env['me.document_exp'].with_user(self.operator_user).create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 77772,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 5,
        })
        self.assertEqual(new_exp.fojas, 5)

    def test_operator_cannot_edit_existing_expediente(self):
        """me.group_user no puede editar expedientes existentes — recibe AccessError."""
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_user).write({'document_object': 'Intento de edición'})

    def test_operator_can_create_new_movement(self):
        """me.group_user puede crear movimientos nuevos."""
        dep_me = self.env['tmc.dependence'].search([('abbreviation', '=', 'ME')], limit=1)
        dep_arch = self.env['tmc.dependence'].search([('abbreviation', '=', 'ARCH')], limit=1)
        if not dep_arch:
            dep_arch = dep_me
        movement = self.env['me.document_movement'].with_user(self.operator_user).create({
            'expediente_id': self.expediente.id,
            'date': fields.Datetime.now(),
            'origin_dependence_id': dep_me.id if dep_me else self.dep_dem.id,
            'destination_dependence_id': dep_arch.id if dep_arch else self.dep_dem.id,
            'fojas': 3,
        })
        self.assertTrue(movement.id)

    def test_operator_cannot_edit_existing_movement(self):
        """me.group_user no puede editar movimientos existentes — recibe AccessError."""
        existing_movement = self.expediente.document_movement_ids[:1]
        self.assertTrue(existing_movement, "El expediente debe tener al menos un movimiento automático")
        with self.assertRaises(AccessError):
            existing_movement.with_user(self.operator_user).write({'fojas': 99})

    def test_create_in_progress_flag_allows_internal_write(self):
        """El flag me_create_in_progress permite write() para no-managers.

        Simula el write() interno que el ORM ejecuta durante el flujo de create()
        (e.g., flush de stored computed fields, _inherits sync de campos propios
        del modelo hijo). Sin el flag, el guard bloquearía con AccessError; con
        él, debe pasar. Solo aplica a campos en la tabla me_document_exp (no
        delegados a tmc.document, que tiene su propia ACL).
        """
        self.expediente.with_user(self.operator_user).with_context(
            me_create_in_progress=True
        ).write({'fojas': 99})
        self.expediente.invalidate_recordset(['fojas'])
        self.assertEqual(self.expediente.fojas, 99)

        # Sin el flag, el mismo write() queda bloqueado.
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_user).write({'fojas': 10})

    def test_operator_write_delegated_fields_during_create_flow(self):
        """me_create_in_progress permite write() sobre campos delegados (tmc.document) vía sudo().

        Reproduce el path de UI/web_save: el ORM llama me.document_exp.write() con campos
        almacenados en tmc_document (delegados via _inherits) durante el flujo de alta.
        Sin sudo() en self.document_id.write(), falla con AccessError por perm_write=0
        en tmc.document para me.group_user.
        """
        # Simula el write() que el ORM emite en web_save con campos delegados.
        self.expediente.with_user(self.operator_user).with_context(
            me_create_in_progress=True
        ).write({'document_object': 'Referencia asignada durante alta'})
        self.expediente.invalidate_recordset(['document_object'])
        self.assertEqual(self.expediente.document_object, 'Referencia asignada durante alta')

    def test_operator_cannot_write_delegated_fields_without_flag(self):
        """Sin me_create_in_progress, el guard bloquea write() sobre campos delegados."""
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_user).write({'document_object': 'Intento directo'})

    def test_manager_can_write_delegated_fields_without_flag(self):
        """me.group_manager puede escribir campos delegados sin flag."""
        self.expediente.with_user(self.manager_user).write({'document_object': 'Edición de manager'})
        self.expediente.invalidate_recordset(['document_object'])
        self.assertEqual(self.expediente.document_object, 'Edición de manager')

    def test_operator_create_with_main_topic_id(self):
        """Operador puede crear expediente con main_topic_id — inverse no dispara AccessError.

        Reproduce el bug: _set_main_topic_id asignaba record.main_topic_ids = [...]
        que pasaba por _inverse_related del ORM y llamaba tmc.document.write() con
        usuario operador (perm_write=0) → AccessError envuelto con 'Implicitly accessed
        through'. El fix escribe directamente vía record.document_id.sudo().write().
        """
        topic = self.env.ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        if not topic:
            topic = self.env['tmc.document_topic'].create({
                'name': 'Topic Test Operator Create',
            })
        new_exp = self.env['me.document_exp'].with_user(self.operator_user).create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 77774,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 2,
            'main_topic_id': topic.id,
        })
        self.assertEqual(new_exp.main_topic_id.id, topic.id)

    def test_operator_create_with_secondary_topic_id(self):
        """Operador puede crear expediente con secondary_topic_id — inverse no dispara AccessError."""
        parent_topic = self.env.ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        if not parent_topic:
            parent_topic = self.env['tmc.document_topic'].create({'name': 'Parent Topic Test'})
        child_topic = self.env['tmc.document_topic'].search(
            [('parent_id', '=', parent_topic.id)], limit=1
        )
        if not child_topic:
            child_topic = self.env['tmc.document_topic'].create({
                'name': 'Child Topic Test',
                'parent_id': parent_topic.id,
            })
        new_exp = self.env['me.document_exp'].with_user(self.operator_user).create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 77775,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 2,
            'main_topic_id': parent_topic.id,
            'secondary_topic_id': child_topic.id,
        })
        self.assertEqual(new_exp.secondary_topic_id.id, child_topic.id)

    def test_operator_cannot_edit_main_topic_on_existing(self):
        """Operador no puede cambiar main_topic_id en un expediente existente — guard bloquea."""
        topic = self.env.ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        if not topic:
            topic = self.env['tmc.document_topic'].create({'name': 'Topic Block Test'})
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_user).write({'main_topic_id': topic.id})

    def test_manager_can_edit_main_topic_on_existing(self):
        """Manager puede cambiar main_topic_id en un expediente existente."""
        topic = self.env.ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        if not topic:
            topic = self.env['tmc.document_topic'].create({'name': 'Topic Manager Test'})
        self.expediente.with_user(self.manager_user).write({'main_topic_id': topic.id})
        self.expediente.invalidate_recordset(['main_topic_id', 'main_topic_ids'])
        self.assertEqual(self.expediente.main_topic_id.id, topic.id)

    def test_clear_main_topic_id_does_not_raise(self):
        """Clearing main_topic_id writes (6,0,[]) to tmc.document — not (5,0,0).

        (5,0,0)[2] = int 0 → set(0) → TypeError in tmc.document.write().
        (6,0,[])[2] = [] → set([]) = set() → no error.
        """
        topic = self.env.ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        if not topic:
            topic = self.env['tmc.document_topic'].create({'name': 'Clear Main Topic Test'})
        self.expediente.with_user(self.manager_user).write({'main_topic_id': topic.id})
        self.expediente.with_user(self.manager_user).write({'main_topic_id': False})
        self.expediente.invalidate_recordset(['main_topic_id', 'main_topic_ids'])
        self.assertFalse(self.expediente.main_topic_id)

    def test_clear_secondary_topic_id_does_not_raise(self):
        """Clearing secondary_topic_id writes (6,0,[]) to tmc.document — not (5,0,0)."""
        parent_topic = self.env.ref('tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False)
        if not parent_topic:
            parent_topic = self.env['tmc.document_topic'].create({'name': 'Clear Secondary Parent'})
        child_topic = self.env['tmc.document_topic'].search(
            [('parent_id', '=', parent_topic.id)], limit=1
        )
        if not child_topic:
            child_topic = self.env['tmc.document_topic'].create({
                'name': 'Clear Secondary Child', 'parent_id': parent_topic.id,
            })
        self.expediente.with_user(self.manager_user).write({
            'main_topic_id': parent_topic.id,
            'secondary_topic_id': child_topic.id,
        })
        self.expediente.with_user(self.manager_user).write({'secondary_topic_id': False})
        self.expediente.invalidate_recordset(['secondary_topic_id', 'secondary_topic_ids'])
        self.assertFalse(self.expediente.secondary_topic_id)

    def test_manager_can_create_and_edit_without_tmc_manual_assignment(self):
        """me.group_manager puede crear y editar sin asignación manual de tmc.group_manager.

        implied_ids en me.group_manager incluye tmc.group_manager, que otorga
        perm_write en tmc.document (necesario para campos delegados via _inherits).
        """
        new_exp = self.env['me.document_exp'].with_user(self.manager_user).create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 88881,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 2,
        })
        # Editar un campo delegado (tmc.document) — requiere tmc.group_manager via implied_ids
        new_exp.with_user(self.manager_user).write({'document_object': 'Test objeto'})
        self.assertEqual(new_exp.document_object, 'Test objeto')


@tagged('post_install', '-at_install')
class TestJurisdictionConditional012(TransactionCase):
    """Tests para #012 — Comportamiento condicional de jurisdicción y repartición.

    Cubre:
    - allowed_jurisdiction_ids: retorna las ~21 jurisdicciones madre del nomenclador
    - Regla 1 TMC: auto-asignación de jurisdiction_dependence = TMC
    - Regla 2 CM: auto-asignación interna CM, movimiento CM→TMC generado
    - Regla 3 domain: DEM sin jurisdiction_dependence falla (required=True)
    - onchange: comportamiento de _onchange_dependence para TMC y DEM
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Departamento Ejecutivo Test',
                'abbreviation': 'DEM',
            })

        self.dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        if not self.dep_tmc:
            self.dep_tmc = self.env['tmc.dependence'].create({
                'name': 'TMC Test',
                'abbreviation': 'TMC',
            })

        self.dep_cm = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'CM')], limit=1
        )
        if not self.dep_cm:
            self.dep_cm = self.env['tmc.dependence'].create({
                'name': 'Concejo Municipal Test',
                'abbreviation': 'CM',
            })

        self.dep_mesa = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'ME')], limit=1
        )
        if not self.dep_mesa:
            self.dep_mesa = self.env['tmc.dependence'].create({
                'name': 'Mesa de Entradas Test',
                'abbreviation': 'ME',
            })

        # Jurisdicción de prueba aislada (no es hijo de ADM → no aparece en allowed_jurisdiction_ids)
        self.dep_jur_test = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion 012 Test',
            'abbreviation': 'J012',
        })

        self.current_year = str(fields.Date.today().year)
        self.today = fields.Date.today()

    def _make_vals(self, number, dep_id, **extra):
        vals = {
            'dependence_id': dep_id,
            'document_type_id': self.doc_type_exp.id,
            'number': number,
            'period': self.current_year,
            'intake_date': self.today,
            'date': self.today,
        }
        vals.update(extra)
        return vals

    def test_allowed_jurisdiction_ids_includes_major_bodies(self):
        """allowed_jurisdiction_ids retorna las ~21 jurisdicciones madre del nomenclador.
        Requiere tmc_data: incluye secretarías además de DEM/TMC/CM."""
        record = self.env['me.document_exp'].new({})
        jur_ids = record.allowed_jurisdiction_ids
        abbrs = jur_ids.mapped('abbreviation')
        self.assertIn('DEM', abbrs)
        self.assertIn('TMC', abbrs)
        self.assertIn('CM', abbrs)
        # Should include more than just DEM/TMC/CM (Secretarías, etc.)
        self.assertGreater(len(jur_ids), 3)

    def test_create_tmc_auto_assigns_jurisdiction(self):
        """create() con dependence_id=TMC sin jurisdiction_dependence
        auto-asigna jurisdiction_dependence = TMC record."""
        exp = self.env['me.document_exp'].create(
            self._make_vals(55552, self.dep_tmc.id)
        )
        self.assertEqual(exp.jurisdiction_dependence, self.dep_tmc)

    def test_create_cm_auto_assigns_jurisdiction(self):
        """create() con dependence_id=CM sin jurisdiction_dependence
        auto-asigna jurisdiction_dependence = CM record."""
        exp = self.env['me.document_exp'].create(
            self._make_vals(55553, self.dep_cm.id)
        )
        self.assertEqual(exp.jurisdiction_dependence, self.dep_cm)

    def test_create_cm_generates_cm_tmc_and_tmc_me_movements(self):
        """Expediente CM genera 2 movimientos: CM→TMC y TMC→ME."""
        exp = self.env['me.document_exp'].create(
            self._make_vals(55554, self.dep_cm.id)
        )
        movements = exp.document_movement_ids
        self.assertEqual(len(movements), 2)
        origins = movements.mapped('origin_dependence_id')
        destinations = movements.mapped('destination_dependence_id')
        self.assertIn(self.dep_cm, origins)
        self.assertIn(self.dep_tmc, destinations)
        self.assertIn(self.dep_tmc, origins)
        self.assertIn(self.dep_mesa, destinations)

    def test_create_dem_without_jurisdiction_raises(self):
        """create() con dependence_id=DEM sin jurisdiction_dependence falla
        (DEM no es auto-asignado, required=True activo)."""
        with self.assertRaises(Exception):
            self.env['me.document_exp'].create(
                self._make_vals(55555, self.dep_dem.id)
            )

    def test_create_dem_with_jurisdiction_succeeds(self):
        """create() con dependence_id=DEM y jurisdiction_dependence explícito no falla."""
        exp = self.env['me.document_exp'].create(
            self._make_vals(55556, self.dep_dem.id,
                            jurisdiction_dependence=self.dep_jur_test.id)
        )
        self.assertEqual(exp.jurisdiction_dependence, self.dep_jur_test)

    def test_onchange_dependence_tmc_sets_jurisdiction(self):
        """_onchange_dependence con TMC auto-completa jurisdiction_dependence = TMC."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_tmc.id,
        })
        record._onchange_dependence()
        self.assertEqual(record.jurisdiction_dependence, self.dep_tmc)

    def test_onchange_dependence_tmc_to_dem_clears_jurisdiction(self):
        """Cambiar dependence_id de TMC a DEM limpia jurisdiction_dependence."""
        record = self.env['me.document_exp'].new({
            'dependence_id': self.dep_tmc.id,
            'jurisdiction_dependence': self.dep_tmc.id,
        })
        record.dependence_id = self.dep_dem
        record._onchange_dependence()
        self.assertFalse(record.jurisdiction_dependence)


@tagged('post_install', '-at_install')
class TestHasReentry021(TransactionCase):
    """Tests para #021 — Detección de reingreso institucional.

    Verifica:
    - Expediente sin salidas → has_reentry = False
    - Expediente con salida pero sin reingreso → has_reentry = False
    - Expediente con salida y reingreso posterior → has_reentry = True
    - Solo movimientos automáticos (todos a destinos internos) → has_reentry = False
    - Secuencia interno → externo → externo → interno → has_reentry = True
    - Cambiar is_internal de una dependencia recalcula has_reentry
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test',
                'abbreviation': 'DEM',
            })

        # Dependencia interna de test (is_internal=True explícito)
        self.dep_int = self.env['tmc.dependence'].create({
            'name': 'Dependencia Interna 021 Test',
            'abbreviation': 'INT021',
            'is_internal': True,
        })

        # Dependencia externa de test (is_internal=False, el default)
        self.dep_ext = self.env['tmc.dependence'].create({
            'name': 'Dependencia Externa 021 Test',
            'abbreviation': 'EXT021',
            'is_internal': False,
        })

        # Jurisdicción aislada: no tiene hijos en el nomenclador,
        # evita disparar _check_source_dependence_required.
        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion 021 Test',
            'abbreviation': 'J021',
        })

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.current_year = str(self.today.year)

    def _make_expediente(self, number):
        return self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': number,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
        })

    def _add_movement(self, exp, origin, destination):
        return self.env['me.document_movement'].create({
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': origin.id,
            'destination_dependence_id': destination.id,
        })

    def test_no_movements_has_no_reentry(self):
        """Expediente sin movimientos: has_reentry = False."""
        exp = self._make_expediente(33001)
        exp.document_movement_ids.unlink()
        self.assertFalse(exp.has_reentry)

    def test_only_internal_movements_no_reentry(self):
        """Solo movimientos automáticos (destinos internos): has_reentry = False.

        Los movimientos automáticos apuntan a TMC y ME, ambos internos.
        No hay salida institucional → no puede haber reingreso.
        """
        exp = self._make_expediente(33002)
        # Forzar todos los destinos como internos para que el test sea determinístico
        # independientemente de si tmc_data está cargado.
        for mov in exp.document_movement_ids:
            mov.destination_dependence_id.is_internal = True
        self.assertFalse(exp.has_reentry)

    def test_exit_without_reentry_is_false(self):
        """Salida a dependencia externa sin reingreso posterior: has_reentry = False."""
        exp = self._make_expediente(33003)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_int, self.dep_ext)  # salida
        self.assertFalse(exp.has_reentry)

    def test_exit_followed_by_reentry_is_true(self):
        """Salida a externa seguida de movimiento a interna: has_reentry = True."""
        exp = self._make_expediente(33004)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_int, self.dep_ext)  # salida
        self._add_movement(exp, self.dep_ext, self.dep_int)  # reingreso
        self.assertTrue(exp.has_reentry)

    def test_internal_before_exit_does_not_count(self):
        """Movimientos internos previos a una salida no cuentan como reingreso."""
        exp = self._make_expediente(33005)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_ext, self.dep_int)  # interno (sin salida previa)
        self._add_movement(exp, self.dep_int, self.dep_ext)  # salida
        # Todavía sin reingreso posterior
        self.assertFalse(exp.has_reentry)

    def test_multiple_exits_then_reentry_is_true(self):
        """Salida → salida → salida → reingreso: has_reentry = True."""
        exp = self._make_expediente(33006)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_int, self.dep_ext)  # salida 1
        self._add_movement(exp, self.dep_ext, self.dep_ext)  # salida 2 (externo→externo)
        self._add_movement(exp, self.dep_ext, self.dep_int)  # reingreso
        self.assertTrue(exp.has_reentry)

    def test_is_internal_change_triggers_recompute(self):
        """Cambiar is_internal de una dependencia recalcula has_reentry."""
        exp = self._make_expediente(33007)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_int, self.dep_ext)  # salida
        self._add_movement(exp, self.dep_ext, self.dep_int)  # reingreso
        self.assertTrue(exp.has_reentry)

        # Marcar dep_ext como interna: ya no hay salida → has_reentry debe ser False
        self.dep_ext.is_internal = True
        exp.invalidate_recordset(['has_reentry'])
        exp._compute_has_reentry()
        self.assertFalse(exp.has_reentry)


@tagged('post_install', '-at_install')
class TestSearchFilters022023024(TransactionCase):
    """Tests para #022, #023, #024 — Filtros de búsqueda.

    #022 — is_currently_internal:
      Verdadero cuando el último movimiento (por id) tiene destino interno.

    #023 — is_licitacion:
      Verdadero cuando main_topic_ids contiene el tema Licitación.

    #024 — Filtro por origen TMC:
      Domain directo sobre dependence_id.abbreviation == 'TMC'.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'DEM Test',
                'abbreviation': 'DEM',
            })

        self.dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        if not self.dep_tmc:
            self.dep_tmc = self.env['tmc.dependence'].create({
                'name': 'TMC Test',
                'abbreviation': 'TMC',
            })

        # Dependencias internas y externas aisladas para tests de is_currently_internal.
        # Se crean siempre nuevas para evitar colisión con datos reales o de otros tests.
        self.dep_int = self.env['tmc.dependence'].create({
            'name': 'Dependencia Interna 022 Test',
            'abbreviation': 'INT022',
            'is_internal': True,
        })
        self.dep_ext = self.env['tmc.dependence'].create({
            'name': 'Dependencia Externa 022 Test',
            'abbreviation': 'EXT022',
            'is_internal': False,
        })

        # Jurisdicción aislada: sin hijos en nomenclador, evita constraint source_dependence.
        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion 022 Test',
            'abbreviation': 'J022',
        })

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.current_year = str(self.today.year)

    def _make_expediente(self, number, dependence=None):
        dep = dependence or self.dep_dem
        return self.env['me.document_exp'].create({
            'dependence_id': dep.id,
            'document_type_id': self.doc_type_exp.id,
            'number': number,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
        })

    def _add_movement(self, exp, origin, destination):
        return self.env['me.document_movement'].create({
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': origin.id,
            'destination_dependence_id': destination.id,
        })

    # ------------------------------------------------------------------
    # #022 — is_currently_internal
    # ------------------------------------------------------------------

    def test_no_movements_is_not_currently_internal(self):
        """Sin movimientos: is_currently_internal = False."""
        exp = self._make_expediente(34001)
        exp.document_movement_ids.unlink()
        self.assertFalse(exp.is_currently_internal)

    def test_last_movement_to_internal_is_true(self):
        """Último movimiento con destino interno: is_currently_internal = True."""
        exp = self._make_expediente(34002)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_int, self.dep_ext)   # externo
        self._add_movement(exp, self.dep_ext, self.dep_int)   # interno — es el último
        self.assertTrue(exp.is_currently_internal)

    def test_last_movement_to_external_is_false(self):
        """Último movimiento con destino externo: is_currently_internal = False."""
        exp = self._make_expediente(34003)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_ext, self.dep_int)   # interno
        self._add_movement(exp, self.dep_int, self.dep_ext)   # externo — es el último
        self.assertFalse(exp.is_currently_internal)

    def test_only_automatic_movements_last_destination_internal(self):
        """Movimientos automáticos apuntan a ME (interno): is_currently_internal = True
        cuando is_internal de la dependencia destino del último movimiento es True."""
        exp = self._make_expediente(34004)
        # Forzar último movimiento automático con destino interno
        last_auto = exp.document_movement_ids.sorted('id')[-1:]
        if last_auto:
            last_auto.destination_dependence_id.is_internal = True
        self.assertTrue(exp.is_currently_internal)

    def test_is_currently_internal_updates_on_new_movement(self):
        """Al agregar un nuevo movimiento se actualiza is_currently_internal."""
        exp = self._make_expediente(34005)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_int, self.dep_int)   # interno
        self.assertTrue(exp.is_currently_internal)

        self._add_movement(exp, self.dep_int, self.dep_ext)   # externo — nuevo último
        self.assertFalse(exp.is_currently_internal)

    # ------------------------------------------------------------------
    # #023 — is_licitacion
    # ------------------------------------------------------------------

    def test_no_topic_is_not_licitacion(self):
        """Sin tema asignado: is_licitacion = False."""
        exp = self._make_expediente(34010)
        self.assertFalse(exp.is_licitacion)

    def test_licitacion_topic_sets_is_licitacion(self):
        """Tema principal = Licitación: is_licitacion = True."""
        licitacion = self.env.ref(
            'tmc_data.tmc_document_topic_licitacion', raise_if_not_found=False
        )
        if not licitacion:
            self.skipTest('tmc_data.tmc_document_topic_licitacion not found')
        exp = self._make_expediente(34011)
        exp.main_topic_ids = [(6, 0, [licitacion.id])]
        self.assertTrue(exp.is_licitacion)

    def test_other_topic_is_not_licitacion(self):
        """Tema distinto de Licitación: is_licitacion = False."""
        nota = self.env.ref(
            'tmc_data.tmc_document_topic_nota', raise_if_not_found=False
        )
        if not nota:
            self.skipTest('tmc_data.tmc_document_topic_nota not found')
        exp = self._make_expediente(34012)
        exp.main_topic_ids = [(6, 0, [nota.id])]
        self.assertFalse(exp.is_licitacion)

    # ------------------------------------------------------------------
    # #024 — Filtro por origen TMC
    # ------------------------------------------------------------------

    def test_origin_tmc_appears_in_tmc_filter(self):
        """Expediente originado en TMC aparece al filtrar por dependence_id.abbreviation='TMC'."""
        # TMC auto-asigna jurisdiction_dependence = TMC (backup en create)
        exp_tmc = self.env['me.document_exp'].create({
            'dependence_id': self.dep_tmc.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 34020,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_tmc.id,
            'intake_date': self.today,
            'date': self.today,
        })
        result = self.env['me.document_exp'].search([
            ('dependence_id.abbreviation', '=', 'TMC'),
            ('id', '=', exp_tmc.id),
        ])
        self.assertEqual(result, exp_tmc)

    def test_origin_dem_excluded_from_tmc_filter(self):
        """Expediente originado en DEM no aparece en el filtro por origen TMC."""
        exp_dem = self._make_expediente(34021, dependence=self.dep_dem)
        result = self.env['me.document_exp'].search([
            ('dependence_id.abbreviation', '=', 'TMC'),
            ('id', '=', exp_dem.id),
        ])
        self.assertFalse(result)

    def test_tmc_filter_does_not_confuse_current_location_with_origin(self):
        """Un expediente de DEM que terminó en una dependencia TMC-interna
        NO aparece en el filtro de origen TMC."""
        exp_dem = self._make_expediente(34022, dependence=self.dep_dem)
        exp_dem.document_movement_ids.unlink()
        self._add_movement(exp_dem, self.dep_ext, self.dep_int)  # destino interno
        # is_currently_internal = True, pero origin = DEM → no debe aparecer en filtro TMC
        self.assertTrue(exp_dem.is_currently_internal)
        result = self.env['me.document_exp'].search([
            ('dependence_id.abbreviation', '=', 'TMC'),
            ('id', '=', exp_dem.id),
        ])
        self.assertFalse(result)


@tagged('post_install', '-at_install')
class TestArchivoDependence025(TransactionCase):
    """Tests para #025 — Archivo del TMC como destino de movimiento.

    Verifica:
    - La dependencia ARCH existe en el nomenclador con nombre "Archivo".
    - ARCH tiene is_internal=True.
    - ARCH aparece en tmc.dependence_order con código 1.13.91 y parent=TMC.
    - ARCH es seleccionable como destino de un movimiento estándar.
    - Movimiento a ARCH sin salida previa no genera has_reentry=True.
    - Salida a externo seguida de movimiento a ARCH sí genera has_reentry=True.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'DEM Test',
                'abbreviation': 'DEM',
            })

        self.dep_arch = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'ARCH')], limit=1
        )

        self.dep_ext = self.env['tmc.dependence'].create({
            'name': 'Dependencia Externa 025 Test',
            'abbreviation': 'EXT025',
            'is_internal': False,
        })

        # Jurisdicción aislada: sin hijos en nomenclador, evita constraint source_dependence.
        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion 025 Test',
            'abbreviation': 'J025',
        })

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.current_year = str(self.today.year)

    def _make_expediente(self, number):
        return self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': number,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
        })

    def _add_movement(self, exp, origin, destination):
        return self.env['me.document_movement'].create({
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': origin.id,
            'destination_dependence_id': destination.id,
        })

    def test_archivo_dependence_exists(self):
        """La dependencia ARCH existe con nombre 'Archivo'."""
        self.assertTrue(self.dep_arch, "La dependencia ARCH debe existir en el nomenclador")
        self.assertEqual(self.dep_arch.name, 'Archivo')

    def test_archivo_is_internal(self):
        """ARCH tiene is_internal=True."""
        self.assertTrue(self.dep_arch, "La dependencia ARCH debe existir")
        self.assertTrue(self.dep_arch.is_internal)

    def test_archivo_is_child_of_tmc_in_nomenclator(self):
        """ARCH aparece en tmc.dependence_order con código 1.13.91 y parent=TMC."""
        self.assertTrue(self.dep_arch, "La dependencia ARCH debe existir")
        dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        order = self.env['tmc.dependence_order'].search([
            ('dependence_id', '=', self.dep_arch.id),
        ], limit=1)
        self.assertTrue(order, "ARCH debe tener entrada en tmc.dependence_order")
        self.assertEqual(order.code, '1.13.91')
        self.assertEqual(order.parent_id, dep_tmc)

    def test_archivo_selectable_as_movement_destination(self):
        """Se puede crear un movimiento con ARCH como destino."""
        self.assertTrue(self.dep_arch, "La dependencia ARCH debe existir")
        exp = self._make_expediente(35001)
        exp.document_movement_ids.unlink()
        mov = self._add_movement(exp, self.dep_dem, self.dep_arch)
        self.assertEqual(mov.destination_dependence_id, self.dep_arch)

    def test_movement_to_archivo_does_not_generate_reentry(self):
        """Movimiento directo a ARCH sin salida previa: has_reentry = False."""
        self.assertTrue(self.dep_arch, "La dependencia ARCH debe existir")
        exp = self._make_expediente(35002)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_dem, self.dep_arch)
        self.assertFalse(exp.has_reentry)

    def test_exit_then_archivo_is_reentry(self):
        """Salida a externo seguida de movimiento a ARCH: has_reentry = True."""
        self.assertTrue(self.dep_arch, "La dependencia ARCH debe existir")
        exp = self._make_expediente(35003)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_dem, self.dep_ext)   # salida a externo
        self._add_movement(exp, self.dep_ext, self.dep_arch)  # reingreso vía ARCH
        self.assertTrue(exp.has_reentry)


@tagged('post_install', '-at_install')
class TestLegajoDependence026(TransactionCase):
    """Tests para #026 — Movimiento a Legajo: destino y número de legajo.

    Verifica:
    - La dependencia LEG existe con nombre 'Adjunto a Legajo'.
    - LEG tiene is_internal=True.
    - LEG aparece en tmc.dependence_order con código 1.13.92 y parent=TMC.
    - Crear un movimiento con destino LEG sin legajo_number lanza ValidationError.
    - Crear un movimiento con destino LEG con legajo_number funciona correctamente.
    - Crear un movimiento con destino distinto de LEG no requiere legajo_number.
    - Movimiento a LEG sin salida previa no genera has_reentry=True.
    - Salida a externo seguida de movimiento a LEG genera has_reentry=True.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'DEM Test',
                'abbreviation': 'DEM',
            })

        self.dep_leg = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'LEG')], limit=1
        )

        self.dep_ext = self.env['tmc.dependence'].create({
            'name': 'Dependencia Externa 026 Test',
            'abbreviation': 'EXT026',
            'is_internal': False,
        })

        self.dep_int = self.env['tmc.dependence'].create({
            'name': 'Dependencia Interna 026 Test',
            'abbreviation': 'INT026',
            'is_internal': True,
        })

        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion 026 Test',
            'abbreviation': 'J026',
        })

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.current_year = str(self.today.year)

    def _make_expediente(self, number):
        return self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': number,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
        })

    def _add_movement(self, exp, origin, destination, legajo_number=None):
        vals = {
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': origin.id,
            'destination_dependence_id': destination.id,
        }
        if legajo_number is not None:
            vals['legajo_number'] = legajo_number
        return self.env['me.document_movement'].create(vals)

    def test_leg_dependence_exists(self):
        """La dependencia LEG existe con nombre 'Adjunto a Legajo'."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir en el nomenclador")
        self.assertEqual(self.dep_leg.name, 'Adjunto a Legajo')

    def test_leg_is_internal(self):
        """LEG tiene is_internal=True."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        self.assertTrue(self.dep_leg.is_internal)

    def test_leg_is_child_of_tmc_in_nomenclator(self):
        """LEG aparece en tmc.dependence_order con código 1.13.92 y parent=TMC."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        order = self.env['tmc.dependence_order'].search([
            ('dependence_id', '=', self.dep_leg.id),
        ], limit=1)
        self.assertTrue(order, "LEG debe tener entrada en tmc.dependence_order")
        self.assertEqual(order.code, '1.13.92')
        self.assertEqual(order.parent_id, dep_tmc)

    def test_movement_to_leg_without_legajo_number_raises(self):
        """Movimiento a LEG sin legajo_number lanza ValidationError."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        exp = self._make_expediente(36001)
        exp.document_movement_ids.unlink()
        with self.assertRaises(ValidationError):
            self._add_movement(exp, self.dep_dem, self.dep_leg)

    def test_movement_to_leg_with_legajo_number_succeeds(self):
        """Movimiento a LEG con legajo_number guardado correctamente."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        exp = self._make_expediente(36002)
        exp.document_movement_ids.unlink()
        mov = self._add_movement(exp, self.dep_dem, self.dep_leg, legajo_number='LEG-2025-001')
        self.assertEqual(mov.legajo_number, 'LEG-2025-001')
        self.assertEqual(mov.destination_dependence_id, self.dep_leg)

    def test_movement_to_other_destination_does_not_require_legajo_number(self):
        """Movimiento a destino distinto de LEG no requiere legajo_number."""
        exp = self._make_expediente(36003)
        exp.document_movement_ids.unlink()
        mov = self._add_movement(exp, self.dep_dem, self.dep_int)
        self.assertFalse(mov.legajo_number)

    def test_movement_to_leg_does_not_generate_reentry(self):
        """Movimiento directo a LEG sin salida previa: has_reentry = False."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        exp = self._make_expediente(36004)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_dem, self.dep_leg, legajo_number='123')
        self.assertFalse(exp.has_reentry)

    def test_exit_then_leg_is_reentry(self):
        """Salida a externo seguida de movimiento a LEG: has_reentry = True."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        exp = self._make_expediente(36005)
        exp.document_movement_ids.unlink()
        self._add_movement(exp, self.dep_dem, self.dep_ext)
        self._add_movement(exp, self.dep_ext, self.dep_leg, legajo_number='456')
        self.assertTrue(exp.has_reentry)

    def test_destination_abbreviation_computed_on_movement(self):
        """destination_abbreviation devuelve la abreviación del destino del movimiento."""
        self.assertTrue(self.dep_leg, "La dependencia LEG debe existir")
        exp = self._make_expediente(36006)
        exp.document_movement_ids.unlink()
        mov = self._add_movement(exp, self.dep_dem, self.dep_leg, legajo_number='789')
        self.assertEqual(mov.destination_abbreviation, 'LEG')


@tagged('post_install', '-at_install')
class TestMovementDefaultGet(TransactionCase):
    """Tests para default_get de me.document_movement.

    Verifica la pre-carga de fojas y origin_dependence_id al crear
    un nuevo movimiento. La fuente correcta para fojas es el último
    movimiento persistido (snapshot chain), no expediente.fojas.
    """

    def setUp(self):
        super().setUp()

        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test',
                'abbreviation': 'EXP',
            })

        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'DEM Test',
                'abbreviation': 'DEM',
            })

        self.dep_a = self.env['tmc.dependence'].create({
            'name': 'Dep A DefaultGet Test',
            'abbreviation': 'DA_DG',
        })
        self.dep_b = self.env['tmc.dependence'].create({
            'name': 'Dep B DefaultGet Test',
            'abbreviation': 'DB_DG',
        })

        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion DefaultGet Test',
            'abbreviation': 'J_DG',
        })

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.current_year = str(self.today.year)

        self.expediente = self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 37001,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 5,
        })

    def _call_default_get(self, expediente_id):
        """Llama a default_get simulando el contexto del popup del One2many."""
        Movement = self.env['me.document_movement'].with_context(
            default_expediente_id=expediente_id
        )
        return Movement.default_get([
            'expediente_id', 'date', 'origin_dependence_id',
            'destination_dependence_id', 'fojas', 'user_id',
            'is_automatic', 'legajo_number',
        ])

    def test_fojas_preloaded_from_last_movement_not_expediente(self):
        """fojas se pre-carga desde el último movimiento, no desde expediente.fojas.

        Regresión: default_get leía expediente.fojas (valor original de alta)
        en lugar del fojas del último movimiento persistido.
        """
        # expediente.fojas = 5 (valor de creación)
        self.assertEqual(self.expediente.fojas, 5)

        # Creamos un movimiento manual con fojas=30 (snapshot corregido)
        self.expediente.document_movement_ids.unlink()
        self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_a.id,
            'fojas': 30,
        })

        defaults = self._call_default_get(self.expediente.id)

        # Debe pre-cargar 30 (último movimiento), no 5 (expediente.fojas)
        self.assertEqual(
            defaults.get('fojas'), 30,
            "fojas debe pre-cargarse desde el último movimiento, no desde expediente.fojas"
        )

    def test_fojas_zero_when_no_movements(self):
        """Sin movimientos previos, fojas se pre-carga como 0."""
        self.expediente.document_movement_ids.unlink()
        defaults = self._call_default_get(self.expediente.id)
        self.assertEqual(defaults.get('fojas'), 0)

    def test_origin_preloaded_from_last_movement_destination(self):
        """origin_dependence_id se pre-carga con el destino del último movimiento."""
        self.expediente.document_movement_ids.unlink()
        self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_b.id,
            'fojas': 10,
        })

        defaults = self._call_default_get(self.expediente.id)

        self.assertEqual(
            defaults.get('origin_dependence_id'), self.dep_b.id,
            "origin_dependence_id debe pre-cargarse con el destino del último movimiento"
        )

    def test_fojas_and_origin_use_same_last_movement(self):
        """fojas y origin_dependence_id provienen del mismo último movimiento."""
        self.expediente.document_movement_ids.unlink()
        # Primer movimiento
        self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_a.id,
            'fojas': 10,
        })
        # Segundo movimiento (el último): fojas=25, destino=dep_b
        self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_a.id,
            'destination_dependence_id': self.dep_b.id,
            'fojas': 25,
        })

        defaults = self._call_default_get(self.expediente.id)

        self.assertEqual(defaults.get('fojas'), 25)
        self.assertEqual(defaults.get('origin_dependence_id'), self.dep_b.id)


@tagged('post_install', '-at_install')
class TestMovementPoseedor027(TransactionCase):
    """Tests para #027 — solo el poseedor puede registrar nuevos pases desde UI.

    El poseedor actual = user_id del movimiento con mayor id del expediente.
    El guard de write() en me.document_exp distingue comandos O2M CREATE de
    otros writes, y para CREATE verifica que el usuario sea el poseedor.
    """

    def setUp(self):
        super().setUp()
        self.doc_type_exp = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1
        )
        if not self.doc_type_exp:
            self.doc_type_exp = self.env['tmc.document_type'].create({
                'name': 'Expediente Test 027', 'abbreviation': 'EXP',
            })
        self.dep_dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1
        )
        if not self.dep_dem:
            self.dep_dem = self.env['tmc.dependence'].create({
                'name': 'Dependencia DEM Test 027', 'abbreviation': 'DEM',
            })
        self.dep_me = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'ME')], limit=1
        )
        if not self.dep_me:
            self.dep_me = self.dep_dem
        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Test 027', 'abbreviation': 'JT027',
        })
        self.today = fields.Date.today()
        self.current_year = str(self.today.year)

        self.manager_user = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Manager 027', 'login': 'manager_027@test.com',
            'group_ids': [(6, 0, [self.env.ref('me.group_manager').id])],
        })
        self.operator_a = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Operador A 027', 'login': 'operator_a_027@test.com',
            'group_ids': [(6, 0, [self.env.ref('me.group_user').id])],
        })
        self.operator_b = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Operador B 027', 'login': 'operator_b_027@test.com',
            'group_ids': [(6, 0, [self.env.ref('me.group_user').id])],
        })

        # Expediente creado por operator_a → operator_a es el poseedor inicial
        self.expediente = self.env['me.document_exp'].with_user(self.operator_a).create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 88801,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': 1,
        })

    def _movement_cmd(self):
        return (0, 0, {
            'date': fields.Datetime.now(),
            'origin_dependence_id': self.dep_me.id,
            'destination_dependence_id': self.dep_dem.id,
            'fojas': 1,
        })

    def test_poseedor_can_add_movement_via_o2m_write(self):
        """Escenario 1: operador poseedor puede agregar un nuevo pase vía O2M write."""
        count_before = len(self.expediente.document_movement_ids)
        self.expediente.with_user(self.operator_a).write({
            'document_movement_ids': [self._movement_cmd()],
        })
        self.assertEqual(len(self.expediente.document_movement_ids), count_before + 1)

    def test_non_poseedor_cannot_add_movement_via_o2m_write(self):
        """Escenario 2: operador que NO es el poseedor recibe AccessError."""
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_b).write({
                'document_movement_ids': [self._movement_cmd()],
            })

    def test_operator_cannot_update_movement_via_o2m(self):
        """Escenario 4: operador no puede enviar comando UPDATE sobre movimientos existentes."""
        existing_mov = self.expediente.document_movement_ids[:1]
        self.assertTrue(existing_mov)
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_a).write({
                'document_movement_ids': [(1, existing_mov.id, {'fojas': 99})],
            })

    def test_no_movements_any_operator_can_add(self):
        """Escenario 5: sin movimientos, cualquier operador puede agregar el primero."""
        # sudo() needed: self.expediente env is operator_a (no perm_unlink)
        self.expediente.sudo().document_movement_ids.unlink()
        self.assertFalse(self.expediente.document_movement_ids)
        self.expediente.with_user(self.operator_b).write({
            'document_movement_ids': [self._movement_cmd()],
        })
        self.assertTrue(self.expediente.document_movement_ids)

    def test_manager_can_always_add_movement(self):
        """Escenario 6: manager puede agregar movimientos sin ser el poseedor."""
        count_before = len(self.expediente.document_movement_ids)
        self.expediente.with_user(self.manager_user).write({
            'document_movement_ids': [self._movement_cmd()],
        })
        self.assertEqual(len(self.expediente.document_movement_ids), count_before + 1)

    def test_operator_editing_expediente_field_still_blocked(self):
        """Regresión: operador sigue bloqueado al editar campos del expediente."""
        with self.assertRaises(AccessError):
            self.expediente.with_user(self.operator_a).write({'document_object': 'test'})
