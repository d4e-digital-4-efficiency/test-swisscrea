# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    internal_reference = fields.Char(string='Internal Reference')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    _sql_constraints = [
        (
            'check_credit_debit',
            'CHECK(credit + debit>=0 AND credit * debit=0)',
            'Wrong credit or debit value in accounting entry !'
        ),
        (
            'check_amount_currency_balance_sign',
            '''CHECK(
                (
                    (currency_id != company_currency_id)
                    AND
                    (
                        (debit - credit <= 0 AND amount_currency <= 0)
                        OR
                        (debit - credit >= 0 AND amount_currency >= 0)
                    )
                )
                OR
                (
                    currency_id = company_currency_id
                    AND
                    ROUND(debit - credit - amount_currency, 2) = 0
                )
            )''',
            "The amount expressed in the secondary currency must be positive when account is debited and negative when "
            "account is credited. If the currency is the same as the one from the company, this amount must strictly "
            "be equal to the balance."
        ),
    ]
