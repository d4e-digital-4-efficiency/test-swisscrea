#-*- coding:utf-8 -*-

from odoo import api, models, fields, _


class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    name = fields.Char(string='Description', translate=True, required=True)
