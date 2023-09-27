# -*- coding: utf-8 -*-
{
    'name': 'Inventory Dashboard',
    'version': '16.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Inventory Dashboard',
    'depends': ['stock', 'base'],
    'data': [
                'security/inventory_dashboard_security.xml',
                'views/dashboard_menu.xml',
             ],
    'assets': {
        'web.assets_backend': [
            'inventory_dashboard/static/src/css/style.css',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js',
            'inventory_dashboard/static/src/js/custom_dashboard.js',
            'inventory_dashboard/static/src/xml/dashboard.xml',

        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}