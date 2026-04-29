from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SPKApprovalLine(models.Model):
    _name = "spk.approval.line"
    _description = "SPK Approval Line"
    _order = "sequence asc"

    spk_id = fields.Many2one(
        "fleet.spk",
        string="SPK",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", default=1)
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        required=True,
    )
    delegation_id = fields.Many2one(
        "res.users",
        string="Delegation",
        help="Optional delegation approver if primary approver is unavailable",
    )
    state = fields.Selection(
        [
            ("waiting_approval", "Waiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="waiting_approval",
    )
    actual_approver_id = fields.Many2one(
        "res.users",
        string="Actual Approver",
        readonly=True,
        help="User who actually performed the approval",
    )
    reject_by_id = fields.Many2one(
        "res.users",
        string="Rejected By",
        readonly=True,
    )
    date_approved = fields.Datetime(string="Date Approved", readonly=True)
    date_rejected = fields.Datetime(string="Date Rejected", readonly=True)
    remarks = fields.Text(string="Remarks")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
    )


    def _check_parent_editable(self):
        for approval in self:
            if approval.spk_id and approval.spk_id.state in ('approved', 'done', 'closed'):
                raise ValidationError('Approved SPK records cannot be edited anymore.')

    def _check_assigned_approver(self):
        for approval in self:
            if approval.approver_id != self.env.user and not self.env.su:
                raise ValidationError(
                    "Only assigned approver can process this approval."
                )

    def write(self, vals):
        self._check_parent_editable()
        protected_fields = {
            "state",
            "date_approved",
            "approver_id",
            "remarks",
            "attachment_ids",
        }
        if (
            not self.env.su
            and not self.env.context.get("skip_approval_write_check")
            and protected_fields.intersection(vals.keys())
        ):
            self._check_assigned_approver()
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            spk_id = vals.get('spk_id')
            if spk_id:
                spk = self.env['fleet.spk'].browse(spk_id)
                if spk.state in ('approved', 'done', 'closed'):
                    raise ValidationError('Approved SPK records cannot be edited anymore.')
        return super().create(vals_list)

    def unlink(self):
        self._check_parent_editable()
        return super().unlink()

    def action_approve(self):
        """Mark this approval line as approved."""
        for approval in self:
            approval._check_assigned_approver()
            approval.write({
                'state': 'approved',
                'actual_approver_id': self.env.user.id,
                'date_approved': fields.Datetime.now(),
            })
            approval.spk_id._compute_next_approver()
            approval.spk_id._send_next_approver_notification()

    def action_reject(self):
        """Reject this approval line."""
        for approval in self:
            approval._check_assigned_approver()
            approval.write({
                'state': 'rejected',
                'reject_by_id': self.env.user.id,
                'date_rejected': fields.Datetime.now(),
            })
            approval.spk_id.write({'state': 'rejected'})

    def action_open_approve_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("approve")

    def action_open_reject_wizard(self):
        self.ensure_one()
        return self._open_action_wizard("reject")

    def _open_action_wizard(self, action_type):
        """Open approval action wizard"""
        self.ensure_one()
        self._check_assigned_approver()
        return {
            "type": "ir.actions.act_window",
            "name": "SPK Approval Action",
            "res_model": "spk.approval.action.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_spk_id": self.spk_id.id,
                "default_approval_id": self.id,
                "default_action_type": action_type,
            },
        }
