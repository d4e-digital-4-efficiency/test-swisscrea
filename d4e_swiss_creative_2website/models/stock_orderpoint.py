# -*- coding: utf-8 -*-

import logging


from odoo import SUPERUSER_ID, _, api, fields, models, registry
from odoo.tools import float_compare, frozendict, split_every

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.depends('qty_multiple', 'qty_forecast', 'product_min_qty', 'product_max_qty')
    def _compute_qty_to_order(self):
        cur_prods = []
        prods = []
        for orderpoint in self:
            special = False
            if orderpoint.product_id not in prods:
                if not orderpoint.product_id or not orderpoint.location_id:
                    orderpoint.qty_to_order = False
                    continue
                qty_to_order = 0.0
                rounding = orderpoint.product_uom.rounding
                if float_compare(orderpoint.qty_forecast, orderpoint.product_min_qty, precision_rounding=rounding) < 0:
                    # if orderpoint.product_tmpl_id.special_reappro:
                    #     qty_to_order = max(orderpoint.product_min_qty, orderpoint.product_max_qty) - orderpoint.qty_on_hand
                    # else:
                    qty_to_order = max(orderpoint.product_min_qty, orderpoint.product_max_qty) - orderpoint.qty_forecast

                    remainder = orderpoint.qty_multiple > 0 and qty_to_order % orderpoint.qty_multiple or 0.0
                    if float_compare(remainder, 0.0, precision_rounding=rounding) > 0:
                        qty_to_order += orderpoint.qty_multiple - remainder
                    special = True
                purchases = self.env['purchase.order.line'].search([('orderpoint_id', '=', orderpoint.id),('state', '!=', 'cancel')], limit=1, order='id desc')
                if self.env.context.get('compute_max_qty', False) and orderpoint.product_tmpl_id.special_reappro and (special or purchases):
                    cur_prods = orderpoint._get_same_supplier_product(purchases.partner_id) if purchases else orderpoint._get_same_supplier_product()
                    # if special or any(p.product_tmpl_id.virtual_available < p.product_tmpl_id.reordering_min_qty for p in cur_prods):
                    for prod in cur_prods:
                        qty_to_orderx = 0.0
                        prod_orderpoint = self.filtered(lambda e: e.product_id.id == prod.id)
                        if prod_orderpoint and prod_orderpoint.product_tmpl_id.special_reappro:
                            qty_to_orderx = max(prod_orderpoint.product_min_qty,
                                               prod_orderpoint.product_max_qty) - prod_orderpoint.qty_forecast
                            if qty_to_orderx >= 6:
                                qty_to_orderx = qty_to_orderx - (qty_to_orderx % 6)
                            else:
                                qty_to_orderx = 0.0
                            prod_orderpoint.qty_to_order = qty_to_orderx
                            prods.append(prod)

                if orderpoint.product_tmpl_id.special_reappro:
                    if qty_to_order >= 6:
                        qty_to_order = qty_to_order - (qty_to_order % 6)
                    else:
                        qty_to_order = 0.0
                orderpoint.qty_to_order = qty_to_order


    def _get_same_supplier_product(self, supp=None):
        products = []
        sixaine = self.env.ref('d4e_swiss_creative_2website.product_uom_six_unit').id
        supp = self.product_id._select_seller(partner_id= supp, uom_id=sixaine)
        for prod in self.env['product.template'].search([('special_reappro', '=', True),('uom_po_id', '=', sixaine)]):
            # if (prod.qty_available <= prod.reordering_max_qty)and(prod.qty_available >= prod.reordering_min_qty):
            if prod.virtual_available <= (prod.reordering_max_qty-6):
                product = self.env['product.product'].search([('product_tmpl_id', '=', prod.id)])
                seller = product._select_seller(partner_id=supp.name, uom_id=supp.product_uom)
                if supp.name.id == seller.name.id and product.id != self.product_id.id:
                    products.append(product)
        return products