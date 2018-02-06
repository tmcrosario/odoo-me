# -*- coding: utf-8 -*-

{
    'name': "TMC RAA",
    'version': '10.0.1.0.0',
    'summary': 'Sistema de Registro de Actos Administrativos',
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'website': 'https://www.tmcrosario.gob.ar',
    'license': 'AGPL-3',
    'sequence': 150,
    'depends': [
        'tmc',
        'report_py3o',
        'report_py3o_fusion_server',
        'web_ir_actions_act_window_message'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/registry_aa.xml',
        'views/wizards.xml',
        'views/menu.xml',
        'report/missing_raa.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'qweb': []
}
