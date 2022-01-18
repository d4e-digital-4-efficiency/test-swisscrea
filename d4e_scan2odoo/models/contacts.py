# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Contacts(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_data_account_type_expenses(self):
        return [
            ('user_type_id', '=',
             self.env.ref('account.data_account_type_expenses').id)
        ]

    default_charge_account_for_capture = fields.Many2one('account.account', string="Default charge account for capture",
                                                         domain=_get_data_account_type_expenses)