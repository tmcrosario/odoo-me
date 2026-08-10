from odoo import api, models


class ReportMissingRaa(models.AbstractModel):
    _name = "report.raa.missing_raa_report"
    _description = "Missing Administrative Acts Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        # Recompute here; large lists via report_action data overflow the URL.
        docs = self.env["raa.entry"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "raa.entry",
            "docs": docs,
            "data": docs[:1].search_missing() if docs else {},
        }
