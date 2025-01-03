from datetime import date

from odoo import _, api, exceptions, fields, models


class RegistryExp(models.Model):
    _name = "me.registry_exp"
    # _inherit = "tmc.document"
    _description = "Expediente Registry"

    # name = fields.Char(compute="_compute_name", store=True)
    # name =  fields.Char(required=True, store=True)

    document_id = fields.Many2one(
        comodel_name="tmc.document",
        required=True,
        # context="{'from_registry_exp': True}" # le doy contexto de expediente
    )

    name = fields.Char(related="document_id.name", string="Nombre documento")

    number = fields.Integer(related="document_id.number")
    period = fields.Integer(related="document_id.period")

    date = fields.Date(related="document_id.date", string="Fecha de inicio de trámite")

    entry_date = fields.Date(
        default=fields.Date.context_today,
        required=True,
        string="Fecha de ingreso al TMC")

    external_key = fields.Char(
        string="Clave Externa",
        help="lo usa la Muni para identificar los expedientes"
    )


    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     # Detecta el contexto para redirigir al wizard
    #     if self.env.context.get('create_wizard'):
    #         action = self.env.ref('me_registry_exp.action_reg_exp_wizard')
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': action.name,
    #             'res_model': action.res_model,
    #             'view_mode': action.view_mode,
    #             'target': action.target,
    #             'views': [(v.view_id.id, v.view_mode) for v in action.view_ids],
    #         }
    #     return super(RegistryExp, self).fields_view_get(view_id, view_type, toolbar, submenu)


    # name = fields.Char(
    #     related="documenti_id.name",
    #     string="Nombre del documento"
    # )
    # entry_date = fields.Date(
    #     related="document_id.entry_date",
    #     string="Fecha de Entrada"
    # )

    # date = fields.Date()

    # document_type_id = fields.Many2one(
    #     comodel_name="tmc.document_type", required=True
    # )

    # document_type_abbr = fields.Char(related="document_type_id.abbreviation")

    # document_type_ids = fields.Many2many(
    #     related="dependence_id.document_type_ids"
    # )

    # dependence_id = fields.Many2one(
    #     comodel_name="tmc.dependence",
    #     domain=[
    #         ("document_type_ids", "!=", False),
    #         ("system_ids", "ilike", "ME"),
    #     ],
    #     required=True,
    # )

    # document_topic_ids = fields.Many2many(
    #     related="dependence_id.document_topic_ids"
    # )

    # main_topic_ids = fields.Many2many(
    #     comodel_name="tmc.document_topic",
    #     # relation="document_main_topic_rel",
    #     column1="tmc_document_id",
    #     column2="tmc_document_topic_id",
    #     domain="[('parent_id', '=', False), ('id', 'in', document_topic_ids)]",
    # )

    # secondary_topic_ids = fields.Many2many(
    #     comodel_name="tmc.document_topic",
    #     relation="document_secondary_topic_rel",
    #     domain="[('parent_id', 'in', main_topic_ids)]",
    # )

    # related_document_ids = fields.Many2many(
    #     comodel_name="tmc.document",
    #     # relation="tmc_document_relation",
    #     column1="left_document_id",
    #     column2="right_document_id",
    #     domain="[('id', '!=', id)]",
    # )

    # document_object_required = fields.Boolean()

    # document_object = fields.Char(string="Object", size=125, index=True)

    # number = fields.Integer()

    # period = fields.Integer(store=True)

    # date = fields.Date(string='Inicio de Trámite')

    # subject = fields.Char('Subject')
    # reference = fields.Char()

    # in_tmc = fields.Boolean(string='Actualmente en TMC')



    # @api.depends("document_type_id", "dependence_id", "number", "period")
    # def _compute_name(self):
    #     for document in self:
    #         doc_abbr = document.document_type_id.abbreviation
    #         doc_number = document.number
    #         doc_period = document.period
    #         dep_abbr = document.dependence_id.abbreviation

    #         if doc_abbr == "ACT":
    #             doc_number = self.env.ref(
    #                 "tmc_data.seq_tmc_act"
    #             ).number_next_actual

    #         if doc_abbr and doc_number and doc_period and dep_abbr:
    #             document.name = "%s-%s-%s/%s" % (
    #                 doc_abbr,
    #                 str(doc_number).zfill(6),
    #                 dep_abbr,
    #                 doc_period,
    #             )
    #         else:
    #             document.name = _("Unnamed Document")

    # @api.onchange("dependence_id", "document_type_id", "period", "number")
    # def _onchange_document_data(self):
    #     if (
    #         self.dependence_id
    #         and self.document_type_id
    #         and self.number
    #         and self.period
    #     ):
    #         if self.env["tmc.document"].search([("name", "=", self.name)]):
    #             raise exceptions.Warning(_("Document already exists"))

    # @api.onchange("dependence_id")
    # def _onchange_dependence(self):
    #     self.document_type_id = False
    #     document_types = self.dependence_id.document_type_ids
    #     if len(document_types.ids) == 1:
    #         self.document_type_id = document_types.ids[0]
    #     return {"domain": {"document_type_id": [("id", "in", document_types.ids)]}}

    # @api.model
    # def create(self, vals):

    #     documento = self.env['tmc.document'].create({
    #         'dependence_id': vals.get('dependence_id'),
    #         'document_type_id': vals.get('document_type_id'),
    #         'number': vals.get('number'),
    #         'period': vals.get('period'),
    #         'document_object': vals.get('document_object'),
    #         'date': vals.get('date')
    #     })

    #     vals['document_id'] = documento.id

    #     return super(RegistryExp, self).create(vals)
