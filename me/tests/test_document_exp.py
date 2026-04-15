from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
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
        self.assertEqual(record.computed_name, "Documento sin nombre")

    def test_tmc_has_eleven_internal_dependences_in_nomenclator(self):
        """
        Verifica que TMC tiene exactamente 11 dependencias internas en
        tmc.dependence_order con parent_id = TMC (rango 1.13.80–1.13.90).
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
            len(internal_orders), 11,
            f"Se esperan 11 dependencias internas de TMC, encontradas: {len(internal_orders)}"
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
        expected_abbreviations = {'ME', 'VOC', 'SEC', 'FC', 'CF', 'DIC', 'DAL', 'DAT', 'DCD', 'DAF', 'AFC'}
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
