# -*- coding: utf-8 -*-

{
    'name': "TMC RAA",
    'version': '10.0.1.0.0',
    'summary': 'Sistema de Registro de Actos Administrativos',
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'website': 'https://www.tmcrosario.gob.ar',
    'license': 'AGPL-3',
    'depends': ['tmc'],
    'data': [
        # 'security/raa_group.xml',
        # 'security/ir.model.access.csv',
        'views/registry_aa.xml',
        'views/wizards.xml',
        # 'report/report_missing_raa.xml',
        'views/menu.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'qweb': [],
}
