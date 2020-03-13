{
    'name': "TMC RAA Reports",
    'version': '13.0.1.0.1',
    'summary': "Odoo reports for RAA using OCA alternative reporting engine",
    'author': 'Tribunal Municipal de Cuentas - Municipalidad de Rosario',
    'website': 'https://www.tmcrosario.gob.ar',
    'license': 'AGPL-3',
    'depends': [
        'raa',
        'report_py3o',
        'report_py3o_fusion_server'
    ],
    'data': [
        'report/missing_raa.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'qweb': []
}  # yapf: disable
