from odoo.modules.module import get_manifest
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

SCSS_ASSET = 'me/static/src/scss/me_form_save_button.scss'


@tagged('post_install', '-at_install')
class TestSaveButton(TransactionCase):
    """The document_exp form exposes a textual Save (special=save), ported from
    junco:EPIC-008/TASK-004. Pure UI/SCSS: these assert the arch wiring and the
    manifest/asset coupling. The dirty-only VISIBILITY lives in
    me_form_save_button.scss and needs a browser, so it stays a USER-RUN UI check."""

    def test_form_has_textual_save_button(self):
        view = self.env.ref('me.document_exp_view_form')
        arch = view.arch_db or view.arch
        self.assertIn('special="save"', arch, 'el form debe tener el botón Save')
        self.assertIn('btn-outline-primary o_me_form_save_button', arch)
        # outline, never solid: the solid variant would show a permanent blue button.
        self.assertNotIn('btn-primary o_me_form_save_button', arch)

    def test_save_button_scss_is_registered(self):
        # Guards the button<->SCSS coupling: dropping the manifest asset (or the file)
        # would silently un-style the button (permanently visible + empty bar) while the
        # arch test above stays green. Keep this red if the asset is removed.
        backend = get_manifest('me').get('assets', {}).get('web.assets_backend', [])
        self.assertIn(SCSS_ASSET, backend,
                      'el SCSS del botón Save debe estar en web.assets_backend')
