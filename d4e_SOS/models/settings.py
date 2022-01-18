# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SosSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    date_support = fields.Date('Support Date')
    module_d4e_SOS_black = fields.Boolean(string='Black_background')

    def set_values(self):
        res = super(SosSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('d4e_SOS.date_support', self.date_support)
        self.env.ref('d4e_SOS.default_sos_client').date_support = self.date_support
        return res

    @api.model
    def get_values(self):
        res = super(SosSettings, self).get_values()
        ICPsudo = self.env['ir.config_parameter'].sudo()
        date = ICPsudo.get_param('d4e_SOS.date_support')
        res.update(date_support=date)
        return res

