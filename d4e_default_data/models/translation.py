# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class IrTranslation(models.Model):
    _inherit = 'ir.translation'


    def create_or_update_translations(self, model_name=None, lang_code=None, res_id=None, src=None, value=None):
        list_lang = self.env['res.lang'].search([('active', '=', True)]).mapped('code')
        for record_id in res_id:
            if lang_code in list_lang:
                data = {
                    'type': 'model',
                    'name': model_name,
                    'lang': lang_code,
                    'res_id': record_id,
                    'src': src,
                    'value': value,
                    'state': 'inprogress',
                }
                existing_trans = self.env['ir.translation'].search([('name', '=', model_name),
                                                                    ('res_id', '=', record_id),
                                                                    ('lang', '=', lang_code)])
                if not existing_trans:
                    self.env['ir.translation'].create(data)
                else:
                    existing_trans.write(data)

