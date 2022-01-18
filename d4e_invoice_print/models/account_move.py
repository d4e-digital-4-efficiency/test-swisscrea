# -*- coding: utf-8 -*-
from odoo import models, fields, http
from odoo.tools import pdf
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    print_date = fields.Datetime('Print Date')
    printed = fields.Boolean('Printed')
    sent = fields.Boolean('Sent', copy = False)
    qr_image = fields.Binary('Image',compute='_compute_qr_image')

    def _compute_qr_image(self):
        last_image= self.env['qr.image'].search([])
        if last_image:
            self.qr_image = self.env['qr.image'].search([], order="create_date desc")[0].qr_image
        else:
            self.qr_image = False

    def update_print_date(self):
        for record_id in self:
            if record_id.state != 'draft':
                record_id.write({
                    'print_date': datetime.now(),
                    'printed': True,
                })

    def print_ch_qr_bill(self):
        res = super(AccountMove, self).print_ch_qr_bill()
        self.update_print_date()
        return res

    def isr_print(self):
        res = super(AccountMove, self).isr_print()
        self.update_print_date()
        return res

    def action_invoice_print(self):
        res = super(AccountMove, self).action_invoice_print()
        self.update_print_date()
        return res

    def copy(self, default=None):
        default = dict(default or {})
        default['print_date'] = None
        default['printed'] = None
        return super(AccountMove, self).copy(default=default)

    def _pdf_invoices_with_isr(self, invoice_ids):
        pdf_docs = []
        ai_render_qweb_pdf = self.env.ref('account.account_invoices')._render_qweb_pdf
        isr_render_qweb_pdf = self.env.ref('l10n_ch.l10n_ch_isr_report')._render_qweb_pdf
        for invoice_id in self.browse(invoice_ids):
            pdf_data = ai_render_qweb_pdf(invoice_id.id)[0]
            pdf_docs.append(pdf_data)
            if invoice_id.l10n_ch_isr_valid:
                invoice_id.l10n_ch_isr_sent = True
                isr_data = isr_render_qweb_pdf(invoice_id.id)[0]
                pdf_docs.append(isr_data)
            invoice_id.update_print_date()
        pdf_merge = pdf.merge_pdf(pdf_docs)
        return pdf_merge

    def _pdf_invoices_with_qr(self, invoice_ids):
        pdf_docs = []
        ai_render_qweb_pdf = self.env.ref('account.account_invoices')._render_qweb_pdf
        qr_render_qweb_pdf = self.env.ref('l10n_ch.l10n_ch_qr_report')._render_qweb_pdf
        for invoice_id in self.browse(invoice_ids):
            pdf_data = ai_render_qweb_pdf(invoice_id.id)[0]
            pdf_docs.append(pdf_data)
            invoice_id.l10n_ch_isr_sent = True
            qr_data = qr_render_qweb_pdf(invoice_id.id)[0]
            pdf_docs.append(qr_data)
            invoice_id.update_print_date()
        pdf_merge = pdf.merge_pdf(pdf_docs)
        return pdf_merge

class QrImage(models.Model):
    _name = "qr.image"

    qr_image = fields.Binary('Image', required=True)
    name = fields.Char()