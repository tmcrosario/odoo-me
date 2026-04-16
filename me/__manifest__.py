{
    "name": "TMC ME",
    "version": "19.0.1.0.0",
    "summary": "Sistema de Mesa de Entrada",
    "author": "Tribunal Municipal de Cuentas - Municipalidad de Rosario",
    "website": "https://www.tmcrosario.gob.ar",
    "license": "AGPL-3",
    "depends": ["tmc"],
    "data": [
        "security/me_groups.xml",
        "security/ir.model.access.csv",
        "views/movement_views.xml",
        "views/document_exp_views.xml",
        "views/me_menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
}  # yapf: disable
