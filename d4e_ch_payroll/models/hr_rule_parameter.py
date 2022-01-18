#-*- coding:utf-8 -*-

from odoo import api, models, fields, _
import ast
from odoo.exceptions import UserError

class HrSalaryRuleParameter(models.Model):
    _inherit = 'hr.rule.parameter'

    last_parameter_value = fields.Text("Last Value", compute="_get_last_parameter_value", store=True)

    category = fields.Selection(string="Category", selection=[('national data', 'National data'), ('variable', 'Variable data according to contract'),('various', 'Various')],)

    company_id = fields.Many2one('res.company', string='company')

    @api.depends('parameter_version_ids')
    def _get_last_parameter_value(self):
        for rec in self:
            vers = self.env['hr.rule.parameter.value'].search([('rule_parameter_id', '=', rec.id)], order="date_from desc")
            if vers:
                rec.last_parameter_value = vers[0].parameter_value
            else:
                rec.last_parameter_value = False

    def read(self, fields=None, load='_classic_read'):
        for rec in self:
            rec._get_last_parameter_value()
        result = super(HrSalaryRuleParameter, self).read(fields=fields, load=load)
        return result

    def _get_parameter_from_code_customer(self, code, date=None, raise_if_not_found=True):
        if not date:
            date = fields.Date.today()
        # This should be quite fast as it uses a limit and fields are indexed
        # moreover the method is cached
        rule_parameter = self.env['hr.rule.parameter.value'].search([
            ('code', '=', code),
            ('date_from', '<=', date)], limit=1)
        if rule_parameter:
            return ast.literal_eval(rule_parameter.parameter_value)
        if raise_if_not_found:
            raise UserError(_("No rule parameter with code '%s' was found for %s ") % (code, date))
        else:
            return None

class HrSalaryRuleParameterValue(models.Model):
    _inherit = 'hr.rule.parameter.value'
    company_id = fields.Many2one('res.company', string='company')

    _sql_constraints = [
        ('_unique', 'unique (rule_parameter_id, date_from, company_id)', "Two rules with the same code cannot start the same day"),
    ]
    def parameter_company_value(self):
        companies = self.env['res.company'].search([])
        companies_has_rules = self.env['hr.rule.parameter.value'].search([]).mapped('company_id')
        for company in companies:
            if company not in companies_has_rules:
                # if not self.env['hr.rule.parameter.value'].search([('company_id', '=', company.id)]):
                for value in self.env['hr.rule.parameter.value'].search([('company_id', '=', self.env.ref("base.main_company").id)]):
                    value.copy({"company_id": company.id})


