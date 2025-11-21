from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "property types"

    name = fields.Char(required=True)

    _unique_type = models.Constraint(
        "unique(name)",
        "This type already exists"
    )
