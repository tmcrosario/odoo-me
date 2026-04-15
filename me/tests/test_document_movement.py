from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDocumentMovement(TransactionCase):

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

        self.dep_tmc = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'TMC')], limit=1
        )
        if not self.dep_tmc:
            self.dep_tmc = self.env['tmc.dependence'].create({
                'name': 'TMC',
                'abbreviation': 'TMC',
            })

        self.dep_mesa = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'ME')], limit=1
        )
        if not self.dep_mesa:
            self.dep_mesa = self.env['tmc.dependence'].create({
                'name': 'Mesa de Entradas',
                'abbreviation': 'ME',
            })

        self.dep_jur = self.env['tmc.dependence'].search(
            [('name', '=', 'Jurisdiccion MOV Test')], limit=1
        )
        if not self.dep_jur:
            self.dep_jur = self.env['tmc.dependence'].create({
                'name': 'Jurisdiccion MOV Test',
                'abbreviation': 'MOVT',
            })

        self.dep_other = self.env['tmc.dependence'].search(
            [('name', '=', 'Otra Dependencia MOV Test')], limit=1
        )
        if not self.dep_other:
            self.dep_other = self.env['tmc.dependence'].create({
                'name': 'Otra Dependencia MOV Test',
                'abbreviation': 'MOVT2',
            })

        self.current_year = str(fields.Date.today().year)
        self.today = fields.Date.today()
        self.now = fields.Datetime.now()

        self.expediente = self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 88881,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
        })

    def _make_movement(self, **kwargs):
        """Helper: crea un movimiento con valores por defecto sobreescribibles."""
        vals = {
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
        }
        vals.update(kwargs)
        return self.env['me.document_movement'].create(vals)

    def test_movement_without_origin_raises(self):
        """Crear movimiento sin origin_dependence_id lanza error."""
        with self.assertRaises(Exception):
            self.env['me.document_movement'].create({
                'expediente_id': self.expediente.id,
                'date': self.now,
                'destination_dependence_id': self.dep_other.id,
            })

    def test_movement_without_destination_raises(self):
        """Crear movimiento sin destination_dependence_id lanza error."""
        with self.assertRaises(Exception):
            self.env['me.document_movement'].create({
                'expediente_id': self.expediente.id,
                'date': self.now,
                'origin_dependence_id': self.dep_dem.id,
            })

    def test_duplicate_movement_raises(self):
        """Crear dos movimientos idénticos (mismo exp+orig+dest+date) lanza error."""
        fixed_date = fields.Datetime.now()
        self._make_movement(date=fixed_date)
        with self.assertRaises(Exception):
            self._make_movement(date=fixed_date)

    def test_same_path_different_date_does_not_raise(self):
        """Crear dos movimientos mismo exp+orig+dest pero fecha distinta no falla."""
        # Ambas fechas deben ser pasadas (>= intake_date) y distintas entre sí.
        # Usar horas del mismo día para no cruzar la restricción de fecha futura.
        date1 = fields.Datetime.from_string(str(self.today) + ' 08:00:00')
        date2 = fields.Datetime.from_string(str(self.today) + ' 09:00:00')
        self._make_movement(date=date1)
        mov2 = self._make_movement(date=date2)
        self.assertTrue(mov2.id)

    def test_future_date_raises(self):
        """Crear movimiento con date > now() lanza ValidationError."""
        future = fields.Datetime.now() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self._make_movement(date=future)

    def test_date_before_intake_raises(self):
        """Crear movimiento con date.date() < expediente.intake_date lanza ValidationError."""
        before_intake = fields.Datetime.from_string(
            str(self.today - timedelta(days=1)) + ' 00:00:00'
        )
        with self.assertRaises(ValidationError):
            self._make_movement(date=before_intake)

    def test_date_equal_intake_does_not_raise(self):
        """Crear movimiento con date.date() == expediente.intake_date no falla."""
        same_as_intake = fields.Datetime.from_string(
            str(self.today) + ' 00:00:00'
        )
        mov = self._make_movement(date=same_as_intake)
        self.assertTrue(mov.id)

    def test_valid_movement_creates_successfully(self):
        """Crear movimiento con todos los campos válidos no falla."""
        mov = self._make_movement()
        self.assertTrue(mov.id)
        self.assertEqual(mov.expediente_id, self.expediente)
        self.assertEqual(mov.origin_dependence_id, self.dep_dem)
        self.assertEqual(mov.destination_dependence_id, self.dep_other)
