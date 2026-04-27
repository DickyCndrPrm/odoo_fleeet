from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class Bastk(models.Model):
    _name = 'bastk.bastk'
    _description = 'BASTK Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char('BASTK Number', copy=False, readonly=True, default='New')
    bastk_type_id = fields.Many2one('bastk.type', string='BASTK Type', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Unit', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    pic_partner = fields.Char('PIC Partner')
    call_number = fields.Char('Call Number', default=None)
    address = fields.Text('Address')
    driver = fields.Char('Driver')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date')
    description = fields.Text('Description')
    
    # Fields yang diambil dari vehicle (free text, diisi otomatis saat pilih unit)
    asset_number = fields.Char('Asset Number')
    license_plate = fields.Char('License Plate')
    unit_type = fields.Char('Unit Type')
    color = fields.Char('Color')
    model_year = fields.Char('Model Year')
    vin_number = fields.Char('VIN Number')
    engine_number = fields.Char('Engine Number')

    inspection_line_keluar_ids = fields.One2many(
        'bastk.inspection.line', 'bastk_id', 
        string='Checklist Keluar', 
        domain=[('type', '=', 'keluar')],
        context={'default_type': 'keluar'}
    )
    inspection_line_masuk_ids = fields.One2many(
        'bastk.inspection.line', 'bastk_id', 
        string='Checklist Masuk', 
        domain=[('type', '=', 'masuk')],
        context={'default_type': 'masuk'}
    )    
    customer_sign = fields.Binary('Customer Sign', attachment=True)
    cakrawala_sign = fields.Binary('Cakrawala Sign', attachment=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.model
    def default_get(self, fields_list):
        """Sediakan line checklist awal saat buat BASTK baru."""
        res = super().default_get(fields_list)
        items = self.env['bastk.checklist.item'].search([])
        keluar_lines = []
        masuk_lines = []
        for item in items:
            if item.applies_on in ('keluar', 'both'):
                keluar_lines.append((0, 0, {
                    'checklist_item_id': item.id,
                    'type': 'keluar',
                    'sequence': item.sequence,
                }))
            if item.applies_on in ('masuk', 'both'):
                masuk_lines.append((0, 0, {
                    'checklist_item_id': item.id,
                    'type': 'masuk',
                    'sequence': item.sequence,
                }))
        if 'inspection_line_keluar_ids' in fields_list:
            res['inspection_line_keluar_ids'] = keluar_lines
        if 'inspection_line_masuk_ids' in fields_list:
            res['inspection_line_masuk_ids'] = masuk_lines
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.address = self.partner_id.street or ''
        else:
            self.address = ''

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            vehicle = self.vehicle_id
            if vehicle._name != 'fleet.vehicle':
                vehicle = self.env['fleet.vehicle'].browse(vehicle.id)
            if vehicle.exists():
                # self.asset_number = vehicle.vin_sn or vehicle.name
                self.license_plate = vehicle.license_plate
                self.unit_type = vehicle.model_id.name if vehicle.model_id else ''
                self.color = vehicle.color
                self.model_year = vehicle.model_year
                self.vin_number = vehicle.vin_sn
                # self.engine_number = ''
            else:
                self.asset_number = self.license_plate = self.unit_type = self.color = self.model_year = self.vin_number = self.engine_number = ''
        else:
            self.asset_number = self.license_plate = self.unit_type = self.color = self.model_year = self.vin_number = self.engine_number = ''

    @api.model_create_multi
    def create(self, vals_list):
        """Override create untuk handle sequence."""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self._generate_sequence()
        return super().create(vals_list)

    def _generate_sequence(self):
        return self.env['ir.sequence'].next_by_code('bastk.sequence') or '0001'


class BastkInspectionLine(models.Model):
    _name = 'bastk.inspection.line'
    _description = 'BASTK Inspection Line'
    _order = 'sequence'

    bastk_id = fields.Many2one('bastk.bastk', required=True, ondelete='cascade')
    checklist_item_id = fields.Many2one('bastk.checklist.item', required=True, string='Description')
    type = fields.Selection([('keluar', 'Keluar'), ('masuk', 'Masuk')], required=True, default='keluar')
    
    is_baik = fields.Boolean('Baik', default=False)
    is_tidak_ada = fields.Boolean('Tidak Ada', default=False)
    is_rusak = fields.Boolean('Rusak', default=False)
    is_hilang = fields.Boolean('Hilang', default=False)
    remarks = fields.Text('Remarks')
    
    sequence = fields.Integer('Sequence', default=10)

    @api.constrains('is_baik', 'is_tidak_ada', 'is_rusak', 'is_hilang')
    def _check_at_least_one_condition(self):
        for line in self:
            if not (line.is_baik or line.is_tidak_ada or line.is_rusak or line.is_hilang):
                raise ValidationError("Setiap item checklist harus memilih salah satu kondisi: Baik, Tidak Ada, Rusak, atau Hilang.")