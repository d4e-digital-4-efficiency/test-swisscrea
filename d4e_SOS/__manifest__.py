# -*- coding: utf-8 -*-
{
    'name': 'SOS by D4E',
    'version': '1.0',
    'summary': """
   D4E Offers
""",
    'Author': 'D4E',
    'category': 'Tools',
    'website': 'https://www.d4e.cool',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/sosdata.xml',
        'views/sos.xml',
        'views/settings.xml',
        'views/theme.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}