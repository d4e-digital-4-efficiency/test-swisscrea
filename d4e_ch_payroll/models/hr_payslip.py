#-*- coding:utf-8 -*-

import base64
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo import api, models, fields, _
from datetime import datetime
import itertools
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, ResultRules
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang
from odoo.tools.float_utils import  float_round
import math


class Payslips(BrowsableObject):
    """a class that will be used into the python code, mainly for usability purposes"""

    def sum(self, code, from_date, to_date=None):
        if to_date is None:
            to_date = fields.Date.today()
        self.env.cr.execute("""SELECT sum(case when hp.credit_note IS NOT TRUE then (pl.total) else (-pl.total) end)
                    FROM hr_payslip as hp, hr_payslip_line as pl
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                    (self.employee_id, from_date, to_date, code))
        res = self.env.cr.fetchone()
        return res and res[0] or 0.0

    def rule_parameter(self, code):
        return self.env['hr.rule.parameter']._get_parameter_from_code_customer(code, self.dict.date_to)

    def sum_category(self, code, from_date, to_date=None):
        if to_date is None:
            to_date = fields.Date.today()

        self.env['hr.payslip'].flush(['credit_note', 'employee_id', 'state', 'date_from', 'date_to'])
        self.env['hr.payslip.line'].flush(['total', 'slip_id', 'category_id'])
        self.env['hr.salary.rule.category'].flush(['code'])

        self.env.cr.execute("""SELECT sum(case when hp.credit_note is not True then (pl.total) else (-pl.total) end)
                    FROM hr_payslip as hp, hr_payslip_line as pl, hr_salary_rule_category as rc
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id
                    AND rc.id = pl.category_id AND rc.code = %s""",
                    (self.employee_id, from_date, to_date, code))
        res = self.env.cr.fetchone()
        return res and res[0] or 0.0

    @property
    def paid_amount(self):
        return self.dict._get_paid_amount()


class HrPayslipLineCopy(models.Model):
    _name = 'hr.payslip.line.copy'
    _description = 'Payslip Line'
    # _order = 'contract_id, sequence, code'

    name = fields.Char(required=False)
    name_copy = fields.Char(required=False , string='name')
    note = fields.Text(string='Description')
    # sequence = fields.Integer(required=False, index=True, default=5,
    #                           help='Use to arrange calculation sequence')
    sequence_copy = fields.Integer(required=False,  string='sequence',index=True, default=5,
                              help='Use to arrange calculation sequence')
    code = fields.Char(required=False,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.")
    code_copy = fields.Char(required=False,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.",  string='code')
    slip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=False, ondelete='cascade')
    slip_section_id = fields.Many2one('hr.payslip', string='Pay Slip', required=False, ondelete='cascade')
    slip_employee_id = fields.Many2one('hr.payslip', string='Pay Slip', required=False, ondelete='cascade')
    slip_share_id = fields.Many2one('hr.payslip', string='Pay Slip', required=False, ondelete='cascade')
    slip_line_id = fields.Many2one('hr.payslip.line', string='Pay Slip Line', required=False, ondelete='cascade')

    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=False)
    salary_rule_id_copy = fields.Many2one('hr.salary.rule', string='Rule', required=False)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=False, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=False)
    rate = fields.Float(string='Rate (%)', digits='Payroll Rate', default=100.0)
    rate_copy = fields.Float(string='Rate (%)', digits='Payroll Rate', default=100.0)
    amount = fields.Float(digits='Payroll')
    amount_copy = fields.Float(digits='Payroll')
    quantity = fields.Float(digits='Payroll', default=1.0)
    quantity_copy = fields.Float(digits='Payroll', default=1.0)
    # total = fields.Float(compute='_compute_total', string='Total', store=True)
    total = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True)
    total_copy = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True)

    amount_select = fields.Selection(related='salary_rule_id.amount_select', readonly=True)
    amount_fix = fields.Float(related='salary_rule_id.amount_fix', readonly=True)
    amount_percentage = fields.Float(related='salary_rule_id.amount_percentage', readonly=True)
    appears_on_payslip = fields.Boolean(related='salary_rule_id.appears_on_payslip', readonly=True)
    category_id = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)
    category_id_copy = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)
    partner_id = fields.Many2one(related='salary_rule_id.partner_id', readonly=True, store=True)

    date_from = fields.Date(string='From', related="slip_id.date_from", store=True)
    date_to = fields.Date(string='To', related="slip_id.date_to", store=True)
    company_id = fields.Many2one(related='slip_id.company_id')

    appears_on_payslip = fields.Boolean(related='salary_rule_id.appears_on_payslip')
    # type = fields.Char(string='type', related='salary_rule_id.rule_type')
    type = fields.Selection(string="Rule type", related='salary_rule_id.rule_type', store=True, required=False, selection=[('section', 'Section'), ('calculation basis', 'Calculation basis'),('storage data', 'Storage data'),('Headings - Employer share', 'Headings - Employer share')],)
    verification = fields.Boolean(default=False , related='salary_rule_id.verification')
    payslip_rubrique = fields.Selection([('salaire_brut', 'Salaire Brut'), ('charges_sociales', 'Charges Sociales'),
                                         ('divers', 'Divers')], string='Groupe', default=False)

    sequence = fields.Integer('Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            if int(line.slip_id.company_id.round) == 1:
                line.total = float(line.quantity) * line.amount * line.rate / 100
            elif int(line.slip_id.company_id.round) == 5:
                line.total = round((float(line.quantity) * line.amount * line.rate / 100) * 20) / 20
            else:
                  line.total = float(line.quantity) * line.amount * line.rate / 100


    @api.model
    def create(self, values):
        if values.get('code'):
            values['code_copy'] = values['code']
        if values.get('name'):
            values['name_copy'] = values['name']
        if values.get('sequence'):
            values['sequence_copy'] = values['sequence']
        if values.get('salary_rule_id'):
            values['salary_rule_id_copy'] = values['salary_rule_id']
        if values.get('category_id'):
            values['category_id_copy'] = values['category_id']
        if values.get('total'):
            values['total_copy'] = values['total']
        res = super(HrPayslipLineCopy, self).create(values)
        domain = False
        if res.slip_section_id:
            domain = [('code', '=', res.code), ('slip_id', '=', res.slip_section_id.id)]
        if res.slip_employee_id:
            domain = [('code', '=', res.code), ('slip_id', '=', res.slip_employee_id.id)]
        if res.slip_share_id:
            domain = [('code', '=', res.code), ('slip_id', '=', res.slip_share_id.id)]
        if domain:
            line = self.env['hr.payslip.line'].search(domain)
            line.update({
                'quantity': res.quantity,
                'amount': res.amount,
                'rate': res.rate,
                'total': res.total,
                'note': res.note})
        return res

    def write(self, values):
        res = super(HrPayslipLineCopy, self).write(values)
        domain = False
        if self.slip_section_id:
            domain = [('code', '=', self.code), ('slip_id', '=', self.slip_section_id.id)]
        if self.slip_employee_id:
            domain = [('code', '=', self.code), ('slip_id', '=', self.slip_employee_id.id)]
        if self.slip_share_id:
            domain = [('code', '=', self.code), ('slip_id', '=', self.slip_share_id.id)]
        if domain:
            line = self.env['hr.payslip.line'].search(domain)
            line.update({
                'quantity': self.quantity,
                'amount': self.amount,
                'rate': self.rate,
                'total': self.total,
                'note': self.note })
        return res



class Payslip(models.Model):
    _inherit = 'hr.payslip'

    date_to = fields.Date(string='To', readonly=True, required=True,compute='_compute_date_to',
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
                          states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        return {
            'name': line.name,
            'partner_id': line.partner_id.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            # 'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
            'analytic_account_id':  line.slip_id.contract_id.analytic_account_id.id or line.salary_rule_id.analytic_account_id.id,
            # 'analytic_tag_ids': line.salary_rule_id.analytical_labels or line.slip_id.contract_id.analytical_labels,
            'analytic_tag_ids': line.slip_id.contract_id.analytical_labels or line.salary_rule_id.analytical_labels
        }

    @api.onchange('date_from')
    def _compute_date_to (self):
        for element in self:
            element.date_to = (element.date_from + relativedelta(months=+1, day=1, days=-1))


    line_ids_cp = fields.One2many('hr.payslip.line', 'slip_id', compute=False, store=True,
                               string='Payslip Lines', readonly=True, domain=[('appears_on_payslip', '=', True)])

    wage_type = fields.Selection([('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')], default='monthly')

    line_ids_employee_section_ids = fields.One2many('hr.payslip.line.copy', 'slip_section_id' ,
                                              string='Payslip Lines', readonly=False)
    # line_ids_employee_section_ids = fields.One2many('hr.payslip.line.copy', 'slip_section_id' ,
    #                                           string='Payslip Lines',readonly=False)

    # line_ids_employee_basis_ids = fields.One2many('hr.payslip.line.copy', 'slip_employee_id',
    #                                           string='Payslip Lines', readonly=False, domain=[('appears_on_payslip', '=', True), ('type', '=', 'calculation basis')])
    line_ids_employee_basis_ids = fields.One2many('hr.payslip.line.copy', 'slip_employee_id',
                                              string='Payslip Lines', readonly=False)

    # line_ids_employee_share_ids = fields.One2many('hr.payslip.line.copy', 'slip_share_id',
    #                                           string='Payslip Lines', readonly=False, domain=[('appears_on_payslip', '=', True), ('type', '=', 'Headings - Employer share')])
    line_ids_employee_share_ids = fields.One2many('hr.payslip.line.copy', 'slip_share_id',
                                              string='Payslip Lines', readonly=False)
    date_from_year = fields.Char(compute='get_date_from_year', store=True)

    def compute_sheet(self):
        payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
        # delete old payslip lines
        payslips.line_ids.unlink()
        for payslip in payslips:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
            payslip._onchange_worked_days_inputs()
        return True

    @api.depends('date_from')
    def get_date_from_year(self):
        for rec in self:
            rec.date_from_year = str(rec.date_from)[:4]

    def update_hr_payslip_lines_copy(self):
        for hr_payslip in self:
            hr_payslip.get_ligne_tab()

    def get_ligne_tab(self):
        hr_payslip_line_ids = self.env['hr.payslip.line'].search([('slip_id', '=', self.id)])
        for line in hr_payslip_line_ids:
            if line.salary_rule_id.rule_type == 'section' and ((line.amount > 0) or (line.amount < 0)):
                vals = {
                'sequence': line.sequence,
                'code': line.code,
                'name': line.name,
                'salary_rule_id': line.salary_rule_id.id,
                'amount': line.amount,
                'quantity': line.quantity,
                'rate': line.rate,
                'slip_section_id' : self.id,
                'note': line.note,
                'verification': line.verification,
                'payslip_rubrique': line.payslip_rubrique
                }


            if line.salary_rule_id.rule_type == 'Headings - Employer share' and ((line.amount > 0) or (line.amount < 0)):
                vals = {
                'sequence': line.sequence,
                'code': line.code,
                'name': line.name,
                'salary_rule_id': line.salary_rule_id.id,
                'amount': line.amount,
                'quantity': line.quantity,
                'rate': line.rate,
                'slip_share_id': self.id,

                'note': line.note,
                'verification': line.verification,
                'payslip_rubrique': line.payslip_rubrique
                }
            if line.salary_rule_id.rule_type == 'calculation basis'and ((line.amount > 0) or (line.amount < 0)):
                vals = {
                'sequence': line.sequence,
                'code': line.code,
                'name': line.name,
                'salary_rule_id': line.salary_rule_id.id,
                'amount': line.amount,
                'quantity': line.quantity,
                'rate': line.rate,
                'slip_employee_id': self.id,
                'note': line.note,
                'verification': line.verification,
                'payslip_rubrique': line.payslip_rubrique
                }
            self.env['hr.payslip.line.copy'].create(vals)

    def action_payslip_cancel(self):
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        moves.unlink()
        self.write({'state': 'cancel'})
        self.mapped('payslip_run_id').action_close()
        return True

    def get_group_vals(self, group, list1, pos_name, pos_total, total_net):
        listKeys = ['sequence', 'code', 'name', 'salary_rule_id', 'contract_id', 'employee_id', 'amount', 'quantity',
                    'rate', 'slip_id', 'note', 'type'
            , 'verification', 'payslip_rubrique', 'code_copy', 'name_copy', 'sequence_copy', 'salary_rule_id_copy']
        d1 = {}
        for val in listKeys:
            if val == 'name':
                if group:
                    d1[val] = group.capitalize().replace('_',' ')
                else:
                    d1[val] = False
            else:
                d1[val] = False
        d1['display_type'] = 'line_section'
        tuple1 = (0, 0, d1)
        total = 0
        pos = pos_total
        for element in list1:
            for d in element:
                if isinstance(d, dict) and d['payslip_rubrique'] == group:
                    total += float(d['quantity']) * d['amount'] * d['rate'] / 100
                    pos += 1
        d2 = {}
        for val in listKeys:
            # if val == 'amount':
            #     d2[val] = total
            if val == 'name':
                if group:
                    if int(self.env['res.company'].browse(self._context.get('allowed_company_ids')).round) == 1:
                        d2[val] = 'Total ' + group.replace('_',' ') + ':  ' + str(round(total, 2))
                    elif int(self.env['res.company'].browse(self._context.get('allowed_company_ids')).round) == 5:
                        d2[val] = 'Total ' + group.replace('_',' ') + ':  ' + str(round(total*20)/20)
                else:
                    if int(self.env['res.company'].browse(self._context.get('allowed_company_ids')).round) == 1:
                        d2[val] = 'Total '+ str(round(total, 2))
                    elif int(self.env['res.company'].browse(self._context.get('allowed_company_ids')).round) == 5:
                        d2[val] = 'Total '+ str(round(total*20)/20)
                    # d2[val] = 'Total '+ str(round(total, 2))
                    # d2[val] = 'Total '+ str(round(total*20)/20)
            else:
                d2[val] = False

        d2['display_type'] = 'line_note'
        tuple2 = (0, 0, d2)

        if total:
            if d1:
                list1.insert(pos_name, tuple1)
            list1.insert(pos + 2, tuple2)
            pos_name = pos + 3
            pos_total = pos_name - 1
            total_net += total
        return pos_name, pos_total, total_net


    @api.onchange('struct_id', 'worked_days_line_ids', 'input_line_ids','date_from')
    def _onchange_worked_days_inputs(self):
        self.line_ids_cp = [(5, 0, 0)]
        self.line_ids = [(5, 0, 0)]
        values = [(5, 0, 0)]
        line_ids_employee_section_ids_values = [(5, 0, 0)]
        line_ids_employee_basis_ids_values = [(5, 0, 0)]
        line_ids_employee_share_ids_values = [(5, 0, 0)]
        for line_vals in self._get_payslip_lines():
            if self.env['hr.salary.rule'].browse(line_vals['salary_rule_id']).appears_on_payslip:
                values.append((0, 0, line_vals))
                new_line_vals = line_vals.copy()
                if new_line_vals.get('type') == 'section':
                    new_line_vals['code_copy'] = new_line_vals['code']
                    new_line_vals['name_copy'] = new_line_vals['name']
                    new_line_vals['sequence_copy'] = new_line_vals['sequence']
                    new_line_vals['salary_rule_id_copy'] = new_line_vals['salary_rule_id']
                    new_line_vals['payslip_rubrique'] = new_line_vals['payslip_rubrique']
                    line_ids_employee_section_ids_values.append((0, 0, new_line_vals))
                if new_line_vals.get('type') == 'calculation basis':
                    new_line_vals['code_copy'] = new_line_vals['code']
                    new_line_vals['name_copy'] = new_line_vals['name']
                    new_line_vals['sequence_copy'] = new_line_vals['sequence']
                    new_line_vals['salary_rule_id_copy'] = new_line_vals['salary_rule_id']
                    new_line_vals['payslip_rubrique'] = new_line_vals['payslip_rubrique']
                    line_ids_employee_basis_ids_values.append((0, 0, new_line_vals))
                if new_line_vals.get('type') == 'Headings - Employer share':
                    new_line_vals['code_copy'] = new_line_vals['code']
                    new_line_vals['name_copy'] = new_line_vals['name']
                    new_line_vals['sequence_copy'] = new_line_vals['sequence']
                    new_line_vals['salary_rule_id_copy'] = new_line_vals['salary_rule_id']
                    new_line_vals['payslip_rubrique'] = new_line_vals['payslip_rubrique']
                    line_ids_employee_share_ids_values.append((0, 0, new_line_vals))

        groups = [False, 'salaire_brut', 'charges_sociales', 'divers']

        listToTreat = [line_ids_employee_section_ids_values]
        for l in listToTreat:
            pos_name = 1
            pos_total = 0
            total_net = 0
            for group in groups:
                pos_name, pos_total, total_net = self.get_group_vals(group, l, pos_name, pos_total, total_net)
            if total_net:
                dict1 = {}

                # dict1['name'] = 'Salaire Net: ' + str(round(total_net, 2))
                dict1['name'] = 'Salaire Net: ' + str(round(total_net *20)/20)
                dict1['display_type'] = 'line_note'
                tuple1 = (0, 0, dict1)
                l.append(tuple1)



        self.line_ids_employee_section_ids = line_ids_employee_section_ids_values
        self.line_ids_employee_basis_ids = line_ids_employee_basis_ids_values
        self.line_ids_employee_share_ids = line_ids_employee_share_ids_values
        self.line_ids = values

    def _compute_basic_net(self):
        for payslip in self:
            reslt = 0
            for element in payslip.line_ids_employee_section_ids:
                if element.name and ("Salaire Net" in element.name):
                    if element.name[13:]:
                        reslt = float(element.name[13:])
            payslip.net_wage = reslt
            payslip.basic_wage = 0

    @api.onchange('struct_id')
    def _d4e_onchange_struct_id(self):
        if self.struct_id :
            self.wage_type = self.struct_id.type_id.wage_type
            if self.struct_id.input_line_type_ids:
                for line in self.struct_id.input_line_type_ids:
                    if line.id not in self.input_line_ids.mapped('input_type_id').ids:
                        self.env['hr.payslip.input'].create({
                                                        'input_type_id': line.id,
                                                        'payslip_id': self.id,
                                                    })
            else:
                self.input_line_ids = [(5, 0, 0)]

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        work_entry_type_ids = []
        contract = self.contract_id
        hours_per_day = self._get_worked_day_lines_hours_per_day()

        unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids
        paid_work_entry_types = self.env['hr.work.entry.type'].search([]) - unpaid_work_entry_types
        all_work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(all_work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        paid_amount = self._get_contract_wage()
        for work_entry_type, h in work_hours_ordered:
            work_entry_type_ids.append(work_entry_type)
        #table_worked_days_from_structure
        lines_worked = self.env['hr.payroll.structure'].search([('name', '=', self.struct_id.name)]).unpaid_work_entry_type_ids
        for elem in lines_worked:
            if elem.id not in work_entry_type_ids:
                attendance_line = {
                    'sequence': elem.sequence,
                    'work_entry_type_id': elem.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'hourly_rate': 0.0 if contract.wage_type != "hourly" else contract.hourly_wage,
                    'amount': 0.0,
                    'visible_in_payslip': elem.visible_in_payslip,
                }
                res.append(attendance_line)
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            if work_entry_type.visible_in_payslip:
                # is_paid = work_entry_type_id not in unpaid_work_entry_types
                work_hours = False
                for k, v in all_work_hours.items():
                    if k == work_entry_type.id and k in paid_work_entry_types.ids:
                        work_hours = v
                days = round(hours / hours_per_day, 5) if hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    days += add_days_rounding
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)
                if self.contract_id.wage_type == "hourly":
                    amount = self.contract_id.hourly_wage * hours
                else:
                    amount = hours * paid_amount / work_hours if work_hours else 0.0
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': day_rounded,
                    'number_of_hours': hours,
                    'hourly_rate': 0.0 if contract.wage_type != "hourly" else contract.hourly_wage,
                    'amount': amount,
                    'visible_in_payslip': work_entry_type.visible_in_payslip
                }
                res.append(attendance_line)
        return res


    # def _get_localdict_1(self):
    #     self.ensure_one()
    #     worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
    #     inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
    #     inputs_dict_2 = {}
    #     for line in self.input_line_ids:
    #         if line.code:
    #             if not inputs_dict_2.get(line.code):
    #                 inputs_dict_2[line.code] = (line)
    #             else:
    #                 inputs_dict_2[line.code] += line
    #     inputs_dict = inputs_dict_2
    #     employee = self.employee_id
    #     contract = self.contract_id
    #
    #     localdict = {
    #         **self._get_base_local_dict(),
    #         **{
    #             'categories': BrowsableObject(employee.id, {}, self.env),
    #             'rules': BrowsableObject(employee.id, {}, self.env),
    #             'payslip': Payslips(employee.id, self, self.env),
    #             'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
    #             'inputs': InputLine(employee.id, inputs_dict, self.env),
    #             'employee': employee,
    #             'contract': contract,
    #             'result_rules': ResultRules(employee.id, {}, self.env)
    #         }
    #     }
    #     table_calcul_base = {}
    #     if employee:
    #         # employee.get_salary_by_rule()
    #         for line in employee.employee_id_month_ids:
    #             table_calcul_base[line.salary_rule_id.code] = {
    #                 'january': line.january or 0.00,
    #                 'february': line.february or 0.00,
    #                 'march': line.march or 0.00,
    #                 'avril': line.avril or 0.00,
    #                 'may': line.may or 0.00,
    #                 'june': line.june or 0.00,
    #                 'july': line.july or 0.00,
    #                 'august': line.august or 0.00,
    #                 'september': line.september or 0.00,
    #                 'october': line.october or 0.00,
    #                 'november': line.november or 0.00,
    #                 'december': line.december or 0.00,
    #             }
    #     localdict['table_calcul_base'] = table_calcul_base
    #
    #     return localdict
    #
    # def _get_localdict_2(self, localdict):
    #
    #     line_rate = self.env['tax.rate'].search([])
    #     # print('line_rate: ', line_rate)
    #     perception_scale = []
    #     for element in line_rate:
    #         if element.perception_scale not in perception_scale and element.perception_scale:
    #             perception_scale.append(element.perception_scale)
    #     target_list = []
    #     compteur = 1
    #     for ps in perception_scale:
    #         date_val_str = '01-01-1900'
    #         date_val_date = datetime.strptime(date_val_str, '%m-%d-%Y').date()
    #         target_element = False
    #         # is_base = self.env['hr.payslip.line'].search([('code', '=', 'IS_BASE')]).amount
    #         for i in range(compteur, len(line_rate)):
    #             element = line_rate[i]
    #             if element.perception_scale and ps == element.perception_scale and element.validity_start_date:
    #                 if element.validity_start_date > date_val_date:
    #                     date_val_date = element.validity_start_date
    #                     target_element = element
    #                 compteur = i
    #             elif ps != element.perception_scale and target_element:
    #                 break
    #         if target_element:
    #             target_list.append(target_element)
    #         # print('target_list:', target_list)
    #     retenue_impot = {}
    #     for element in target_list:
    #         retenue_impot[element.perception_scale] = {
    #             'canton': element.code_canton or False,
    #             'impot ecclésiastique': element.church_tax or False,
    #             'impot': element.taxes_percent or 0.00,
    #         }
    #     localdict['retenue_impot'] = retenue_impot
    #
    #     return localdict
    #
    #
    # def _get_localdict(self):
    #     self.ensure_one()
    #     worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
    #     inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
    #     inputs_dict_2 = {}
    #     for line in self.input_line_ids:
    #         if line.code:
    #             if not inputs_dict_2.get(line.code):
    #                 inputs_dict_2[line.code] = (line)
    #             else:
    #                 inputs_dict_2[line.code] += line
    #     inputs_dict = inputs_dict_2
    #     employee = self.employee_id
    #     contract = self.contract_id
    #     localdict = {
    #         **self._get_base_local_dict(),
    #         **{
    #             'categories': BrowsableObject(employee.id, {}, self.env),
    #             'rules': BrowsableObject(employee.id, {}, self.env),
    #             'payslip': Payslips(employee.id, self, self.env),
    #             'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
    #             'inputs': InputLine(employee.id, inputs_dict, self.env),
    #             'employee': employee,
    #             'contract': contract,
    #             'result_rules': ResultRules(employee.id, {}, self.env)
    #         }
    #     }
    #
    #     localdict = self._get_localdict_1()
    #     self._get_localdict_2(localdict)
    #
    #     return localdict

    def _get_localdict(self):
        self.ensure_one()
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
        inputs_dict_2 = {}
        for line in self.input_line_ids:
            if line.code:
                if not inputs_dict_2.get(line.code):
                    inputs_dict_2[line.code] = (line)
                else:
                    inputs_dict_2[line.code] += line
        inputs_dict = inputs_dict_2
        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, {}, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract,
                'result_rules': ResultRules(employee.id, {}, self.env)
            }
        }
        table_calcul_base = {}
        if employee:
            # employee.get_salary_by_rule()
            for line in employee.employee_id_month_ids:
                table_calcul_base[line.salary_rule_id.code] = {
                    'january': line.january or 0.00,
                    'february': line.february or 0.00,
                    'march': line.march or 0.00,
                    'avril': line.avril or 0.00,
                    'may': line.may or 0.00,
                    'june': line.june or 0.00,
                    'july': line.july or 0.00,
                    'august': line.august or 0.00,
                    'september': line.september or 0.00,
                    'october': line.october or 0.00,
                    'november': line.november or 0.00,
                    'december': line.december or 0.00,
                }
        localdict['table_calcul_base'] = table_calcul_base
        target_list = []
        tax_base = {}
        line_rate = self.env['tax.rate'].search([('perception_scale' ,'=', contract.tabelle)], order="validity_start_date desc, monthly_taxable_income asc")
        target_element = False
        for i in range(0, len(line_rate)):
        # for i in range(0, 10):
            element = line_rate[i]
            # if element.perception_scale == contract.canton :
            target_element = element
            if target_element:
                target_list.append(target_element)

        for element in target_list:
            # if tax_base[element] in tax_base:
            #     tax_base[element.perception_scale] = {
            #             'canton': element.code_canton or False,
            #             'impot ecclésiastique': element.church_tax or False,
            #             'impot': element.taxes_percent or 0.00,
            #             'revenue': element.monthly_taxable_income or 0.00,
            #         }
            # if tax_base[element] in tax_base:
                tax_base[element.id] = {
                        'perception_scale': element.perception_scale or False,
                        'canton': element.code_canton or False,
                        'impot ecclésiastique': element.church_tax or False,
                        'impot': element.taxes_percent or 0.00,
                        'revenue': element.monthly_taxable_income or 0.00,
                    }
        # print (tax_base)

        localdict['tax_base'] = tax_base





        # line_rate = self.env['tax.rate'].search([])
        # # print('line_rate: ', line_rate)
        # perception_scale = []
        # for element in line_rate:
        #     if element.perception_scale not in perception_scale and element.perception_scale:
        #         perception_scale.append(element.perception_scale)
        # target_list = []
        # compteur = 1
        # for ps in perception_scale:
        #     date_val_str = '01-01-1900'
        #     date_val_date = datetime.strptime(date_val_str, '%m-%d-%Y').date()
        #     target_element = False
        #     # is_base = self.env['hr.payslip.line'].search([('code','=', 'IS_BASE'),]).amount
        #     for i in range(compteur, len(line_rate)):
        #         element = line_rate[i]
        #         if element.perception_scale and ps == element.perception_scale and element.validity_start_date:
        #             if element.validity_start_date > date_val_date:
        #                 date_val_date = element.validity_start_date
        #                 target_element = element
        #             compteur = i
        #         elif ps != element.perception_scale and target_element:
        #             break
        #     if target_element:
        #         target_list.append(target_element)
        #     # print('target_list:', target_list)
        # retenue_impot = {}
        # for element in target_list:
        #     retenue_impot[element.perception_scale] = {
        #         'canton': element.code_canton or False,
        #         'impot ecclésiastique': element.church_tax or False,
        #         'impot': element.taxes_percent or 0.00,
        #     }
        # localdict['retenue_impot'] = retenue_impot
        #

        return localdict

    def read(self, fields, load='_classic_read'):
        if (len(self) == 1) and self.employee_id:
            self.employee_id.get_salary_by_rule()
        if ((len(self) == 1) and (self.state == 'draft') ):
            self._onchange_worked_days_inputs()
        return super(Payslip, self).read(fields, load=load)



    def action_payslip_done(self):
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state': 'done'})
        self.mapped('payslip_run_id').action_close()
        # Validate work entries for regular payslips (exclude end of year bonus, ...)
        regular_payslips = self.filtered(lambda p: p.struct_id.type_id.default_struct_id == p.struct_id)
        for regular_payslip in regular_payslips:
            work_entries = self.env['hr.work.entry'].search([
                ('date_start', '<=', regular_payslip.date_to),
                ('date_stop', '>=', regular_payslip.date_from),
                ('employee_id', '=', regular_payslip.employee_id.id),
            ])
            work_entries.action_validate()


        for slip in self.browse(self.ids):
            perception_scale = slip.employee_id.perception_scale
            payslip_year = str(slip.date_from.year)
            if perception_scale:
                line = slip.employee_id.cumulative_salary_lines.filtered(lambda line: line.perception_scale == perception_scale and line.year == payslip_year)
                if line:
                    line.write({'cumulative_salary': line.cumulative_salary + slip.contract_id.wage})
                else:
                    self.env['cumulative.salary'].create({'emp_id': slip.employee_id.id,
                                                          'perception_scale': slip.employee_id.perception_scale,
                                                          'cumulative_salary': slip.contract_id.wage,
                                                          'year': payslip_year,
                                                            })

        self._action_create_account_move()


    #send_mail
    def send_mail_condition (self):
        if self.env.context.get('payslip_generate_pdf') :
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.sudo()._render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                # Sudo to allow payroll managers to create document.document without access to the
                # application
                attachment = self.env['ir.attachment'].sudo().create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodebytes(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })

                # Send email to employees
                subject = '%s, a new payslip is available for you' % (payslip.employee_id.name)
                template = self.env.ref('hr_payroll.mail_template_new_payslip', raise_if_not_found=False)
                if template:
                    email_values = {
                        'attachment_ids': attachment,
                        }
                    template.send_mail(
                        payslip.id,
                        email_values=email_values,
                        notif_layout='mail.mail_notification_light')

    def monthly_taxable_income_interval(self, monthly_taxable_income):
        dix = [1, 10, 100, 1000, 10000, 100000, 1000000]
        x = str(int(monthly_taxable_income))
        ind = len(x)-1 if len(x)>0 else 0
        deb = int(x[0]) * dix[ind]
        end = (int(x[0])+1) * dix[ind]
        return [float(deb), float(end)]

    def compute_fetch_taux(self, code_canton, year, monthly_taxable_income, perception_scale):
        """called in the salary rules :
                        result = payslip.env['hr.payslip'].compute_fetch_taux('GE', 2021, 100.0, 'HE')
                    """
        args = []
        res = []
        interval = self.monthly_taxable_income_interval(monthly_taxable_income)
        if code_canton:
            args.append(('code_canton', '=', code_canton))
        if monthly_taxable_income:
            args.append(('monthly_taxable_income', '>=', float(interval[0])))
            args.append(('monthly_taxable_income', '<', float(interval[1])))
        if perception_scale:
            args.append(('perception_scale', '=', perception_scale))
        tax_rate = self.env['tax.rate'].search(args, order='monthly_taxable_income asc')
        if year:
            for line in tax_rate:
                if not (line.validity_start_date.year == year):
                    tax_rate -= line
        if len(tax_rate) > 0 and len(args) > 0:
            lst = []
            for elem in tax_rate:
                lst.append(elem.monthly_taxable_income)
            if float(monthly_taxable_income) in lst:
                x = lst.index(float(monthly_taxable_income))
                return tax_rate[x].taxes_percent
            else:
                lst.append(float(monthly_taxable_income))
                lst = sorted(lst, key = float)
                x = lst.index(float(monthly_taxable_income)) - 1
                if x >= 0:
                    return tax_rate[x].taxes_percent
                else:
                    return 0.0
        else:
            return 0.0


    def _get_base_local_dict(self):
        res = super(Payslip, self)._get_base_local_dict()
        res.update({
            'compute_current_date': compute_current_date,
        })
        return res

    def _get_payslip_lines(self):
        self.ensure_one()

        localdict = self.env.context.get('force_payslip_localdict', None)
        if localdict is None:
            localdict = self._get_localdict()

        rules_dict = localdict['rules'].dict
        result_rules_dict = localdict['result_rules'].dict

        blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

        result = {}

        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            if rule.id in blacklisted_rule_ids:
                continue
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                # check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                # set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                # Retrieve the line name in the employee's lang
                employee_lang = self.employee_id.sudo().address_home_id.lang
                # This actually has an impact, don't remove this line
                context = {'lang': employee_lang}
                if rule.code in ['BASIC', 'GROSS', 'NET']:  # Generated by default_get (no xmlid)
                    if rule.code == 'BASIC':
                        rule_name = _('Basic Salary')
                    elif rule.code == "GROSS":
                        rule_name = _('Gross')
                    elif rule.code == 'NET':
                        rule_name = _('Net Salary')
                else:
                    rule_name = rule.with_context(lang=employee_lang).name
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'salary_rule_id': rule.id,
                    'contract_id': localdict['contract'].id,
                    'employee_id': localdict['employee'].id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                    'note': rule.note,
                    'type': rule.rule_type,
                    'verification': rule.verification,
                    'payslip_rubrique': rule.payslip_rubrique
                }
        list_delete = []
        for line in result.values():
            if line['amount'] == 0.0:
                list_delete.append(line['code'])

        new_result = {}
        for element in result:
            if element not in list_delete:
                new_result[element] = result[element]
        return new_result.values()

    def action_payslip_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        if self.env.context.get('payslip_generate_pdf'):
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.sudo()._render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                # Sudo to allow payroll managers to create document.document without access to the
                # application
                attachment = self.env['ir.attachment'].sudo().create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodebytes(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })

        self.ensure_one()
        template = self.env.ref('hr_payroll.mail_template_new_payslip', raise_if_not_found=False)
        if template:
            # email_values = {
            #     'attachment_ids': [(4, attachment.id)]
            # }
            # mail = template.send_mail(
            #     self.id,
            #     email_values=email_values,
            #     notif_layout='mail.mail_notification_light')
            # attach_mail_ids = self.env['mail.mail'].browse(mail).attachment_ids

            lang = template._render_lang(self.ids)[self.id]

        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('d4e_ch_payroll.account_payslip_send_wizard_form', raise_if_not_found=False)
        if len(self) == 1:
            ctx = dict(
                default_model='hr.payslip',
                default_res_id=self.id,
                default_attachment_ids = [attachment.id],
                # For the sake of consistency we need a default_res_model if
                # default_res_id is set. Not renaming default_model as it can
                # create many side-effects.
                default_res_model='hr.payslip',
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='comment',
                mark_invoice_as_sent=True,
                custom_layout="mail.mail_notification_paynow",
                # model_description=self.with_context(lang=lang).type_name,
                force_email=True
            )
        else:
            ctx = dict(
                default_model='hr.payslip',
                default_res_id=self.id,
                # For the sake of consistency we need a default_res_model if
                # default_res_id is set. Not renaming default_model as it can
                # create many side-effects.
                default_res_model='hr.payslip',
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='mass_mail',
                mark_invoice_as_sent=True,
                custom_layout="mail.mail_notification_paynow",
                # model_description=self.with_context(lang=lang).type_name,
                force_email=True)
        return {
            'name': _('Send Payslip'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
def compute_current_date():
    return datetime.now()


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    appears_on_payslip = fields.Boolean(related='salary_rule_id.appears_on_payslip')
    # type = fields.Char(string='type', related='salary_rule_id.rule_type')
    type = fields.Selection(string="Rule type", related='salary_rule_id.rule_type', store=True, required=True, selection=[('section', 'Section'), ('calculation basis', 'Calculation basis'),('storage data', 'Storage data'),('Headings - Employer share', 'Headings - Employer share')],)
    verification = fields.Boolean(default=False , related='salary_rule_id.verification')
    payslip_rubrique = fields.Selection([('salaire_brut', 'Salaire Brut'), ('charges_sociales', 'Charges Sociales'),
                                         ('divers', 'Divers')], string='Groupe', default=False)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            if int(line.slip_id.company_id.round) == 1:
                line.total = float(line.quantity) * line.amount * line.rate / 100
            elif int(line.slip_id.company_id.round) == 5:
                line.total = round((float(line.quantity) * line.amount * line.rate / 100) * 20) / 20
            else:
                line.total = float(line.quantity) * line.amount * line.rate / 100



class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    hourly_rate = fields.Monetary("taux horaire")
    visible_in_payslip = fields.Boolean(related='work_entry_type_id.visible_in_payslip')


    @api.onchange('number_of_hours')
    def _onchange_number_of_hours(self):
        if self.number_of_hours:
            if not self.contract_id and not self.payslip_id.contract_id :
                self.amount = 0
                self.payslip_id._onchange_worked_days_inputs()
            else:
                unpaid_work_entry_types = self.payslip_id.struct_id.unpaid_work_entry_type_ids.ids
                is_paid = self.work_entry_type_id.id not in unpaid_work_entry_types
                if self.payslip_id.wage_type == "hourly":
                    self.amount = self.payslip_id.contract_id.hourly_wage * self.number_of_hours if is_paid else 0
                    self.payslip_id._onchange_worked_days_inputs()
                # else:
                #     self.amount = self.payslip_id.normal_wage * self.number_of_hours / (
                #             self.payslip_id.sum_worked_hours or 1) if self.is_paid else 0

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=False, ondelete='cascade', index=True)



class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    visible_in_payslip = fields.Boolean("Afficher dans la fiche de paie")