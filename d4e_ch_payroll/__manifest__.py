# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Switzerland - Payroll',
    'version': '14.0.0.0.1',
    'category': 'Human Resources',
    'summary': 'Manage your employee payroll records',
    'description': """
Règles de gestion de la paie en Suisse.
=======================================
* Date Courant :

compute_current_date(): retourner un objet Datetime, donc tu peut appliquer .year, .month, ...
Cette methode est appelé dans le regle de salaire de cette façon :

    date = compute_current_date()
    
* Taux d'impôt :

compute_fetch_taux (canton, année en cours, salaire mensuel, Barême de perception)
Cette methode est appelé dans le regle de salaire de cette façon :

    result = payslip.env['hr.payslip'].compute_fetch_taux('GE', 2021, 100.0, 'HE')

* Cumul de salaire :

compute_fetch_cumulsalaire(barème de perception, année)
Cette methode est appelé dans le regle de salaire de cette façon :

    result = employee.compute_fetch_cumulsalaire('B2', 2021)

* Réserve des déductions AVS reportable sur l'année :

compute_upsert_AVSreportable(montant)
Cette methode est appelé dans le regle de salaire de cette façon :

    result = employee.compute_upsert_AVSreportable(123.9)
    """,

    'website': 'https://d4e-ch.odoo.com',
    'depends': ['hr','hr_contract','hr_payroll','hr_work_entry_contract','hr_payroll_account'],
    'data': [
        'security/ir.model.access.csv',
        'data/hierarchy_status_data.xml',
        'data/fuctions.xml',
        'report/report_salary_certificate_template.xml',
        'views/salary_reports.xml',
        'wizard/salary_certificate_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
        'views/res_partner_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/NPA_commune_OFS_views.xml',
        'views/tax_rate_views.xml',
        'views/hr_rule_parameter_views.xml',
        'views/hr_payslip_views.xml',
        'wizard/tax_rate_import_view.xml',
        'views/hr_addition_crates.xml',
        'views/base_calculation_views.xml',
        'views/structure_rule_wizard.xml',
        'views/payslip_run.xml',
        'views/wizard_payslip_send.xml',
        'views/setting.xml',
        'data/template_payslip.xml',

    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
