from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SPKAkiLine(models.Model):
    _name = "spk.aki.line"
    _description = "SPK AKI (Battery) Detail Line"

    spk_id = fields.Many2one(
        "fleet.spk",
        string="SPK",
        required=True,
        ondelete="cascade",
    )
    product_line_id = fields.Many2one(
        "spk.sparepart.line",
        string="Sparepart Product",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.template",
        string="AKI Product",
        related="product_line_id.product_id",
        store=True,
    )
    product_description = fields.Text(
        string="Product Description",
        compute="_compute_product_description",
        store=True,
    )
    old_AKI_code = fields.Char(
        string="Old AKI Code",
    )
    new_AKI_code = fields.Char(
        string="New AKI Code",
    )
    notes = fields.Text(string="Notes")

    def _check_parent_editable(self):
        for line in self:
            if line.spk_id and line.spk_id.state in ('approved', 'done', 'closed'):
                raise ValidationError('Approved SPK records cannot be edited anymore.')

    @api.depends(
        "product_id",
        "product_id.description_sale",
        "product_id.display_name",
    )
    def _compute_product_description(self):
        for line in self:
            if not line.product_id:
                line.product_description = False
                continue
            description_sale = getattr(line.product_id, "description_sale", False)
            display_name = getattr(line.product_id, "display_name", False)
            line.product_description = (
                description_sale or display_name
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            spk_id = vals.get('spk_id')
            if spk_id:
                spk = self.env['fleet.spk'].browse(spk_id)
                if spk.state in ('approved', 'done', 'closed'):
                    raise ValidationError('Approved SPK records cannot be edited anymore.')
        return super().create(vals_list)

    def write(self, vals):
        self._check_parent_editable()
        return super().write(vals)

    def unlink(self):
        self._check_parent_editable()
        return super().unlink()
