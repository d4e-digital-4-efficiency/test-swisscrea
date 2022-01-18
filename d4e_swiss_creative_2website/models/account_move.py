# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    website_id = fields.Many2one('website', string='Website')
