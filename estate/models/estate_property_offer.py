from odoo import models, fields, api


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "property offer"

    price = fields.Float()
    status = fields.Selection(
        copy=False,
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
    )
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    property_id = fields.Many2one("estate.property", required=True, string="Property")
    validity = fields.Integer(default=7)
    deadline_date = fields.Date(compute="_compute_deadline_date", inverse="_inverse_deadline_date")

    @api.depends("create_date", "validity")
    def _compute_deadline_date(self):
        for record in self:
            record.deadline_date = fields.Date.add((record.create_date or fields.Date.today()), days=record.validity)
    
    def _inverse_deadline_date(self):
        for record in self:
            record.validity = (record.deadline_date - fields.Date.today()).days
    