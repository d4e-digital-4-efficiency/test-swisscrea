from odoo import api, fields, models, _

class HrFunds(models.Model):
    _name = "hr.funds"


    def name_get(self):
        result = []
        for record in self:
            result.append((record.id,'%s %s' %(record.Name_of_fund_insurance,record.case_number)))
        return result

    type_of_crate = fields.Selection(string="Type of crate", selection=[('AVS/AC', 'AVS/AC'), ('LAA', 'LAA'), ('IJM', 'IJM'), ('LAAC', 'LAAC'), ('LPP', 'LPP')])
    Name_of_fund_insurance = fields.Text('Name of fund / insurance')
    case_number = fields.Text('Case number')
    customer_number = fields.Char(name="Customer number")
    contract_number = fields.Char(name="Contract number")
    street = fields.Text(name="Street ")
    zip_Location = fields.Char(name="ZIP Location")
    phone = fields.Char(name="Phone")
    e_mail = fields.Char(name="E-mail")


