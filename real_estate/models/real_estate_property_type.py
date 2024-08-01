from odoo import fields, models
from odoo.tools import date_utils


class RealEstatePropertyType(models.Model):
    _name = 'real.estate.property.type'
    _description = "Real Estate Property Type"

    name = fields.Char(string="Name", required=True)
