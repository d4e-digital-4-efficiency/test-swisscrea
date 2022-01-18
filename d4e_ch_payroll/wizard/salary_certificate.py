# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime

class SalaryCertificate(models.TransientModel):
    _name = 'salary.certificate'
    _description = 'Wizard to define data for the Salary Certificate Report'

    def _get_years_list(self):
        current_year = datetime.today().year
        years = list(range(current_year -10 , current_year + 10))
        return [(x, x) for x in years]


    emp_id = fields.Many2many('hr.employee', string='Employee')
    all_emp = fields.Boolean("All Employees")
    certif_year = fields.Selection(_get_years_list, string="Year", default= datetime.today().year)

    @api.onchange('all_emp')
    def _onchange_all_emp(self):
        if self.all_emp:
            self.emp_id = False

    def print_report(self):
        self.ensure_one()
        data = {
            'emp_ids': self.emp_id.ids if not self.all_emp else self.env['hr.employee'].search([]).ids,
            'year': int(self.certif_year),
        }
        return self.env.ref('d4e_ch_payroll.action_report_salary_certificate').report_action([], data=data)
