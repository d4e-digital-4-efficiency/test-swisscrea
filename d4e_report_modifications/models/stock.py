# -*- coding: utf-8 -*-
from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name_report = fields.Char(compute="_compute_name_report")

    def _compute_name_report(self):
        for rec in self:
            rec.name_report = rec.name.split('/')[-1]
