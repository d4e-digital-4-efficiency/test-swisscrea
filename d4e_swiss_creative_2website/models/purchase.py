# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    def write(self, vals):
        if vals.get('product_qty', False) and self.order_id.create_uid.id == self.env.ref('base.user_root').id:
            vals['orderpoint_id'] = False
            for line in self.order_id.order_line.filtered(lambda l: l.id != self.id):
                line.orderpoint_id = False
            self.order_id.origin = ''
        return super().write(vals)


    def unlink(self):
        if self.get('product_qty',False) and self.order_id.create_uid.id == self.env.ref('base.user_root').id:
            for line in self.order_id.order_line.filtered(lambda l: l.id != self.id):
                line.orderpoint_id = False
            self.order_id.origin = ''
        return super().unlink()