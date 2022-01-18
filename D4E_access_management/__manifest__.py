# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'D4E Access Management',
    'version': '14.0.0.0.1',
    'category': '',
    'summary': 'Gérer des accès utilisateurs selon la valeur d un champ',
    'description': """ """,

    'website': 'https://d4e-ch.odoo.com',
    'depends': ['base', 'contacts', 'website', 'website_sale', 'event'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_users.xml',
        'views/product.xml',
        'views/event.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}