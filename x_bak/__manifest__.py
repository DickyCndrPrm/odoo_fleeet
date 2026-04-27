{
    'name': 'BAK (Berita Acara Kejadian)',
    'version': '1.0',
    'summary': 'BAK Module',
    'category': 'Operations',
    'author': 'Kurnia Galuh',
    'depends': [
        'base',
        'fleet',
        'x_service_planning' 
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/bak_views.xml',
    ],
    'installable': True,
    'application': False,
}