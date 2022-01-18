# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _
import time


class SaleRecapMail(models.Model):
    _name = "sale.recap.mail"


    supplier_id = fields.Many2one('res.partner', string="Supplier")
    month_year = fields.Char("Month/Year")
    recap_attach = fields.Many2one('ir.attachment', "Recap PDF")
    state = fields.Selection([('to_send','To Send'),('sent','Sent')], "State")


    def send_mails(self):
        sale_recap_mails = self.env['sale.recap.mail'].browse(self.env.context.get('active_ids'))
        template = self.env.ref('d4e_swiss_creative_2website.email_template_sale_recap_mail')
        for rec in sale_recap_mails.filtered(lambda x: x.state == 'to_send'):
            template.attachment_ids = [(6, 0, [rec.recap_attach.id])]
            if rec.supplier_id.email:
                email_values = {'email_to': rec.supplier_id.email,
                                'email_from': self.env.user.email}
                template.send_mail(rec.id, email_values=email_values, force_send=True)
                template.attachment_ids = [(3, rec.recap_attach.id)]
                rec.write({'state': 'sent'})
                time.sleep(0.5)
        return True
