{
    "name": "TMC RAA",
    "version": "14.0.1.0.1",
    "summary": "Sistema de Registro de Actos Administrativos",
    "author": "Tribunal Municipal de Cuentas - Municipalidad de Rosario",
    "website": "https://www.tmcrosario.gob.ar",
    "license": "AGPL-3",
    "depends": [
        "tmc",
        "tmc_data_py3o",
        "me",
        "report_py3o",
        "report_py3o_fusion_server",
        "popup_message_dialog_box",
    ],
    "data": [
        "security/raa_groups.xml",
        "security/ir.model.access.csv",
        "views/raa_menus.xml",
        "views/registry_aa_views.xml",
        "views/registry_aa_menus.xml",
        "wizards/entry_views.xml",
        "wizards/entry_menu.xml",
        "wizards/number_range_views.xml",
        "wizards/search_missing_views.xml",
        "wizards/search_missing_menu.xml",
        "reports/missing_raa.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "qweb": [],
}  # yapf: disable
