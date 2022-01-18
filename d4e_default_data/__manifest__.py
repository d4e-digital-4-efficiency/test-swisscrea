# -*- coding: utf-8 -*-
{
    'name': "D4E Default data",
    'description': """
        D4E Default data
    """,
    'author': "D4E",
    'website': "https://www.d4e.cool",
    'category': 'Tools',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base',  'l10n_ch', 'account_reports'],
    # always loaded
    'data': [
        'data/account_tax_data.xml',
        'data/account_tax_template.xml',
        'data/account_data.xml',
        'data/translation.xml',
    ],
}