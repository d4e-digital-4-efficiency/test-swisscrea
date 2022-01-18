# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from odoo.tools.safe_eval import safe_eval
from odoo import api, models, fields, _
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang



class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    # def action_validate(self):
    #     self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel').action_payslip_done()
    #     self.action_close()

    # def send_mail_lot(self):
    #     self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel').send_mail_condition()

    def action_payslip_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        # if self.env.context.get('payslip_generate_pdf'):
        #     for payslip in self:
        #         if not payslip.struct_id or not payslip.struct_id.report_id:
        #             report = self.env.ref('hr_payroll.action_report_payslip', False)
        #         else:
        #             report = payslip.struct_id.report_id
        #         pdf_content, content_type = report.sudo()._render_qweb_pdf(payslip.id)
        #         if payslip.struct_id.report_id.print_report_name:
        #             pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
        #         else:
        #             pdf_name = _("Payslip")
        #         # Sudo to allow payroll managers to create document.document without access to the
        #         # application
        #         attachment = self.env['ir.attachment'].sudo().create({
        #             'name': pdf_name,
        #             'type': 'binary',
        #             'datas': base64.encodebytes(pdf_content),
        #             'res_model': payslip._name,
        #             'res_id': payslip.id
        #         })

        self.ensure_one()
        template = self.env.ref('hr_payroll.mail_template_new_payslip', raise_if_not_found=False)
        # if template:
        #     email_values = {
        #         'attachment_ids': [attachment]
        #     }
        #     template.send_mail(
        #         self.id,
        #         email_values=email_values,
        #         notif_layout='mail.mail_notification_light')
        #     lang = template._render_lang(self.ids)[self.id]
        # if not template._render_lang(self.ids)[self.id]:
        lang = get_lang(self.env).code
        compose_form = self.env.ref('d4e_ch_payroll.account_payslip_send_wizard_form', raise_if_not_found=False)
        # if len(self) == 1:
        ctx = dict(
                default_model='hr.payslip',
                default_res_id=self.id,
                # For the sake of consistency we need a default_res_model if
                # default_res_id is set. Not renaming default_model as it can
                # create many side-effects.
                default_res_model='hr.payslip',
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='comment',
                mark_invoice_as_sent=True,
                custom_layout="mail.mail_notification_paynow",
                # model_description=self.with_context(lang=lang).type_name,
                force_email=True
            )

        return {
            'name': _('Send Payslip'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    def action_lot_draft(self):
        for slip in self.slip_ids:
            slip.action_payslip_cancel()
        self.state = 'draft'
