{
    'name': 'x_bastk',
    'version': '0.1.0',
    'category': 'Fleet',
    'summary': 'Berita Acara Serah Terima Kendaraan',
    'description': """
        Custom Modul untuk mengelola BASTK (Berita Acara Serah Terima Kendaraan) dan integrasi ke modul fleet.
    """,
    'author': 'Falih',
    'depends': ['base', 'fleet', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/bastk_sequence.xml',
        'data/bastk_description_master_data.xml',
        'data/bastk_type_master_data.xml',
        'views/bastk_type_views.xml',
        'views/bastk_description_item_views.xml',
        'views/bastk_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}