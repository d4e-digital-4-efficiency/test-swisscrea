# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReportAccountAvs(models.AbstractModel):
    _name = 'report.d4e_ch_payroll_report.report_account_avs'
    _description = 'report AVS'


    @api.model
    def _get_report_values(self, docids, data=None):
        if data.get('emp_id', False):
            emps = self.env['hr.employee'].browse(data['emp_id'])
        else:
            emps = self.env['hr.employee'].search([('contract_id.avs_contribution','=',True)])
        list1 = []
        for emp in emps:
            list1.append(self.get_employee_data(emp, data['year']))
        rep_data = {'lang': self._context.get('lang', 'fr_CH'),
                    'emp_ids': emps,
                    'year': data['year'],
                    'emps_data': list1,
                    }

        return {'report_data': rep_data}

    @api.model
    def get_employee_data(self, emp, year):
        payslips_first_last = self.env['hr.payslip'].search([('employee_id', '=', emp.id)], order='date_from')
        payslips_year = []

        for p in payslips_first_last:
            if p.date_from.year == year:
                payslips_year.append(p)

        acc_avs = False
        acc_ac = False
        acc_acc = False
        date_from = False
        date_to = False
        if payslips_year:
            date_from = payslips_year[0].date_from
            date_to = payslips_year[-1].date_to

        try:
            for line in payslips_year[-1].line_ids_employee_basis_ids:
                if line.code == '002':
                    acc_avs = line.total
                if line.code == '003':
                    acc_ac = line.total
                if line.code == '007':
                    acc_acc = line.total
        except:
            pass

        return {
            'date_from': date_from,
            'date_to': date_to,
            'acc_avs': acc_avs,
            'acc_acc': acc_acc,
            'acc_ac': acc_ac,
            'emp_id': emp,
        }

