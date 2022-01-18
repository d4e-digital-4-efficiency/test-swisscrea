# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class HrPayslipSend(models.TransientModel):
    _name = 'hr.payslip.send'
    _inherits = {'mail.compose.message':'composer_id'}
    _description = 'Payslip Send'

    is_email = fields.Boolean('Email')
    payslip_without_email = fields.Text(compute='_compute_payslip_without_email', string='payslip(s) that will not be sent')
    is_print = fields.Boolean('Print')
    printed = fields.Boolean('Is Printed', default=False)
    payslip_ids = fields.Many2many('hr.payslip', 'account_move_account_payslip_send_rel', string='payslips')
    composer_id = fields.Many2one('mail.compose.message', string='Composer', required=True, ondelete='cascade')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,
        domain="[('model', '=', 'hr.payslip')]"
        )

    # @api.model
    # def default_get(self, fields):
    #     res_ids = self._context.get('active_ids')
    #
    #     payslips = self.env['hr.payslip'].browse(res_ids).filtered(lambda move: self.is_payslip(include_receipts=True))
    #     if not payslips:
    #         raise UserError(_("You can only send payslips."))
    #
    #     composer = self.env['mail.compose.message'].create({
    #         'composition_mode': 'comment' if len(res_ids) == 1 else 'mass_mail',
    #     })
    #     res.update({
    #         'payslip_ids': res_ids,
    #         'composer_id': composer.id,
    #     })
    #     return res

    @api.onchange('payslip_ids')
    def _compute_composition_mode(self):
        for wizard in self:
            wizard.composer_id.composition_mode = 'comment' if len(wizard.payslip_ids) == 1 else 'mass_mail'

    @api.onchange('template_id')
    def onchange_template_id(self):
        for wizard in self:
            if wizard.composer_id:
                wizard.composer_id.template_id = wizard.template_id.id
                wizard._compute_composition_mode()
                wizard.composer_id.onchange_template_id_wrapper()
                # 'hr.payslip.run'
        if (len(self._context.get('active_ids')) == 1) and (self._context.get('active_model') == 'hr.payslip'):
            paslip_ids = self.env['hr.payslip'].browse(self._context.get('active_ids'))
            self.partner_ids = paslip_ids.employee_id.address_home_id

    @api.onchange('is_email')
    def onchange_is_email(self):
        if self.is_email:
            res_ids = self._context.get('active_ids')
            if not self.composer_id:
                self.composer_id = self.env['mail.compose.message'].create({
                    'composition_mode': 'comment' if len(res_ids) == 1 else 'mass_mail',
                    'template_id': self.template_id.id
                })
            else:
                self.composer_id.composition_mode = 'comment' if len(res_ids) == 1 else 'mass_mail'
                self.composer_id.template_id = self.template_id.id
                self._compute_composition_mode()
            self.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    def _compute_payslip_without_email(self):
        for wizard in self:
            if wizard.is_email and len(wizard.payslip_ids) > 1:
                payslips = self.env['hr.payslip'].search([
                    ('id', 'in', self.env.context.get('active_ids')),
                    ('partner_id.email', '=', False)
                ])
                if payslips:
                    wizard.payslip_without_email = "%s\n%s" % (
                        _("The following payslip(s) will not be sent by email, because the customers don't have email address."),
                        "\n".join([i.name for i in payslips])
                        )
                else:
                    wizard.payslip_without_email = False
            else:
                wizard.payslip_without_email = False

    def _send_email(self):
        if self.is_email:
            # with_context : we don't want to reimport the file we just exported.
            composer = self.composer_id.with_context(no_new_payslip=True, mail_notify_author=self.env.user.partner_id in self.composer_id.partner_ids)
            composer.send_mail()
            if self.env.context.get('mark_payslip_as_sent'):
                #Salesman send posted payslip, without the right to write
                #but they should have the right to change this flag
                self.mapped('payslip_ids').sudo().write({'is_move_sent': True})

    def _print_document(self):
        """ to override for each type of models that will use this composer."""
        self.ensure_one()
        action = self.payslip_ids.action_payslip_print()
        action.update({'close_on_report_download': True})
        return action

    def send_and_print_action(self):
        self.ensure_one()
        # Send the mails in the correct language by splitting the ids per lang.
        # This should ideally be fixed in mail_compose_message, so when a fix is made there this whole commit should be reverted.
        # basically self.body (which could be manually edited) extracts self.template_id,
        # which is then not translated for each customer.
        if self.composition_mode == 'mass_mail' and self.template_id:
            active_ids = self.env.context.get('active_ids', self.res_id)
            if self._context.get('active_model') == 'hr.payslip':
                active_records = self.env[self.model].browse(active_ids)
            elif  self._context.get('active_model') == 'hr.payslip.run' :
                active_records = self.env['hr.payslip.run'].browse(active_ids).slip_ids
            else:
                active_records = self.env[self.model].browse(active_ids)
            langs = active_records.mapped('employee_id.address_home_id.lang')
            default_lang = get_lang(self.env)
            for lang in (set(langs) or [default_lang]):
                active_ids_lang = active_records.filtered(lambda r: r.employee_id.address_home_id.lang == lang).ids
                self_lang = self.with_context(active_ids=active_ids_lang, lang=lang)
                self_lang.onchange_template_id()
                self_lang.attachment_ids.unlink()
                self_lang._send_email()
        else:
            self._send_email()
        if self.is_print:
            return self._print_document()
        return {'type': 'ir.actions.act_window_close'}

    def save_as_template(self):
        self.ensure_one()
        self.composer_id.save_as_template()
        self.template_id = self.composer_id.template_id.id
        action = _reopen(self, self.id, self.model, context=self._context)
        action.update({'name': _('Send payslip')})
        return action
