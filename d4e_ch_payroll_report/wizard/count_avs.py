# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime



class AccountAvs(models.TransientModel):
    _name = 'account.avs'
    _description = 'Wizard to define the year for the Company Total Summary Salary Account Report'

    def _get_years_list(self):
        current_year = datetime.today().year
        years = list(range(current_year -10 , current_year + 10))
        return [(x, x) for x in years]

    certif_year = fields.Selection(_get_years_list, string="Year", default=datetime.today().year)
    emp_id = fields.Many2many('hr.employee', string="Employee", domain=lambda self: self._domain_employee_avs())

    @api.model
    def _domain_employee_avs(self):
        res = self.env['hr.employee'].search([('contract_id.avs_contribution','=',True)]).ids
        return "[('id', 'in', %s)]" % res


    def print_report(self):
        self.ensure_one()
        data = {
            'emp_id': self.emp_id.ids,
            'year': int(self.certif_year),
        }
        return self.env.ref('d4e_ch_payroll_report.action_report_avs_account').report_action([], data=data)
