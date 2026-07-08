from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


# post_install: crear res.users / expedientes requiere el registry completo.
@tagged('post_install', '-at_install')
class TestMeSecurity(TransactionCase):
    """EPIC-015 (opción 1) — ME edita ME y solo LEE GD (tmc).

    El operativo de ME hereda solo-lectura de GD (ya no editor), sigue creando
    expedientes (el tmc.document padre se crea vía _inherits con el create elevado),
    y NO puede editar/crear tmc.document directamente.
    """

    def setUp(self):
        super().setUp()
        self.me_user = self.env['res.users'].create({
            'name': 'me_op', 'login': 'me_op',
            'group_ids': [(6, 0, [self.env.ref('me.group_user').id])],
        })
        self.dem = self.env['tmc.dependence'].search(
            [('abbreviation', '=', 'DEM')], limit=1)
        self.exp_type = self.env['tmc.document_type'].search(
            [('abbreviation', '=', 'EXP')], limit=1)
        self.assertTrue(self.dem and self.exp_type,
                        "master data del nomenclador requerida")
        # expediente base creado como admin → su tmc.document padre es el target GD
        self.exp = self.env['me.document_exp'].create({
            'dependence_id': self.dem.id,
            'document_type_id': self.exp_type.id,
            'number': 900100, 'period': '2026', 'date': '2026-02-10',
            'intake_date': '2026-02-12',
            'document_object': 'base seguridad',
        })

    # el operativo de ME hereda lectura de GD y es usuario interno, NO editor de GD
    def test_me_user_implies_read_only_gd(self):
        u = self.me_user
        self.assertTrue(u.has_group('base.group_user'))      # usuario interno preservado
        self.assertTrue(u.has_group('tmc.group_read_only'))  # lee GD
        self.assertFalse(u.has_group('tmc.group_user'))      # ya NO es editor de GD

    # REGRESIÓN me:531 — el operativo crea un expediente; el tmc.document padre se
    # crea vía _inherits con el create elevado (sudo), sin ACL de escritura en GD
    def test_me_user_can_create_expediente(self):
        exp = self.env['me.document_exp'].with_user(self.me_user).create({
            'dependence_id': self.dem.id,
            'document_type_id': self.exp_type.id,
            'number': 900001, 'period': '2026', 'date': '2026-02-10',
            'intake_date': '2026-02-12',
            'document_object': 'Alta como operativo ME',
        })
        self.assertTrue(exp.id)
        self.assertTrue(exp.document_id)   # el padre tmc.document quedó creado

    # el operativo LEE el tmc.document (GD) pero NO lo edita ni lo crea directamente
    def test_me_user_reads_gd_cannot_write_or_create(self):
        parent = self.exp.document_id
        parent.with_user(self.me_user).read(['display_name'])       # lee GD OK
        with self.assertRaises(AccessError):
            parent.with_user(self.me_user).write({'date': '2026-01-01'})
        with self.assertRaises(AccessError):
            self.env['tmc.document'].with_user(self.me_user).create({
                'dependence_id': self.dem.id,
                'document_type_id': self.exp_type.id,
                'number': 900200, 'period': '2026',
            })
