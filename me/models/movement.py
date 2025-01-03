from odoo import fields, models

class Movement(models.Model):

    _name = "me.movement"
    _description = "Movement"

    origin = fields.Char()

    destination = fields.Char()

    pages = fields.Integer()