# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Switzerland - Payroll Reports',
    'version': '14.0.0.0.1',
    'category': 'Human Resources',
    'summary': 'Liste de rapports de la paie en Suisse',
    'description': """ """,

    'website': 'https://d4e-ch.odoo.com',
    'depends': ['d4e_ch_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_salary_rule_views.xml',
        'views/salary_reports.xml',
        'wizard/company_total_summary_salary_account_views.xml',
        'report/report_payslip_templates.xml',
        'report/report_company_total_summary_salary_template.xml',
        'report/report_account_avs.xml',
        'views/salary_AVS_report.xml',
        'wizard/count_avs.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
