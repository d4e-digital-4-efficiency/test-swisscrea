# -*- coding: utf-8 -*-
#################################################################################
# Author      : PIT Solutions AG. (<https://www.pitsolutions.ch/>)
# Copyright(c): 2019 - Present PIT Solutions AG.
# License URL : https://www.webshopextension.com/en/licence-agreement/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.webshopextension.com/en/licence-agreement/>
#################################################################################

{
    'name': 'PostFinance Checkout Flex',
    'category': 'Payment Gateway',
    'summary': '''Payment Acquirer: PostFinance Checkout Flex Implementation
        Payment Acquirer: PostFinance Checkout Flex
        More infos on integrated payment gateways,https://checkout.postfinance.ch/
    ''',
    'version': '14.0.1.0',
    'description': """PostFinance Checkout Flex Payment Acquirer""",
    'currency': 'EUR',
    'price': 150,
    'license': 'OPL-1',
    'author': 'PIT Solutions AG',
    'website': 'http://www.pitsolutions.ch/en/',
    'depends': ['account_payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_acquirer_log.xml',
        'views/postfinance_payment_method_views.xml',
        'views/payment_views.xml',
        'views/postfinance_templates.xml',
        'data/payment_acquirer_data.xml',
        'data/ir_cron_data.xml',
    ],
    'images': ['static/description/banner.png',
    ],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}

