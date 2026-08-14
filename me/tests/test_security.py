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

    # EPIC-015/TASK-004 — la escalera del privilegio ME debe ser ESTRUCTURAL:
    # Read Only < User < Manager. El orden lo fija res_groups.py con la clave
    # (rank, sequence, id), rank = |all_implied_ids ∩ grupos del privilegio|; la cadena
    # real (user implica read_only, manager implica user) da rank 0 < 1 < 2.
    # Este test existe porque el defecto NO lo detectó ninguna suite: lo encontró un
    # humano mirando un dropdown. Si User vuelve a quedar arriba de Read Only, el widget
    # (res_user_group_ids_field.js) borra las opciones de menor nivel y "ME: User"
    # desaparece de la ficha de cualquier usuario con grupos de JUNCO.
    def test_me_privilege_ladder_order(self):
        read_only = self.env.ref('me.group_read_only')
        user = self.env.ref('me.group_user')
        manager = self.env.ref('me.group_manager')
        privilege = user.privilege_id
        self.assertTrue(privilege, "los grupos de ME deben colgar del privilege ME")
        hierarchy = self.env['res.groups']._get_view_group_hierarchy()
        ladder = hierarchy['privileges'][privilege.id]['group_ids']
        self.assertEqual(
            ladder, [read_only.id, user.id, manager.id],
            "la escalera del privilegio ME debe ordenarse Read Only < User < Manager; "
            "si no, el widget borra las opciones de menor nivel y 'ME: User' desaparece "
            "del dropdown (EPIC-015/TASK-004)",
        )
        # el orden debe ser estructural (rank), no sostenido por el desempate por id
        ranks = [
            len(g.all_implied_ids & privilege.group_ids)
            for g in (read_only, user, manager)
        ]
        self.assertEqual(ranks, sorted(set(ranks)),
                         "los ranks deben ser estrictamente crecientes (cadena real), "
                         "no empatados y desempatados por sequence/id")

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

    # Un lector de ME NO puede crear expedientes: el ACL le da create=0 sobre
    # me.document_exp (ir.model.access.csv). El create() se eleva con sudo() para que el
    # _inherits cree el tmc.document padre, y esa elevación saltea el chequeo de ACL del
    # propio me.document_exp (ir.model.access.check corta por env.su), así que create()
    # valida explícitamente contra los permisos del llamador ANTES de elevar.
    def test_me_read_only_cannot_create_expediente(self):
        reader = self.env['res.users'].create({
            'name': 'me_reader', 'login': 'me_reader',
            'group_ids': [(6, 0, [self.env.ref('me.group_read_only').id])],
        })
        with self.assertRaises(AccessError) as cm:
            self.env['me.document_exp'].with_user(reader).create({
                'dependence_id': self.dem.id,
                'document_type_id': self.exp_type.id,
                'number': 900300, 'period': '2026', 'date': '2026-02-10',
                'intake_date': '2026-02-12',
                'document_object': 'Alta como lector ME (debe fallar)',
            })
        # NO SIMPLIFICAR a un assertRaises(AccessError) pelado: pasaría igual SIN el fix.
        # El create elevado saltea el ACL de me.document_exp (ir.model.access.check corta por
        # env.su) y el AccessError llega enmascarado desde me.document_movement, que bloquea
        # de rebote por una coincidencia de la matriz de ACL (ningún grupo tiene create en
        # movimientos sin tenerlo en expedientes), no por la frontera que queremos probar.
        # Assertar el MODELO citado en el mensaje es lo único que discrimina el origen del
        # corte; sin este assert, la regresión vuelve y ninguna suite la ve.
        self.assertIn('me.document_exp', str(cm.exception))

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

    # _update_document_date escribe la fecha de GD con SQL crudo (para escapar la regla
    # año==período de tmc y archivar un documento viejo en un expediente del período
    # actual). El SQL saltea el ORM y, con él, ir.model.access: sin gobierno, un caller
    # sin write sobre tmc.document escribiría la fecha igual. El método re-impone el ACL a
    # mano (check_access('write') sobre document_id) → un lector de GD recibe AccessError.
    # La fecha es válida (no futura, ingreso>=fecha) para que lo ÚNICO que pueda cortar sea
    # el ACL y no una validación previa. Sin el fix este llamado pasaría en silencio.
    def test_gd_read_only_cannot_update_document_date(self):
        with self.assertRaises(AccessError) as cm:
            self.exp.with_user(self.me_user)._update_document_date('2026-02-11')
        # el corte debe venir de tmc.document (la frontera GD), no de otro modelo
        self.assertIn('tmc.document', str(cm.exception))
