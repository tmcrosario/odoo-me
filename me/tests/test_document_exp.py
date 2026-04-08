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
