# -*- coding: utf-8 -*-
{
    'name': 'Domain Snippet',
    'description': """Digital4Efficiency - Domain Snippet""",
    'Author': 'D4E',
    'category': 'Tools',
    'website': 'https://www.d4e.cool',
    'version': '14.0.1.0',
    'depends': [
        'contacts',
        'website',
        'web_editor',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/res_domain.xml',
        'views/snippets.xml',
        'menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
