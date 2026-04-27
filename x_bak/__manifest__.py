{
    'name': 'BAK (Berita Acara Kejadian)',
    'version': '1.0',
    'summary': 'BAK Module',
    'category': 'Operations',
    'author': 'Kurnia Galuh',
    'depends': [
        'base',
        'fleet',
        'x_service_planning',
        'x_spk'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/bak_views.xml',
        'views/fleet_vehicle_views.xml'
    ],
    'installable': True,
    'application': False,
}