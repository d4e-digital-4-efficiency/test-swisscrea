# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"


    supp_invoice = fields.Boolean(default=False, copy=False)


    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund') and r.state != 'cancel')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
