
from datetime import date
from itertools import count, groupby

from odoo import _, api, fields, models


class EntryWizard(models.TransientModel):

    _name = 'raa.entry.wizard'
    _inherit = ['tmc.report']

    entry_date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )

    period = fields.Integer(
        required=True,
        default=int(date.today().year)
    )

    dependence_id = fields.Many2one(
        comodel_name='tmc.dependence',
        string='Dependence',
        domain=[('document_type_ids', '!=', False),
                ('system_ids', 'ilike', u'RAA')],
        required=True
    )

    document_type_id = fields.Many2one(
        comodel_name='tmc.document_type',
        required=True
    )

    specify_maximum = fields.Boolean()

    maximum = fields.Integer()

    range_ids = fields.One2many(
        comodel_name='raa.range',
        inverse_name='registry_aa_id',
        required=True
    )

    def as_range(self, iterable):
        l = list(iterable)
        if len(l) > 1:
            return '{0} a {1}'.format(l[0], l[-1])
        else:
            return '{0}'.format(l[0])

    @api.multi
    def show_window_message(self):
        res = self.search_missing()
        if res['maximum']:
            if res['missing']:
                missing = ', '.join(
                    self.as_range(g) for _, g in groupby(
                        res['missing'],
                        key=lambda n,
                        c=count(): n - next(c)
                    )
                )
                message = _(
                    '<p>Missing administrative acts: <b>%s</b></p>') % missing
            else:
                message = _('No missing administrative acts')
        else:
            message = _('No existing registries matching criteria')

        return {
            'type': 'ir.actions.act_window.message',
            'title': _('Search Results'),
            'is_html_message': True,
            'message': message,
            'close_button_title': False,
        }

    @api.multi
    def search_missing(self):
        domain = [
            ('document_id.document_type_id', '=', self.document_type_id.id),
            ('document_id.dependence_id', '=', self.dependence_id.id),
            ('document_id.period', '=', self.period)
        ]

        registries = self.env['raa.registry_aa'].search(domain)

        document_numbers = registries.mapped('document_id.number')

        last = None
        maximum = None
        missing = None

        if registries:
            last = maximum = max(document_numbers)
            if self.maximum:
                maximum = self.maximum

            missing = []
            for x in range(1, maximum + 1):
                if x not in document_numbers:
                    missing.append(x)

        return {
            'last': last,
            'maximum': maximum,
            'missing': missing
        }

    @api.multi
    def create_registry_aa(self):
        raa_ids = []

        if not self.range_ids:
            raise Warning(_('No ranges were specified'))

        for aa_range in self.range_ids:
            for number in range(aa_range.number_from, aa_range.number_to + 1):
                doc_model = self.env['tmc.document']
                domain = [
                    ('document_type_id', '=', self.document_type_id.id),
                    ('dependence_id', '=', self.dependence_id.id),
                    ('number', '=', number),
                    ('period', '=', self.period)
                ]
                document = doc_model.search(domain, limit=1)
                if not document:
                    vals = {
                        'document_type_id': self.document_type_id.id,
                        'dependence_id': self.dependence_id.id,
                        'number': number,
                        'period': self.period
                    }
                    document = doc_model.sudo().create(vals)

                raa_model = self.env['raa.registry_aa']
                domain = [('document_id', '=', document.id)]
                raa = raa_model.search(domain, limit=1)
                if not raa:
                    vals = {
                        'entry_date': self.entry_date,
                        'document_id': document.id
                    }
                    raa = raa_model.create(vals)
                    raa_ids.append(raa.id)

        if raa_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': _('The following registries were created'),
                'res_model': 'raa.registry_aa',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', raa_ids)],
                'target': 'new',
                'nodestroy': True,
            }
        else:
            return {
                'type': 'ir.actions.act_window.message',
                'title': _('Information'),
                'message': _('Administrative acts registries already exist')
            }

    @api.multi
    def _prepare_report(self):
        context = self._context.copy()
        res = self.search_missing()
        context['last'] = str(res['last']).zfill(6) if res['last'] else None
        context['maximum'] = str(res['maximum']).zfill(6) if res[
            'maximum'] else None
        context['missing'] = [str(x).zfill(6) for x in res['missing']] if res[
            'missing'] else None
        return self.with_context(context)

    @api.multi
    @api.onchange('dependence_id')
    def _onchange_dependence(self):
        document_types = self.dependence_id.document_type_ids
        if len(document_types.ids) == 1:
            self.document_type_id = document_types.ids[0]
        else:
            self.document_type_id = False
        return {'domain': {
            'document_type_id': [('id', 'in', document_types.ids)]
        }}

    @api.multi
    @api.onchange('specify_maximum')
    def _onchange_specify_maximum(self):
        self.maximum = False

    @api.constrains('maximum')
    def _check_maximum(self):
        if self.maximum > 6000:
            raise Warning(_('Maximum number allowed has been exceeded'))


class Range(models.TransientModel):
    _name = 'raa.range'

    registry_aa_id = fields.Many2one(
        comodel_name='raa.entry.wizard',
        required=True
    )

    number_from = fields.Integer(
        required=True
    )

    number_to = fields.Integer(
        required=True
    )

    @api.multi
    @api.constrains('number_from', 'number_to')
    def _check_ranges(self):
        self.ensure_one()
        if self.number_from > self.number_to:
            raise Warning(
                _('There are values in conflict'))
        elif self.number_from < 1 or self.number_to < 1:
            raise Warning(
                _('You must enter values greater than 0 (zero)'))
        elif self.number_to > 6000:
            raise Warning(
                _('Maximum number allowed has been exceeded'))
        return True
