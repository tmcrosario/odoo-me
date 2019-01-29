# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class RegistryAA(models.Model):
    _name = 'raa.registry_aa'

    document_id = fields.Many2one(
        'tmc.document',
        required=True
    )

    entry_date = fields.Date(
        default=fields.Date.context_today,
        required=True
    )

    document_type_id = fields.Many2one(
        related='document_id.document_type_id',
        readonly=True
    )

    dependence_id = fields.Many2one(
        related='document_id.dependence_id',
        readonly=True,
        domain=[('document_type_ids', '!=', False),
                ('system_ids', 'ilike', u'RAA')],
        store=True,
        translate=True
    )

    number = fields.Integer(
        related="document_id.number",
        readonly=True
    )

    period = fields.Integer(
        related='document_id.period',
        readonly=True,
        store=True
    )

    @api.multi
    def name_get(self):
        result = []
        for aa in self:
            document_name = aa.document_id.name_get()[0][1]
            result.append((aa.id, document_name))
        return result

    @api.multi
    def unlink(self):
        for raa_obj in self:
            document_obj = raa_obj.document_id

            if  not document_obj.date and \
                not document_obj.document_object and \
                not document_obj.main_topic_ids and \
                not document_obj.related_document_ids and \
                not document_obj.highlight_ids:

                super(RegistryAA, raa_obj).unlink()
                document_obj.unlink()
            else:
                super(RegistryAA, raa_obj).unlink()

    _sql_constraints = [
        ('document_id_unique',
         'UNIQUE(document_id)',
         _('Record already exists'))
    ]
