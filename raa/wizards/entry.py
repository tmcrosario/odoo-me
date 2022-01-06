from datetime import date
from itertools import count, groupby

from odoo import SUPERUSER_ID, _, api, exceptions, fields, models


class Entry(models.TransientModel):

    _name = "raa.entry"
    _description = "Wizard to load administrative acts"
    _inherit = ["tmc.report"]

    entry_date = fields.Date(required=True, default=fields.Date.context_today)

    period = fields.Integer(required=True, default=int(date.today().year))

    dependence_id = fields.Many2one(
        comodel_name="tmc.dependence",
        string="Dependence",
        domain=[
            ("document_type_ids", "!=", False),
            ("system_ids", "ilike", "RAA"),
        ],
        required=True,
    )

    document_type_id = fields.Many2one(
        comodel_name="tmc.document_type", required=True
    )

    document_type_ids = fields.Many2many(
        related="dependence_id.document_type_ids"
    )

    specify_maximum = fields.Boolean()

    maximum = fields.Integer()

    range_ids = fields.One2many(
        comodel_name="raa.number_range",
        inverse_name="registry_aa_id",
        required=True,
    )

    def as_range(self, iterable):
        range_list = list(iterable)
        if len(range_list) > 1:
            return "{0} a {1}".format(range_list[0], range_list[-1])
        else:
            return "{0}".format(range_list[0])

    def show_window_message(self):
        res = self.search_missing()
        if res["maximum"]:
            if res["missing"]:
                missing = ", ".join(
                    self.as_range(g)
                    for _, g in groupby(
                        res["missing"], key=lambda n, c=count(): n - next(c)
                    )
                )
                message = (
                    _("<p>Missing administrative acts: <b>%s</b></p>")
                    % missing
                )
            else:
                message = _("No missing administrative acts")
        else:
            message = _("No existing registries matching criteria")

        context = dict(self._context or {})
        context["message"] = message
        context["is_html"] = True
        res = {
            "name": _("Success"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "popup.message",
            "view_id": self.env["ir.model.data"].xmlid_to_res_id(
                "popup_message_view_form"
            ),
            "target": "new",
            "context": context,
        }  # yapf: disable

        return res

    def search_missing(self):
        domain = [
            ("document_id.document_type_id", "=", self.document_type_id.id),
            ("document_id.dependence_id", "=", self.dependence_id.id),
            ("document_id.period", "=", self.period),
        ]

        registries = self.env["raa.registry_aa"].search(domain)

        document_numbers = registries.mapped("document_id.number")

        last = None
        maximum = None
        missing = None
        missing_formatted = None

        if registries:
            last = maximum = max(document_numbers)
            if self.maximum:
                maximum = self.maximum

            missing = []
            for numbers in range(1, maximum + 1):
                if numbers not in document_numbers:
                    missing.append(numbers)

            missing_formatted = (
                [str(x).zfill(6) for x in missing] if missing else None
            )

        return {"last": last, "maximum": maximum, "missing": missing_formatted}

    def create_registry_aa(self):
        raa_ids = []

        if not self.range_ids:
            raise exceptions.UserError(_("No ranges were specified"))

        for aa_range in self.range_ids:
            for number in range(aa_range.number_from, aa_range.number_to + 1):
                doc_model = self.env["tmc.document"]
                domain = [
                    ("document_type_id", "=", self.document_type_id.id),
                    ("dependence_id", "=", self.dependence_id.id),
                    ("number", "=", number),
                    ("period", "=", self.period),
                ]
                document = doc_model.search(domain, limit=1)
                if not document:
                    vals = {
                        "document_type_id": self.document_type_id.id,
                        "dependence_id": self.dependence_id.id,
                        "number": number,
                        "period": self.period,
                    }
                    document = doc_model.with_user(SUPERUSER_ID).create(vals)

                raa_model = self.env["raa.registry_aa"]
                domain = [("document_id", "=", document.id)]
                raa = raa_model.search(domain, limit=1)
                if not raa:
                    vals = {
                        "entry_date": self.entry_date,
                        "document_id": document.id,
                    }
                    raa = raa_model.create(vals)
                    raa_ids.append(raa.id)

        if raa_ids:
            message = _("Registries were created successfully")
            context = dict(self._context or {})
            context["message"] = message
            res = {
                "name": _("Success"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "popup.message",
                "view_id": self.env["ir.model.data"].xmlid_to_res_id(
                    "popup_message_view_form"
                ),
                "target": "new",
                "context": context,
            }  # yapf: disable
        else:
            message = _("No new registries were created. They already exist.")
            context = dict(self._context or {})
            context["message"] = message
            res = {
                "name": _("Success"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "popup.message",
                "view_id": self.env["ir.model.data"].xmlid_to_res_id(
                    "popup_message_view_form"
                ),
                "target": "new",
                "context": context,
            }  # yapf: disable

        return res

    @api.onchange("specify_maximum")
    def _onchange_specify_maximum(self):
        self.maximum = False

    @api.constrains("maximum")
    def _check_maximum(self):
        if self.maximum > 6000:
            raise exceptions.UserError(
                _("Maximum number allowed has been exceeded")
            )
