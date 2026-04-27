from odoo import models, fields, api

class BastkType(models.Model):
    _name = 'bastk.type'
    _description = 'BASTK Type'
    _order = 'sequence'

    name = fields.Char('Type Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)

class BastkChecklistItem(models.Model):
    _name = 'bastk.checklist.item'
    _description = 'BASTK Description Item'
    _order = 'sequence'

    name = fields.Char('Description', required=True, translate=True)
    applies_on = fields.Selection([
        ('keluar', 'Keluar'),
        ('masuk', 'Masuk'),
        ('both', 'Both')
    ], string='Type', required=True, default='both')
    sequence = fields.Integer('Sequence', default=10)