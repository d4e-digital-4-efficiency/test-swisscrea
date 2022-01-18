
# -*- coding: utf-8 -*-
{
    'name': 'D4E Custom reports',
    'version': '13.0.0.1',
    'category': 'Sale',
    'summary': '',
    'description': "Account Payment Method Manager",
    'website': 'https://d4e-ch.odoo.com',
    'depends': [
        'sale',
        'account',
        'account_reports',
        'stock',
        'sale_management',
        'delivery',
        'mrp',
        'sale_mrp',
        'l10n_ch',
        'account_followup'
    ],
    'data': [
        'report/report_invoice.xml',
        # 'demo/account_follow_up_demo.xml',
        'views/account_followup.xml',
        'report/report_deliveryslip.xml',
        'report/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}