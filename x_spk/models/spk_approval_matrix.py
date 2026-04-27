from odoo import models, fields


class SPKApprovalMatrix(models.Model):
    _name = "spk.approval.matrix"
    _description = "SPK Approval Matrix Configuration"

    name = fields.Char(
        string="Name",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
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
        default=lambda self: self.env["spk.maintenance.type"].search(
            [("code", "=", "schedule")], limit=1
        ),
    )
    maintenance_type = fields.Char(
        string="Maintenance Type Code",
        related="maintenance_type_id.code",
        store=True,
        readonly=True,
    )
    amount_from = fields.Float(
        string="Amount From",
        required=True,
    )
    amount_to = fields.Float(
        string="Amount To",
        required=True,
    )
    approval_line_ids = fields.One2many(
        "spk.approval.matrix.line",
        "matrix_id",
        string="Approval Sequence",
    )


class SPKApprovalMatrixLine(models.Model):
    _name = "spk.approval.matrix.line"
    _description = "SPK Approval Matrix Line"
    _order = "sequence asc"

    matrix_id = fields.Many2one(
        "spk.approval.matrix",
        string="Approval Matrix",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=1,
    )
    approver_role = fields.Many2one(
        "res.groups",
        string="Approver Role",
        required=True,
    )
    approval_role = fields.Selection(
        [
            ("l1", "Level 1 (Manager)"),
            ("l2", "Level 2 (Senior Manager)"),
            ("l3", "Level 3 (Director)"),
        ],
        string="Approval Role",
        required=True,
        default="l1",
    )
    is_final_approver = fields.Boolean(
        string="Final Approver",
        default=False,
    )
