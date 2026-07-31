from odoo import api, fields, models


class RegistryAA(models.Model):
    _name = "raa.registry_aa"
    _description = "Administrative Act Registry"

    document_id = fields.Many2one(comodel_name="tmc.document", required=True)

    entry_date = fields.Date(default=fields.Date.context_today, required=True)

    document_type_id = fields.Many2one(
        related="document_id.document_type_id",
        readonly=True,
    )

    dependence_id = fields.Many2one(
        related="document_id.dependence_id",
        readonly=True,
    )

    number = fields.Integer(related="document_id.number", readonly=True)

    period = fields.Selection(related="document_id.period", readonly=True, store=True)

    @api.depends("document_id")
    def _compute_display_name(self):
        for raa_obj in self:
            raa_obj.display_name = raa_obj.document_id.display_name

    def unlink(self):
        for raa_obj in self:
            document_obj = raa_obj.document_id

            if (
                not document_obj.date
                and not document_obj.document_object
                and not document_obj.main_topic_ids
                and not document_obj.related_document_ids
                and not document_obj.highlight_ids
            ):
                super(RegistryAA, raa_obj).unlink()
                document_obj.unlink()
            else:
                super(RegistryAA, raa_obj).unlink()
        return True

    _document_id_unique = models.Constraint(
        "UNIQUE(document_id)",
        "Record already exists",
    )
