from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SPKApprovalConfigMaster(models.Model):
    """SPK Approval Configuration Matrix"""
    _name = "spk.approval.config.master"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "SPK Approval Configuration"

    name = fields.Char(
        string="Name",
        copy=False,
        compute="_compute_name",
        store=True,
    )
    category = fields.Selection(
        [
            ("internal", "Internal"),
            ("external", "External"),
        ],
        string="Category",
        required=True,
    )
    maintenance_type_id = fields.Many2one(
        "spk.maintenance.type",
        string="Maintenance Type",
        required=True,
        ondelete="restrict",
    )
    amount_from = fields.Float(
        string="Starting Amount",
        required=True,
        default=0,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=1,
    )
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        required=True,
        domain="[('share', '=', False), ('active','=',True)]",
    )
    delegation_id = fields.Many2one(
        "res.users",
        string="Delegation",
        domain="[('share', '=', False), ('active','=',True)]",
        help="Optional delegation if primary approver is unavailable",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")],
        default="draft",
        string="Status",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env.company.id,
        index=True,
    )
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        (
            "unique_approval_config",
            "UNIQUE(category, maintenance_type_id, amount_from, company_id, active)",
            "Approval configuration must be unique per category, maintenance type, and amount range",
        ),
    ]

    @api.depends("category", "maintenance_type_id", "amount_from", "sequence")
    def _compute_name(self):
        """Auto-generate descriptive name"""
        for record in self:
            # Handle missing dependencies gracefully
            if not record.category or not record.maintenance_type_id or record.amount_from is None:
                record.name = "Approval Configuration"
                continue
            
            category_label = dict(
                record._fields["category"].selection
            ).get(record.category, record.category)
            mt_name = record.maintenance_type_id.name if record.maintenance_type_id else "N/A"
            record.name = f"{category_label} - {mt_name} - Rp {record.amount_from:,.0f}+".replace(
                ",", "."
            )

    def button_draft(self):
        for record in self:
            if record.state != "active":
                continue
            record.write({"state": "draft"})
        return True

    def button_confirm(self):
        for record in self:
            if record.state != "draft":
                continue
            record.write({"state": "active"})
        return True


class SPKApprovalMatrix(models.Model):
    """SPK Approval Matrix - tracks approval chain per SPK document"""
    _name = "spk.approval.matrix"
    _description = "SPK Approval Matrix"
    _order = "sequence asc"

    spk_id = fields.Many2one(
        "fleet.spk",
        string="SPK",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=1,
    )
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        required=True,
    )
    delegation_id = fields.Many2one(
        "res.users",
        string="Delegation",
        help="Optional delegation approver",
    )
    actual_approver_id = fields.Many2one(
        "res.users",
        string="Actual Approver",
        readonly=True,
        help="User who performed approval",
    )
    reject_by_id = fields.Many2one(
        "res.users",
        string="Rejected By",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("waiting_approval", "Waiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        required=True,
        default="waiting_approval",
    )
    date_approved = fields.Datetime(
        string="Date Approved",
        readonly=True,
    )
    date_rejected = fields.Datetime(
        string="Date Rejected",
        readonly=True,
    )
