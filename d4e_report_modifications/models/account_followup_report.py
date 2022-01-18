# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.exceptions import UserError
from datetime import datetime


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def get_html(self, options, line_id=None, additional_context=None):

        self = self.with_context(self._set_context(options))
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        templates = self._get_templates()
        report_manager = self._get_report_manager(options)
        if 'account.followup.report' in str(self):
            report_name = ''

        else:
            report_name = self._get_report_name()
        render_values = {
            'report': {
                'name': report_name,
                'summary': report_manager.summary,
                'company_name': self.env.company.name,
            },
            'options': options,
            'context': self.env.context,
            'model': self,
        }

        # render_values = {
        #     'report': {
        #         'name': self._get_report_name(),
        #         'summary': report_manager.summary,
        #         'company_name': self.env.company.name,
        #     },
        #     'options': options,
        #     'context': self.env.context,
        #     'model': self,
        # }
        if additional_context:
            render_values.update(additional_context)
        if line_id:
            headers = options['headers']
            lines = self._get_lines(options, line_id=line_id)
            template = templates['line_template']
        else:
            headers, lines = self._get_table(options)
            options['headers'] = headers
            template = templates['main_template']
        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)
        render_values['lines'] = {'columns_header': headers, 'lines': lines}

        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})

        # Render.
        html = self.env.ref(template)._render(render_values)
        if self.env.context.get('print_mode', False):
            for k, v in self._replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(b'<div class="js_account_report_footnotes"></div>',
                                self.get_html_footnotes(footnotes_to_render))
            html = html.replace(b'o_account_reports_edit_summary_pencil',
                                          b'o_account_reports_edit_summary_pencil d-none')

        return html



class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"
    _description = "Follow-up Report"


    def _get_columns_name(self, options):

        headers = [{'style':"border:none;" },
                   {'name': _('Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   # {'name': _('N° Reference'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Due Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Delay'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Expected Date'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Excluded'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Reminder N°'), 'style': 'text-align:center; white-space:nowrap; '},
                   {'name': _('Total Due'), 'class': 'number o_price_total',
                    'style': 'text-align:right; white-space:nowrap; '},
                   ]

        if self.env.context.get('print_mode'):
            headers = headers[:4] + headers[6:]
        return headers

    def _get_templates(self):
        result = super()._get_templates()
        result['main_table_header_template'] = 'd4e_report_modifications.main_table_header'
        return result

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang if self._context.get('print_mode') else self.env.user.lang or get_lang(self.env).code
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids.filtered(lambda l: l.company_id == self.env.company):
            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date', 'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = self._format_aml_name(aml.name, aml.move_id.ref, aml.move_id.name)
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                expected_pay_date = format_date(self.env, aml.expected_pay_date, lang_code=lang_code) if aml.expected_pay_date else ''
                invoice_origin = aml.move_id.invoice_origin or ''
                if aml.move_id.invoice_date_due:
                    delay = (datetime.now().date() - aml.move_id.invoice_date_due).days
                else:
                    delay = False
                reminder_number = partner.followup_level.id
                if len(invoice_origin) > 43:
                    invoice_origin = invoice_origin[:40] + '...'
                # if date_due != '':
                #     date_due_name = (datetime.strptime(date_due, '%m/%d/%Y'))
                #     date_due = date_due_name.strftime('%d.%m.%Y')
                if delay:
                    if delay < 0:
                        delay = (-1) * delay
                    delay = str(delay) + " jours"
                columns = [
                    aml.date.strftime('%d.%m.%Y'),
                    # '...............',
                    # date_due.strftime('%d.%m.%Y'),
                    date_due,
                    # followup_level
                    delay,
                    invoice_origin,
                    # move_line_name,
                    (expected_pay_date and expected_pay_date + ' ') + (aml.internal_note or ''),
                    # {'name': '', 'blocked': aml.blocked},
                    reminder_number,
                    amount,
                ]
                if self.env.context.get('print_mode'):
                    columns = columns[:3] + columns[5:]
                lines.append({
                    'id': aml.id,
                    'account_move': aml.move_id,
                    'name': '' if self.env.context.get('print_mode') else aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            if not self.env.context.get('print_mode'):
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'style': 'border-top-style: double',
                    'unfoldable': False,
                    'level': 4,
                    'columns': [{'name': v} for v in [''] * (3 if self.env.context.get('print_mode') else 5) + [total >= 0 and _('Total Due') or '', total_due]],
                })
            if total_due:
                # total_due = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                # if not self.env.context.get('print_mode'):
                #     lines.append({
                #         'id': line_num,
                #         'name': '',
                #         'class': 'total',
                #         'unfoldable': False,
                #         'level': 4,
                #         'columns': [{'name': v} for v in [''] * (4 if self.env.context.get('print_mode') else 6) + [_('Total Overdue'), total_issued]],
                #     })
                if self.env.context.get('print_mode'):
                    col_1 = [{'name': v} for v in
                     [''] * (4 if self.env.context.get('print_mode') else 5)]
                    col_1.append({'name' : total_due,'style': "border-top: 2px black solid; text-align:right;"})
                    lines.append({
                        'id': line_num,
                        'name': '',
                        # 'class': 'total_custom',
                        'style': "font-weight: bold;",
                        'unfoldable': False,
                        'level': 4,
                        'columns': col_1,
                    })
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'style': 'border-bottom-style: none; border:none;',
                'unfoldable': False,
                'level': 0,
                'columns': [{} for col in columns],
            })
        if lines:
            lines.pop()
        return lines


    def get_html(self, options, line_id=None, additional_context=None):

        if additional_context is None:
            additional_context = {}
            # additional_context['followup_line'] = self.get_followup_line(options)
        partner = self.env['res.partner'].browse(options['partner_id'])
        additional_context['partner'] = partner
        additional_context['lang'] = partner.lang or get_lang(self.env).code
        additional_context['invoice_address_id'] = self.env['res.partner'].browse(partner.address_get(['invoice'])['invoice'])
        additional_context['today'] = fields.date.today().strftime('%d.%m.%Y')
        return super(AccountFollowupReport, self).get_html(options, line_id=line_id, additional_context=additional_context)

    @api.model
    def _build_followup_summary_with_field(self, field, options):

        followup_line = self.get_followup_line(options)
        if followup_line:
            partner = self.env['res.partner'].browse(options['partner_id'])
            lang = partner.lang or get_lang(self.env).code
            summary = followup_line.with_context(lang=lang)[field]
            try:
                summary = summary % {'partner_name': partner.name,
                                     'date': format_date(self.env, fields.Date.today(), lang_code=partner.lang),
                                     # 'date': format_date(self.env, fields.Date.today().strftime('%d.%m.%Y')),
                                     'user_signature': html2plaintext(self.env.user.signature or ''),
                                     'company_name': self.env.company.name,
                                     'amount_due': formatLang(self.env, partner.total_due,
                                                              currency_obj=partner.currency_id),
                                     }
            except ValueError as exception:
                message = _(
                    "An error has occurred while formatting your followup letter/email. (Lang: %s, Followup Level: #%s) \n\nFull error description: %s") \
                          % (lang, followup_line.id, exception)
                raise ValueError(message)
            return summary
        raise UserError(_('You need a least one follow-up level in order to process your follow-up'))

class FollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'

    description = fields.Text('Printed Message', translate=True, default=lambda s: _("""
        We still have no news of your payments regarding the invoices below,
        We would be grateful if you could contact our accounting department to trace them.


            """))