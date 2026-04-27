from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    bastk_ids = fields.One2many('bastk.bastk', 'vehicle_id', string='BASTK')
    bastk_count = fields.Integer(compute='_compute_bastk_count', string='BASTK Count')

    def _compute_bastk_count(self):
        for vehicle in self:
            vehicle.bastk_count = self.env['bastk.bastk'].search_count([('vehicle_id', '=', vehicle.id)])

    def action_open_bastk(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'BASTK',
            'res_model': 'bastk.bastk',
            'view_mode': 'list,form', 
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }