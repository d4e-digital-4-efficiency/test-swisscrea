# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    round = fields.Selection(string="Round", readonly=False, related='company_id.round')

class ResCompany(models.Model):
    _inherit = 'res.company'

    round = fields.Selection(string="Round", selection=[('5', 5), ('1', 1)], default='5')
