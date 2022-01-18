# -*- coding: utf-8 -*-
from odoo import models, api


class Payment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('payment_method_id')
    def onchange_payment_method_id(self):
        if self.payment_method_id:
            self.update({'communication': self.payment_method_id.name_get()[0][1]})
