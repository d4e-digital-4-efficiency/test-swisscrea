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

from odoo import api, fields, models, _


class PaymentIcon(models.Model):
    _inherit = 'payment.icon'
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char(translate=True)


class PostFinancePaymentMethod(models.Model):
    _name = 'postfinance.payment.method'
    _description = 'PostFinance Payment Method Details'
    _order = 'sequence'

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Many2one('payment.icon', 'Name', required=True)
    acquirer_id = fields.Many2one('payment.acquirer', 'Acquirer', required=True)
    space_id = fields.Integer(string='Space Ref', required=True)
    method_id = fields.Integer(string='Payment Method Ref', required=True)
    image_url = fields.Char('Image Url', size=1024)
    one_click = fields.Boolean(string='oneClick Payment', default=False)
    one_click_mode = fields.Boolean(string='oneClick Payment Mode', default=False)
    payment_method_ref = fields.Float(string='Payment Method', digits=(15, 0))
    transaction_interface = fields.Char('Transaction Interface')
    active = fields.Boolean(default=True)
    version = fields.Integer(required=True)

    def action_post_data(self):
        for postfinance_pay_method in self:
            postfinance_acquirer = postfinance_pay_method.acquirer_id
        
    
    