# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date, datetime

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    emp_age = fields.Integer(string="Age", compute='_compute_age')
    bool_age_18 = fields.Boolean("In the year of his 18 years", compute='_compute_bool_age')
    bool_age_25 = fields.Boolean("In the year of his 25 years", compute='_compute_bool_age')

    hierarchy_status_id = fields.Many2one('hierarchy.status',"Hierarchy Status")
    date_deb_benefic_rente = fields.Date("Date début bénéficiaire rente")
    # observation = fields.Text("Observations")
    perception_scale = fields.Char("Barème de perception")
    avs_13 = fields.Char(string="N° assurance sociale")
    cumulative_salary_lines = fields.One2many('cumulative.salary', 'emp_id')

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    private_share_service_car = fields.Monetary("Part privée voiture de service")
    lump_sum_representation_costs = fields.Monetary("Frais forfaitaires de représentation")
    allocation_for_child = fields.Monetary("Allocation pour enfant")

    employee_id_month_ids = fields.One2many('base.calcul', 'employee_id', string='employee_id_month')
    hr_payslip_number = fields.Integer('Payslip Number' , compute='get_number_salary')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", tracking=True, required=True)

    def read(self, fields, load='_classic_read'):
        if len(self) == 1:
                self.get_salary_by_rule()
        return super(HrEmployeePrivate, self).read(fields, load=load)

    @api.depends('birthday')
    def _compute_age(self):
        for emp in self:
            if emp.birthday:
                today = date.today()
                emp.emp_age = today.year - emp.birthday.year - (
                        (today.month, today.day) < (emp.birthday.month, emp.birthday.day))
            else:
                emp.emp_age = False

    @api.depends('emp_age')
    def _compute_bool_age(self):
        for emp in self:
            if emp.birthday:
                age = date.today().year - emp.birthday.year
                if age == 18:
                    emp.bool_age_18 = True
                else:
                    emp.bool_age_18 = False
                if age == 25:
                    emp.bool_age_25 = True
                else:
                    emp.bool_age_25 = False
            else:
                emp.bool_age_18 = False
                emp.bool_age_25 = False

    def compute_fetch_cumulsalaire(self, perception_scale, year):
        if self.id:
            line = self.cumulative_salary_lines.filtered(
                lambda line: line.perception_scale == perception_scale and line.year == str(year))
            if line:
                return line.cumulative_salary
        return 0.0

    def compute_upsert_AVSreportable(self, montant):
        if self.id:
            if self.contract_id:
                self.contract_id.write({'avs_ded_year': float(montant)})
        return 0.0

    # (date_from_year, '=', datetime.now().year)
    def get_number_salary(self):
        for employee in self:
            hr_payslip_number_calcul = self.env['hr.payslip'].search_count([('employee_id', '=', employee.id),
                                                                     ('state', '!=', 'cancel'),
                                                                     ('date_from_year', '=', datetime.now().year)])
            employee.hr_payslip_number = hr_payslip_number_calcul

    def get_month_salary(self, date_from):

        hr_payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', self.id),
                                                        ('date_from', '=', date_from),
                                                        ('state','!=','cancel')])
        # hr.salary.rule
        hr_payslip_line_ids = self.env['hr.payslip.line'].search([('slip_id', 'in', hr_payslip_ids.ids),'|',
                                                                  ('salary_rule_id.rule_type', '=', 'calculation basis'),('salary_rule_id.rule_type', '=', 'section')
                                                                  ])

        salary_rule_ids = [] # colummns
        for line in hr_payslip_line_ids:
            if line.salary_rule_id.name not in salary_rule_ids:
                salary_rule_ids.append(line.salary_rule_id.name)

        month_rule_total = []


        for rule_id in salary_rule_ids: #value
            total_base_rule = 0.0
            for line in hr_payslip_line_ids:
                if line.salary_rule_id and (line.salary_rule_id.name == rule_id):
                    total_base_rule += line.total
            month_rule_total.append(total_base_rule)

        final_result = dict(zip(salary_rule_ids, month_rule_total))



        return final_result, salary_rule_ids

    def get_element_month(self, element):
        if element == '01':
            return 'january'
        elif element == '02':
            return 'february'
        elif element == '03':
            return 'march'
        elif element == '04':
            return 'avril'
        elif element == '05':
            return 'may'
        elif element == '06':
            return 'june'
        elif element == '07':
            return 'july'
        elif element == '08':
            return 'august'
        elif element == '09':
            return 'september'
        elif element == '10':
            return 'october'
        elif element == '11':
            return 'november'
        elif element == '12':
            return 'december'
        else:
            return element

    def get_salary_by_rule(self):
        for element in self.employee_id_month_ids:
            # print("element.create_date : ", element.create_date , " | datetime.now() : ", datetime.now())
            difference = datetime.now() - element.create_date
            # print("difference.seconds : ", difference.seconds)
            if difference.seconds < 10:
                return
        self.employee_id_month_ids.unlink()
        month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        list_salary_per_month_rule = {}
        salary_rule_ids = []
        # month_list = ['08']
        for month in month_list:
            month_salary_result = self.get_month_salary( str(date.today().year) +'-' + month + '-01')
            list_salary_per_month_rule[month], month_salary_rule_ids = month_salary_result
            for rule in month_salary_rule_ids:
                if rule not in salary_rule_ids:
                    salary_rule_ids.append(rule)
        # print("list_salary_per_month_rule : " + str(list_salary_per_month_rule))
        # print("salary_rule_ids : " + str(salary_rule_ids))
        final_salary_rule_monthly = {}
        for rule in salary_rule_ids:
            total = 0
            # for element in list_salary_per_month_rule.values():
            for element in list_salary_per_month_rule:
                element_month = self.get_element_month(element)
                for val in list_salary_per_month_rule[element]:
                    if rule == val:
                        if rule not in final_salary_rule_monthly:
                            final_salary_rule_monthly[rule] = {
                                'salary_rule_id': rule,
                                'rule_type': self.env['hr.salary.rule'].search([('name','=', rule)]) and  self.env['hr.salary.rule'].search([('name','=', rule)])[0].rule_type or False ,
                                element_month: list_salary_per_month_rule[element][val],
                                'total' : list_salary_per_month_rule[element][val],
                            }
                        else:
                            final_salary_rule_monthly[rule][element_month] = list_salary_per_month_rule[element][val]
                            final_salary_rule_monthly[rule]['total'] += list_salary_per_month_rule[element][val]



        for month_salaire_line in final_salary_rule_monthly:
            final_salary_rule_monthly[month_salaire_line]['salary_rule_id'] = self.env["hr.salary.rule"].search([('name', '=',  final_salary_rule_monthly[month_salaire_line]['salary_rule_id'])], limit=1).id
            final_salary_rule_monthly[month_salaire_line]['employee_id'] = self.id
            new_res = self.env['base.calcul'].create(final_salary_rule_monthly[month_salaire_line])


        # print("final_salary_rule_monthly : " + str(final_salary_rule_monthly))

    partner_id = fields.Many2one('res.partner',
                                 string='Related Partner',)
    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].create({
                    'name': vals.get('name') or '',
                    'company_type': 'person',
                    'type': 'private',


                })
        vals['address_home_id'] = partner.id
        res = super(HrEmployeePrivate, self).create(vals)
        partner.write({'employee_id': res.id})
        return res



class CumulativeSalary(models.Model):
    _name = "cumulative.salary"
    _description = "Table to save salary per year and perception scale"

    year = fields.Char("year")
    perception_scale = fields.Char("Barème de perception")
    cumulative_salary = fields.Float("Cumulative Salary")
    emp_id = fields.Many2one('hr.employee')