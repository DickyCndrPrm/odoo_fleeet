from odoo import models, fields, api


class SPKOnRiskProductLine(models.Model):
    _name = "spk.on.risk.product.line"
    _description = "SPK Product On Risk Line (for Accident Category)"

    spk_id = fields.Many2one(
        "fleet.spk",
        string="SPK",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.template",
        string="Product",
        required=True,
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
        required=True,
    )
    unit_price = fields.Float(
        string="Unit Price",
        required=True,
    )
    description = fields.Text(
        string="Damage Description",
        required=True,
    )
    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
    )

    @api.model
    def _get_product_autofill_vals(self, product):
        return {
            "description": product.description_sale or product.display_name,
            "unit_price": product.standard_price or product.list_price,
        }

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            product = line.product_id
            if not product:
                continue
            line.update(self._get_product_autofill_vals(product))

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price
