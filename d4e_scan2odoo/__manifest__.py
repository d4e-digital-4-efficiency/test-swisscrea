# -*- coding: utf-8 -*-
{
    'name': 'D4E Scan2Odoo',
    'version': '13.0.0.2',
    'summary': """Import a document from the DCS of D4E - Digital4Efficiency""",
    'author': 'D4E - Digital4Efficiency',
    'category': 'Tools',
    'website': 'https://www.digital4efficiency.ch',
    'depends': [
        'account', 'contacts'
    ],
    'data': [
        'views/contacts.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
