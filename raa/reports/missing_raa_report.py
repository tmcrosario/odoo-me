from odoo import api, models


class ReportMissingRaa(models.AbstractModel):
    _name = "report.raa.missing_raa_report"
    _description = "Missing Administrative Acts Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        # Nest the wizard payload under `data` so the template can read it
        docs = self.env["raa.entry"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "raa.entry",
            "docs": docs,
            "data": data or {},
        }
