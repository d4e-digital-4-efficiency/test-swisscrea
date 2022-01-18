from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"


    def run_inv_onchanges(self):
        try:
            self._onchange_partner_id()
            self._onchange_invoice_date()
            self._onchange_currency()
            self._onchange_recompute_dynamic_lines()
            self._onchange_invoice_line_ids()
            self._onchange_journal()
            self._onchange_invoice_payment_ref()
            self._onchange_invoice_vendor_bill()
            self._onchange_type()
        except Exception as e:
            print(str(e))
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    def run_inv_lines_onchanges(self):
        try:
            self._onchange_product_id()
            self._onchange_currency()
            self._onchange_amount_currency()
            self._onchange_credit()
            self._onchange_debit()
            self._onchange_mark_recompute_taxes()
            self._onchange_mark_recompute_taxes_analytic()
            self._onchange_balance()
            self._onchange_price_subtotal()
        except Exception as e:
            print(str(e))
        return True
