# -*- coding: utf-8 -*-

import base64
from odoo import api, models

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def generate_email(self, res_ids, fields):
        result = super(MailTemplate, self).generate_email(res_ids, fields)
        if self.model != 'account.move':
            return result
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False
        if self.model == 'account.move':
            for record in self.env[self.model].browse(res_ids):
                inv_print_name = self._render_field('report_name', record.ids, compute_lang=True)[record.id]
                new_attachments = []
                record_dict = multi_mode and result[record.id] or result
                pdf_merge =  self.env['account.move'].sudo()._pdf_invoices_with_qr(record.ids)
                qr_report_name = 'QR_'+ inv_print_name +'.pdf'
                pdf_merge = base64.b64encode(pdf_merge)
                new_attachments.append((qr_report_name, pdf_merge))
                record_dict['attachments'] = new_attachments
        return result
