from odoo import _, api, fields, models


class NumberRange(models.TransientModel):

    _name = "raa.number_range"
    _description = "Administrative Acts Ranges"

    registry_aa_id = fields.Many2one(comodel_name="raa.entry", required=True)

    number_from = fields.Integer(required=True)

    number_to = fields.Integer(required=True)

    @api.constrains("number_from", "number_to")
    def _check_ranges(self):
        for number_range in self:
            if number_range.number_from > number_range.number_to:
                raise Warning(_("There are values in conflict"))
            elif number_range.number_from < 1 or number_range.number_to < 1:
                raise Warning(_("You must enter values greater than 0 (zero)"))
            elif number_range.number_to > 6000:
                raise Warning(_("Maximum number allowed has been exceeded"))
            return True
