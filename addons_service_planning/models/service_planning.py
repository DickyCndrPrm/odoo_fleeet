from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServicePlanning(models.Model):
    _name = 'service.planning'
    _description = 'Service Planning'
    _rec_name = 'name'

    name = fields.Char(string="Name", readonly=True, default='/')

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    
    license_plate = fields.Char(related='vehicle_id.license_plate', store=True)
    vin_number = fields.Char(related='vehicle_id.vin_sn', store=True)
    engine_number = fields.Char(related='vehicle_id.engine_number', store=True)
    color = fields.Char(related='vehicle_id.color', store=True)
    asset_number = fields.Char(related='vehicle_id.asset_number', store=True)
    
    service_part = fields.Many2one(
        'product.template',
        string="Service Part",
        domain="[('type','=','service')]",
        required=True
    )

    kilometer = fields.Integer(string="Kilometer", required=True)
    interval = fields.Integer(string="Interval", required=True)

    brand_recommendation = fields.Char()
    remarks = fields.Text()

    def create(self, vals):
        if not vals.get('name') and vals.get('vehicle_id'):
            vehicle = self.env['fleet.vehicle'].browse(vals.get('vehicle_id'))
            vals['name'] = self.env['ir.sequence'].next_by_code('service.planning') or '/'
        return super().create(vals)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        for rec in self:
            if rec.vehicle_id:
                rec.name = f"Service Planning - {rec.vehicle_id.name}"

    @api.constrains('kilometer', 'interval')
    def _check_values(self):
        for rec in self:
            if rec.kilometer <= 0:
                raise ValidationError("Kilometer harus lebih dari 0")
            if rec.interval <= 0:
                raise ValidationError("Interval harus lebih dari 0")
            
    def action_create_spk(self):
    # placeholder dulu (nanti integrasi bareng tim)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': 'SPK akan dibuat di tahap integrasi',
                'type': 'success',
            }
        }
            
    _sql_constraints = [
        (
            'unique_service_plan',
            'unique(vehicle_id, service_part, kilometer)',
            'Service Planning untuk kombinasi ini sudah ada!'
        )
    ]