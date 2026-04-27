from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Bak(models.Model):
    _name = 'bak'
    _description = 'Berita Acara Kejadian'
    _rec_name = 'name'

    # =====================
    # BASIC
    # =====================
    name = fields.Char(string="BAK Number", readonly=True, default='New')

    partner_id = fields.Many2one('res.partner', string="Nama Client", required=True)
    driver_name = fields.Char(string="Nama Pengemudi", required=True)
    address = fields.Text(string="Alamat Lengkap", required=True)
    phone = fields.Char(string="Nomor Telepon", required=True)

    # =====================
    # COST
    # =====================
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    cost = fields.Monetary(string="Biaya Ditanggung", currency_field='currency_id')

    # =====================
    # VEHICLE
    # =====================
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)

    license_plate = fields.Char(related='vehicle_id.license_plate', store=True)
    year = fields.Selection(related='vehicle_id.model_year', store=True)

    last_odometer = fields.Float(string="Last Odometer", required=True)

    # =====================
    # INCIDENT
    # =====================
    ticket_number = fields.Char(string="Ticket Number")

    incident_date = fields.Datetime(string="Tanggal Kejadian", required=True)
    location = fields.Text(string="Lokasi Kejadian", required=True)
    chronology = fields.Text(string="Detail Kronologi", required=True)
    damage = fields.Text(string="Bagian Rusak/Hilang")

    # =====================
    # FILE
    # =====================
    attachment = fields.Binary(string="Attachment")
    image = fields.Binary(string="Foto Kejadian")  # 🔥 WAJIB sesuai XML

    # =====================
    # WORKFLOW
    # =====================
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('done', 'Done')
    ], default='draft')

    # =====================
    # AUTO SEQUENCE
    # =====================
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bak.sequence') or 'New'
        return super().create(vals)

    # =====================
    # VALIDASI
    # =====================
    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone and not rec.phone.isdigit():
                raise ValidationError("Nomor telepon harus angka!")

    # =====================
    # ONCHANGE
    # =====================
    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.partner_id = self.vehicle_id.driver_id

    # =====================
    # BUTTON ACTION
    # =====================
    def action_submit(self):
        self.state = 'submitted'

    def action_approve(self):
        self.state = 'approved'