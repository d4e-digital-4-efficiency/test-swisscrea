# -*- coding: utf-8 -*-
{
    'name': "D4e Pack Accounting",
    'description': """
        D4e Pack Accounting
    """,
    'author': "D4E",
    'website': "https://www.d4e.cool",
    'category': 'Tools',
    'version': '14.0.1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'sale_management',
        'contacts',
        'l10n_ch',
        'hr',
        'web',
        'account_reports',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/account_report.xml',
        'views/res_partner.xml',
        'views/template.xml',
        'views/res_bank.xml',
        'views/postal_number.xml',
    ],
}
