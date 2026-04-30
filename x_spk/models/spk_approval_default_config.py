from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SPKApprovalDefaultConfig(models.Model):
    """Default SPK Approval Fallback Configuration"""
    _name = "spk.approval.default.config"
    _description = "SPK Default Approval Configuration"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        unique=True,
        ondelete="cascade",
        index=True,
    )
    default_approver_id = fields.Many2one(
        "res.users",
        string="Default Approver",
        required=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        help="Default approver when no approval rule matches the SPK amount or criteria",
    )
    delegation_id = fields.Many2one(
        "res.users",
        string="Default Delegation",
        domain="[('share', '=', False), ('active', '=', True)]",
        help="Optional delegation if primary default approver is unavailable",
    )
    description = fields.Text(string="Description", help="Internal notes about this configuration")
    active = fields.Boolean(string="Active", default=True)

    @api.constrains("company_id", "active")
    def _check_unique_active_per_company(self):
        for record in self:
            if record.active:
                existing = self.search([
                    ("company_id", "=", record.company_id.id),
                    ("active", "=", True),
                    ("id", "!=", record.id),
                ])
                if existing:
                    raise ValidationError(
                        "Only one active default approval configuration per company allowed. "
                        f"Company {record.company_id.id} already has one configured."
                    )
