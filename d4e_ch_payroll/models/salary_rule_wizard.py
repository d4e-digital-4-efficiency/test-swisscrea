# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SalaryRuleWizard(models.TransientModel):
    _name = 'salary.rule.wizard'

    rules_to_add = fields.Many2many('hr.salary.rule', string="Rules")


    def add_rule(self):

        for rule in self.rules_to_add:
            rule.copy(default={

                'struct_id': self._context.get('active_ids')[0]

            })

            # res_ids = self._context.get('active_ids')
            #
            # invoices = self.env['account.move'].browse(res_ids).filtered(
            #     lambda move: move.is_invoice(include_receipts=True))