from odoo import models, fields, api, _
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_sequence = fields.Char(string="Sequence", compute="_compute_order_sequence", )

    @api.depends('name')
    def _compute_order_sequence(self):
        for rec in self:
            rec.order_sequence = re.findall('\d+', rec.name)[-1]
