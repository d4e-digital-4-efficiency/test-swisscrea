#-*- coding:utf-8 -*-

from odoo import api, models, fields, _


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_salary_rules_by_rubrique(self, rubrique):
        rules = self.env['hr.salary.rule'].search([('payslip_rubrique', '=', rubrique)])
        return rules.ids if rules else []

    def _get_salary_rules_by_section(self, rubrique):
        rules = self.env['hr.salary.rule'].search([('rule_type', '=', 'section'), ('payslip_rubrique', '=', rubrique)])
        return rules.ids if rules else []
