# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'D4E ch payroll data',
    'version': '14.0.0.0.1',
    'category': 'Human Resources',
    'summary': 'D4E ch payroll data',
    'description': """D4E ch payroll data""",

    'website': 'https://d4e-ch.odoo.com',
    'depends': ['d4e_ch_payroll', 'd4e_ch_payroll_report','hr_payroll','hr_work_entry','hr_contract'],
    'data': [
        'data/hr.salary.rule.category.csv',
        'data/work_entry.xml',
        'data/hr.work.entry.type.csv',
        'data/hr.payroll.structure.type.csv',
        'data/hr.payroll.structure.csv',
        'data/structure_type_relation.xml',
        'data/hr.salary.rule.csv',
        'data/hr.payslip.input.type.csv',
        'data/hr.rule.parameter.csv',
        'data/hr.rule.parameter.value.csv',
        'data/ir_rule.xml',



    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
