# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    active = fields.Boolean(default=True)