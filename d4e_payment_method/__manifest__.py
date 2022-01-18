# -*- coding: utf-8 -*-
{
    'name': 'D4E Account Payment Method',
    'version': '13.0.0.1',
    'category': 'Account',
    'summary': '',
    'description': "Account Payment Method Manager",
    'website': 'https://d4e-ch.odoo.com',
    'depends': [
        'account',
        'account_batch_payment',
    ],
    'data': [
        'security/res_groups.xml',
        'views/account_payment_method.xml',
        'menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
