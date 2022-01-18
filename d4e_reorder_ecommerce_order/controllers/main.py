# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    @http.route([
        '''/reorder/<model("sale.order"):order>'''], type='http', auth="public", website=True, sitemap=True)
    def reorder(self, order=None, **post):
        if order:
            sale_order = request.website.sale_get_order(force_create=True)
            for line in order.order_line.filtered(lambda l: l.product_template_id.type in ['consu', 'product']):
                line.copy({'order_id': sale_order.id})
        return request.redirect('/shop/cart')