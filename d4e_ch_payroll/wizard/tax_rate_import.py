# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import base64
import io

class TaxRateImport(models.TransientModel):
    _name = 'tax.rate.import'
    _description = 'Wizard to import tax rate file'


    file = fields.Binary('Tax Rate File', required=True)
    filename = fields.Char()

    def change_format(self, amount):
        if amount > 100 :
            return amount/100
        return amount

    def import_file(self):
        if self.file:
            try:
                str_content = ''
                with io.BytesIO(base64.b64decode(self.file)) as f:
                    content = f.read()
                    str_content = content.decode('UTF-8')
            except:
                raise UserError(_('Incorrect format. Please try to save the file txt format first !'))
            for line in str_content.split("\r\n"):
                vals = {}
                # line = line.strip().replace(chr(32),'')
                line = line.strip()
                if line[:2] == '00':
                   vals={
                       'code_canton': line[2:4],
                       'perception_scale': False,
                       'church_tax': False,
                       'validity_start_date': datetime.strptime(line[19:27], '%Y%m%d').date(),
                       'monthly_taxable_income': False,
                       'francs_taxes': False,
                       'taxes_percent': False,
                   }
                elif line[:2] in ['06', '11', '12', '13']:
                   vals={
                       'code_canton': line[4:6],
                       'perception_scale': line[6:8],
                       'church_tax': False if line[:2] in ['12', '13'] else line[8],
                       'validity_start_date': datetime.strptime(line[16:24], '%Y%m%d').date(),
                       'monthly_taxable_income': self.env.company.currency_id._convert(self.change_format(int(line[24:33])), self.env.company.currency_id, self.env.company, datetime.now().date()),
                       'francs_taxes': self.change_format(int(line[45:54])),
                       'taxes_percent': int(line[54:59])/100,
                   }
                elif line[:2] == '99':
                   vals={
                       'code_canton': line[17:19],
                       'perception_scale': False,
                       'church_tax': False,
                       'validity_start_date': False,
                       'monthly_taxable_income': False,
                       'francs_taxes': False,
                       'taxes_percent': False,
                   }
                if len(vals)>0:
                    new = self.env['tax.rate'].create(vals)
            f.close()

        return {
            'name': _('Tax Rate List'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'tax.rate',
        }

