# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SosClient(models.Model):
    _name = 'sos.client'
    _description = "Module d'assistance client D4E"
    date_support = fields.Date('Support Date' ,readonly=True)
    text_sos_support = fields.Text('Text Sos', compute='_compute_text')

    @api.depends('date_support')
    def _compute_text(self):
        if self.date_support:
            self.text_sos_support = _("support up to  ") + str(self.date_support.strftime("%d-%m-%Y"))
        else:
            self.text_sos_support = _("No SOS support activated - Contact our sales department")




