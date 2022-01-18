# -*- coding: utf-8 -*-
from odoo import models, api


class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.onchange('payment_method_id')
    def onchange_payment_method_id(self):
        if self.payment_method_id:
            self.update({'communication': self.payment_method_id.name_get()[0][1]})
