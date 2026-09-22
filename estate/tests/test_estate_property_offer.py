from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEstatePropertyOffer(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.property = cls.env["estate.property"].create({
            "name": "Luxury Sea View Villa",
            "expected_price": 100000.0,
            "state": "new",
            "postcode": "361210",
        })
        cls.buyer_1 = cls.env["res.partner"].create({
            "name": "ABC",
        })
        cls.buyer_2 = cls.env["res.partner"].create({
            "name": "XYZ",
        })

        cls.offer1 = cls.env["estate.property.offer"].create({
            "partner_id": cls.buyer_1.id,
            "property_id": cls.property.id,
            "price": 100000.0,
        })
        cls.offer2 = cls.env["estate.property.offer"].create({
            "partner_id": cls.buyer_2.id,
            "property_id": cls.property.id,
            "price": 110000.0,
        })

    def test_offer_accept(self):
        self.offer2.action_accept()

        self.assertEqual(self.offer2.status, "accepted")
        self.assertEqual(self.offer1.status, "rejected")
        self.assertEqual(self.property.selling_price, 110000.0)
        self.assertEqual(self.property.buyer_id, self.buyer_2)
        self.assertEqual(self.property.state, "offer_accepted")
