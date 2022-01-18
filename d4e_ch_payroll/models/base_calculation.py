from odoo import api, fields, models, _

class BaseCalcul(models.Model):
    _name = "base.calcul"

    january = fields.Char(string='January')
    february = fields.Char(string='February')
    march = fields.Char(string='March')
    avril = fields.Char(string='Avril')
    may = fields.Char(string='May')
    june = fields.Char(string='June')
    july = fields.Char(string='July')
    august = fields.Char(string='August')
    september = fields.Char(string='September')
    october = fields.Char(string='October')
    november = fields.Char(string='November')
    december = fields.Char(string='December')
    total = fields.Char(string='Total')
    employee_id = fields.Many2one('hr.employee', string='employee')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='salary')
    rule_type = fields.Selection(string="Rule type", related=False, required=False, selection=[('section', 'Section'), ('calculation basis', 'Calculation basis'),('storage data', 'Storage data'),('Headings - Employer share', 'Headings - Employer share')],)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if("domain_custom" in self.env.context):
            args.append(('rule_type', '=', 'calculation basis'))
            print(self.env.context["domain_custom"] )
        res = super(BaseCalcul, self).search(args, offset=offset, limit=limit, order=order, count=count)

        return res








