# -*- coding: utf-8 -*-

from odoo import models, fields, api



class ReportChPayroll(models.AbstractModel):
    _name = 'report.d4e_ch_payroll.report_salary_certificate_template'
    _description = 'Switzerland salary certificate report'

    def _get_rubrique_value(self, emp, year, rubrique_num):
        amount = 0.0
        for slip in self.env['hr.payslip'].search([('employee_id', '=', emp.id),('state', '=', 'done')]):
            if slip.date_from.year == int(year):
                for line in slip.line_ids:
                    if line.salary_rule_id.rubrique_certificat == rubrique_num:
                        amount += line.total
        return amount

    @api.model
    def _get_report_values(self, docids, data=None):
        emps = self.env['hr.employee'].browse(data['emp_ids'])
        rep_data = {'lang': self._context.get('lang', 'fr_CH'),
                    'emp_ids': emps,
                    'year': data['year'],
                    'get_rubrique_value': self._get_rubrique_value,
                    }
        return {'report_data': rep_data}
