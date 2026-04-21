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


@tagged('post_install', '-at_install')
class TestFojasMovimiento(TransactionCase):
    """Tests para #015 — campo fojas en me.document_movement.

    Verifica:
    - snapshot semántico: movimientos automáticos heredan record.fojas de create()
    - is_automatic distingue movimientos automáticos de manuales
    - default=0 cuando fojas no está cargado
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

        # Jurisdicción sin hijos en el nomenclador para no disparar
        # _check_source_dependence_required (#017)
        self.dep_jur = self.env['tmc.dependence'].create({
            'name': 'Jurisdiccion Fojas Test',
            'abbreviation': 'JFOJ',
        })

        self.dep_other = self.env['tmc.dependence'].create({
            'name': 'Otra Dep Fojas Test',
            'abbreviation': 'OFOJ',
        })

        self.current_year = str(fields.Date.today().year)
        self.today = fields.Date.today()
        self.now = fields.Datetime.now()

    def _make_expediente(self, fojas=0, number=77770):
        return self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': number,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
            'fojas': fojas,
        })

    def test_automatic_movements_have_is_automatic_true(self):
        """Los movimientos generados por create() tienen is_automatic == True."""
        exp = self._make_expediente(number=77771)
        for mov in exp.document_movement_ids:
            self.assertTrue(
                mov.is_automatic,
                f"Movimiento {mov.id} debería tener is_automatic=True",
            )

    def test_automatic_movements_snapshot_fojas_nonzero(self):
        """Movimientos automáticos capturan el valor real de fojas=5 del expediente."""
        exp = self._make_expediente(fojas=5, number=77772)
        for mov in exp.document_movement_ids:
            self.assertEqual(
                mov.fojas, 5,
                f"Movimiento {mov.id} debería tener fojas=5 (snapshot)",
            )

    def test_automatic_movements_fojas_zero_when_not_loaded(self):
        """Movimientos automáticos registran fojas=0 cuando el expediente no tiene fojas."""
        exp = self._make_expediente(fojas=0, number=77773)
        for mov in exp.document_movement_ids:
            self.assertEqual(mov.fojas, 0)

    def test_manual_movement_has_is_automatic_false(self):
        """Movimiento creado manualmente tiene is_automatic == False."""
        exp = self._make_expediente(number=77774)
        mov = self.env['me.document_movement'].create({
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
        })
        self.assertFalse(mov.is_automatic)

    def test_manual_movement_fojas_zero_by_default(self):
        """Movimiento manual sin fojas explícito usa default=0."""
        exp = self._make_expediente(fojas=5, number=77775)
        mov = self.env['me.document_movement'].create({
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
        })
        # Sin contexto default_expediente_id, fojas cae al default=0 del campo
        self.assertEqual(mov.fojas, 0)

    def test_manual_movement_fojas_explicit_zero_does_not_raise(self):
        """Movimiento manual con fojas=0 explícito no lanza error."""
        exp = self._make_expediente(number=77776)
        mov = self.env['me.document_movement'].create({
            'expediente_id': exp.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
            'fojas': 0,
        })
        self.assertEqual(mov.fojas, 0)

    def test_default_get_preloads_fojas_from_context(self):
        """default_get() pre-carga fojas desde el expediente cuando está en el contexto."""
        exp = self._make_expediente(fojas=7, number=77777)
        defaults = self.env['me.document_movement'].with_context(
            default_expediente_id=exp.id
        ).default_get(['fojas', 'expediente_id'])
        self.assertEqual(defaults.get('fojas'), 7)


@tagged('post_install', '-at_install')
class TestResponsibleUser011(TransactionCase):
    """Tests para #011 — user_id como responsable operativo en destino.

    Verifica:
    - user_id defaultea al usuario de sesión
    - user_id puede ser distinto al usuario de sesión
    - movimientos automáticos tienen user_id = usuario que creó el expediente
    - create_uid queda asignado al usuario de sesión al crear el movimiento
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
            'name': 'Jurisdiccion Resp Test',
            'abbreviation': 'JRSP',
        })
        self.dep_other = self.env['tmc.dependence'].create({
            'name': 'Otra Dep Resp Test',
            'abbreviation': 'ORSP',
        })

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.current_year = str(fields.Date.today().year)

        self.expediente = self.env['me.document_exp'].create({
            'dependence_id': self.dep_dem.id,
            'document_type_id': self.doc_type_exp.id,
            'number': 99990,
            'period': self.current_year,
            'jurisdiction_dependence': self.dep_jur.id,
            'intake_date': self.today,
            'date': self.today,
        })

    def test_user_id_default_is_session_user(self):
        """Nuevo movimiento manual: user_id defaultea al usuario de sesión."""
        mov = self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
        })
        self.assertEqual(mov.user_id, self.env.user)

    def test_user_id_can_be_different_from_session(self):
        """user_id puede ser un usuario distinto al que cargó el movimiento."""
        other_user = self.env.ref('base.user_demo', raise_if_not_found=False)
        if not other_user:
            other_user = self.env['res.users'].search(
                [('id', '!=', self.env.user.id)], limit=1
            )
        if not other_user:
            self.skipTest("No hay otro usuario disponible para este test")

        mov = self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
            'user_id': other_user.id,
        })
        self.assertEqual(mov.user_id, other_user)

    def test_automatic_movements_have_user_id(self):
        """Movimientos automáticos tienen user_id asignado (usuario de sesión en create)."""
        for mov in self.expediente.document_movement_ids:
            self.assertTrue(
                mov.is_automatic,
                f"Movimiento {mov.id} debería ser automático",
            )
            self.assertTrue(
                mov.user_id,
                f"Movimiento automático {mov.id} debería tener user_id asignado",
            )

    def test_create_uid_set_on_movement_create(self):
        """create_uid queda asignado al usuario de sesión al crear el movimiento."""
        mov = self.env['me.document_movement'].create({
            'expediente_id': self.expediente.id,
            'date': self.now,
            'origin_dependence_id': self.dep_dem.id,
            'destination_dependence_id': self.dep_other.id,
        })
        self.assertEqual(mov.create_uid, self.env.user)
