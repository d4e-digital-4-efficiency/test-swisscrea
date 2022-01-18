# -*- coding: utf-8 -*-

from odoo import models, fields, api
from operator import itemgetter

# months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]
months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décember' ]
rubriques =[('salaire_brut', 'Salaire Brut'), ('rht', 'RHT'), ('charges_sociales', 'Charges Sociales'), ('divers', 'Divers'), ('avances', 'Avances'), ('corrections', 'Corrections')]

class ReportCompanyTotalSummarySalary(models.AbstractModel):
    _name = 'report.d4e_ch_payroll_report.company_totsum_salary_template'
    _description = 'Company Total Summary Salary Account report'

    # def _get_rubrique_value(self, emp, year, rubrique_num):
    #     amount = 0.0
    #     for slip in self.env['hr.payslip'].search([('employee_id', '=', emp.id),('state', '=', 'done')]):
    #         if slip.date_from.year == int(year):
    #             for line in slip.line_ids:
    #                 if line.salary_rule_id.rubrique_certificat == rubrique_num:
    #                     amount += line.total
    #     return amount

    def _get_rubriques(self, op):
        for elem in rubriques:
            if elem[0] == op:
                return elem[1]

    def _get_amounts(self, emp, rubrique, year):
        if rubrique != 'none':
            rules = self.env['hr.salary.rule'].search([('payslip_rubrique', '=', rubrique)])
            rub = self._get_rubriques(rubrique)
        else:
            rules = self.env['hr.salary.rule'].search([('payslip_rubrique', '=', False)])
            rub = False
        res = []
        # sums = {'January': 0.0, 'February': 0.0, 'March': 0.0, 'April': 0.0, 'May': 0.0, 'June': 0.0, 'July': 0.0,
        #         'August': 0.0, 'September': 0.0, 'October': 0.0, 'November': 0.0, 'December': 0.0}
        sums = {'Janvier': 0.0, 'Février': 0.0, 'Mars': 0.0, 'Avril': 0.0, 'Mai': 0.0, 'Juin': 0.0, 'Juillet': 0.0,
                'Août': 0.0, 'Septembre': 0.0, 'Octobre': 0.0, 'Novembre': 0.0, 'Décember': 0.0}
        slips = self.env['hr.payslip'].search([('employee_id', '=', emp.id), ('state', 'in', ['paid','done']), ('credit_note', '=', False)])
        for rule in rules:
            rule_amounts = {}
            month_amount = {}
            add = False
            for m, month in enumerate(months, start=1):
                amount = 0.0
                for slip in slips:
                    if rule.id in slip.struct_id.rule_ids.ids:
                        add = True
                        if slip.date_from.year == int(year) and slip.date_from.month == int(m):
                            for line in slip.line_ids:
                                if line.salary_rule_id.id == rule.id:
                                    amount += line.total
                # calculation des salaire par mois
                month_amount[month] = amount
                sums[month] += amount
            if add:
                rule_amounts["rule"] = rule
                rule_amounts["amounts"] = month_amount
                res.append(rule_amounts)

        return {'rub': rub,'data': res, 'sums':sums}

    @api.model
    def _get_report_values(self, docids, data=None):
        if data.get('emp_id', False):
            emps = self.env['hr.employee'].browse(data['emp_id'])
        else:
            emps = self.env['hr.employee'].search([])
        rep_data = {'lang': self._context.get('lang', 'fr_CH'),
                    'emp_ids': emps,
                    'year': data['year'],
                    'months': months,
                    'rubriques': rubriques,
                    'get_amounts': self._get_amounts,
                    }
        return {'report_data': rep_data}
