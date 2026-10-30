from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    # dependence_data.xml es noupdate: un -u no marca las bases que ya tenían instalado me.
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in ('tmc_data.tmc_dependence_sec', 'tmc_data.tmc_dependence_cf'):
        dependence = env.ref(xmlid, raise_if_not_found=False)
        if dependence and not dependence.is_internal:
            dependence.is_internal = True
