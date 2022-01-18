# -*- coding: utf-8 -*-
{
    'name': 'Print Invoice Date',
    'version': '14.0.0.1',
    'description': """
        Print Invoice Date
    """,
    'Author': 'D4E',
    'category': 'Tools',
    'website': 'https://www.d4e.cool',
    'depends': [
        'account_accountant',
        'l10n_generic_coa',
        'l10n_ch',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'reports/account_move.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
