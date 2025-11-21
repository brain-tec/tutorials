from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "property tags"

    name = fields.Char(required=True)

    _unique_tag = models.Constraint(
        "unique(name)",
        "This tag already exists"
    )
    