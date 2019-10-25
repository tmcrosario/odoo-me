from odoo import _, api, fields, models


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
