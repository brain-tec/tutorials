from odoo import models, fields, api, exceptions
from odoo.tools import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate model"

    name = fields.Char(required=True)
    description = fields.Char()
    postcode = fields.Char()
    available_from = fields.Date(
        copy=False, default=fields.Date.add(fields.Date.today(), months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    active = fields.Boolean(default=True)
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("new", "New"),
            ("offer received", "Offer Received"),
            ("offer accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        copy=False,
        default="new",
    )
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type", string="Property Type"
    )
    buyer = fields.Many2one(comodel_name="res.partner", copy=False)
    salesman = fields.Many2one(
        comodel_name="res.users", default=lambda self: self.env.uid
    )
    tag_ids = fields.Many2many(comodel_name="estate.property.tag", string="Tags")
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer", inverse_name="property_id"
    )
    total_area = fields.Integer(compute="_compute_area", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best_price")

    _postive_expected_price = models.Constraint(
        "CHECK (expected_price > 0)",
        "The expected price must be strictly positive"
    )

    _postive_selling_price = models.Constraint(
        "CHECK (selling_price > 0)",
        "The selling price must be strictly positive"
    )

    @api.depends("living_area", "garden_area")
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price'), default=0.0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def sell_property(self):
        for record in self:
            if record.state == "cancelled":
                raise exceptions.UserError("You cannot sell a cancelled property")
            else:
                record.state = "sold"
        return True

    def cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise exceptions.UserError("You cannot cancel a sold property")
            else:
                record.state = "cancelled"
        return True
    
    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if float_compare(record.selling_price, 0.9 * record.expected_price, 2) == -1:
                raise exceptions.ValidationError("The selling price must be at least 90% of the expected price.")
