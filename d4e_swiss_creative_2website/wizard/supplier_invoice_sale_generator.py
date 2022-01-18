# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby
from datetime import datetime
import base64


MONTHS = [('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),
          ('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]


class SupplierInvoiceSaleGenerator(models.Model):
    _name = "supplier.invoice.sale.generator"

    month = fields.Selection(MONTHS, string='Month', default=str(fields.Date.today().month), required=True)
    supplier_id = fields.Many2one('res.partner',"Supplier")

    def create_supp_invoice(self, supp_id=None):
        move = self.env['account.move']
        datas = []
        done_order = []
        for website in self.env['website'].search([]):
            lst = []
            lines = {}
            inv_sellers = {}
            if not(self.env.context.get('old_invoices', False)):
                for order in self.env['sale.order'].search([('state', 'in', ['sale', 'done']),('website_id', '=', website.id),('supp_invoice', '=', False)]):
                    # if order.date_order.month == int(self.month) and order.invoiceable_order():
                    if order.date_order.month == int(self.month):
                        for line in order.order_line:
                            if (not line.display_type) and line.product_id.purchase_ok and line.product_id.website_ids and line.product_id.type != 'service':
                                qty = line.product_uom_qty
                                new_line = True
                                seller = line.product_id._select_seller_with_website(quantity=line.product_uom_qty, uom_id=line.product_uom, website_id=order.website_id)
                                if not seller:
                                    raise UserError(_(
                                        "There is no vendor associated to the product %s. "
                                        "Please define a vendor for this product.") % (line.product_id.name,))
                                fpos = self.env['account.fiscal.position'].sudo().get_fiscal_position(seller.name.id)
                                taxes = line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == order.company_id)
                                taxes_id = fpos.map_tax(taxes, line.product_id, seller.name)
                                old_inv = False
                                today = fields.Date.today()
                                for o_inv in move.search([('move_type', '=', 'in_invoice'), ('company_id', '=', order.company_id.id),
                                                          ('partner_id', '=', seller.name.id), ('currency_id','=', self.env.company.currency_id.id),
                                                          ('state','=', 'draft')], order='id DESC'):
                                    if o_inv.create_date.month == int(self.month):
                                        old_inv = o_inv
                                        break
                                if old_inv:
                                    if seller.name.id not in inv_sellers.keys():
                                        inv_sellers[seller.name.id] = old_inv.id
                                    inv = old_inv
                                if seller.name.is_company:
                                    banks = seller.name.bank_ids
                                else:
                                    banks = seller.name.parent_id.bank_ids
                                if seller.name.id not in inv_sellers.keys():
                                    inv = move.create({
                                        'partner_id': seller.name.id,
                                        'partner_bank_id': banks[0].id if banks else False,
                                        'currency_id': self.env.company.currency_id.id,
                                        'move_type': 'in_invoice',
                                        'invoice_date': today,
                                        'fiscal_position_id': fpos.id,
                                        'company_id': order.company_id.id,
                                        'invoice_line_ids': [(0, 0, {
                                            'product_id': line.product_id.id,
                                            'website_id': website.id,
                                            'quantity': line.product_uom_qty,
                                            'product_uom_id': line.product_uom.id,
                                            'price_unit': seller.price / line.product_id.uom_po_id.factor_inv,
                                            'currency_id': self.env.company.currency_id.id,
                                            'partner_id': seller.name.id,
                                            'tax_ids': [(6, 0, taxes_id.ids)],
                                            'sale_line_ids': [(4, line.id)],
                                        })],
                                    })
                                    inv_sellers[seller.name.id] = inv.id
                                else:
                                    inv = move.browse(inv_sellers[seller.name.id])
                                    inv_line = inv.invoice_line_ids.filtered(
                                        lambda x: (x.product_id.id == line.product_id.id) and x.website_id.id == website.id)
                                    # if line.product_id.id in inv.invoice_line_ids.mapped('product_id').ids:
                                    if inv_line:
                                        vals = []
                                        # inv_line= inv.invoice_line_ids.filtered(lambda x: x.product_id.id == line.product_id.id)
                                        sale_line_ids = inv_line.sale_line_ids.ids
                                        copied_vals = inv_line.copy_data()[0]
                                        copied_vals['quantity'] = line.product_uom_qty + inv_line.quantity
                                        sale_line_ids.append(line.id)
                                        copied_vals['sale_line_ids'] = [(6, 0, sale_line_ids)]
                                        for l in inv.invoice_line_ids.filtered(lambda x: (x.product_id.id != line.product_id.id) or x.website_id.id != website.id):
                                            cp_vals = l.copy_data()[0]
                                            vals.append(cp_vals)

                                        inv.line_ids.unlink()
                                        inv.write({'invoice_line_ids': [(0, 0,copied_vals)]})
                                        for elm in vals:
                                            inv.write({'invoice_line_ids': [(0, 0, elm)]})

                                    else:
                                        inv.write({'invoice_line_ids':[(0, 0, {
                                            'move_id': inv.id,
                                            'product_id': line.product_id.id,
                                            'website_id': website.id,
                                            'quantity': line.product_uom_qty,
                                            'product_uom_id': line.product_uom.id,
                                            'price_unit': seller.price / line.product_id.uom_po_id.factor_inv,
                                            'partner_id': seller.name.id,
                                            'currency_id': inv.currency_id.id,
                                            'account_id': inv.journal_id.default_account_id.id,
                                            'tax_ids': [(6, 0, taxes_id.ids)],
                                            'sale_line_ids': [(4, line.id)],
                                        })]})

                                for elem in lst:
                                    if elem['product_id'] == line.product_id.id and elem['supp_id'] == seller.name.id:
                                        elem['qte'] = elem['qte'] + qty
                                        new_line = False
                                if new_line:
                                    lst.append({
                                        'product_id': line.product_id.id,
                                        'supp_id': seller.name.id,
                                        'product': line.product_id.name,
                                        'qte': qty,
                                        'unit': line.product_uom.name,
                                        'supp': seller.name.name,
                                        'price': seller.price / line.product_id.uom_po_id.factor_inv,
                                    })
                                order.write({'supp_invoice': True})
                                done_order.append(order.id)
                done_order = list(set(done_order))
            if self.env.context.get('old_invoices', False):
                for order in self.env['sale.order'].search([('state', 'in', ['sale', 'done']), ('website_id', '=', website.id)]):
                    if order.date_order.month == int(self.month) and order.id not in done_order:
                        for line in order.order_line:
                            if line.product_id.purchase_ok and line.product_id.website_ids and line.product_id.type != 'service':
                                new_line = True
                                seller = line.product_id._select_seller_with_website(quantity=line.qty_invoiced,
                                                                                     uom_id=line.product_uom,
                                                                                     website_id=order.website_id)
                                if not seller:
                                    raise UserError(_(
                                        "There is no vendor associated to the product %s."
                                        " Please define a vendor for this product.") % (line.product_id.name,))
                                for elem in lst:
                                    if elem['product_id'] == line.product_id.id and elem['supp_id'] == seller.name.id:
                                        elem['qte'] = elem['qte'] + line.product_uom_qty
                                        new_line = False
                                if new_line:
                                    lst.append({
                                        'product_id': line.product_id.id,
                                        'supp_id': seller.name.id,
                                        'product': line.product_id.name,
                                        'qte': line.product_uom_qty,
                                        'unit': line.product_uom.name,
                                        'supp': seller.name.name,
                                        'price': seller.price / line.product_id.uom_po_id.factor_inv,
                                    })

            if self.supplier_id or supp_id:
                supplier = self.supplier_id or supp_id
                lines[supplier.name] = []
                for elem in lst:
                    if elem['supp_id'] == supplier.id:
                        lines[supplier.name].append(elem)
                if len(lines[supplier.name]) == 0:
                    lines.pop(supplier.name, None)
            else:
                for k, v in groupby(lst, key=lambda l: l['supp_id']):
                    supp = self.env['res.partner'].browse(k).name
                    if lines.get(supp, False):
                        for elem in list(v):
                            lines[supp].append(elem)
                    else:
                        lines[supp] = list(v)

            if len(lines.keys())>0:
                datas.append({'website': website.name, 'currency_id': self.env.company.currency_id.name, 'lst': lines})
        return {'month': dict(self._fields['month']._description_selection(self.env)).get(self.month),
                'supplier': self.supplier_id.name or False if supp_id is None else supp_id.name,
                'data': datas}

    def print_report(self):
        self.ensure_one()
        datas = self.with_context(old_invoices=True).create_supp_invoice()
        return self.env.ref('d4e_swiss_creative_2website.action_report_supp_invoice_recap').report_action([], data=datas)

    def supp_mail_prep(self):
        month_year = dict(self._fields['month']._description_selection(self.env)).get(self.month) + '/' + str(
            datetime.now().year)
        if self.supplier_id:
            datas = self.with_context(old_invoices=True).create_supp_invoice()
            if any(len(dt['lst'][self.supplier_id.name])>0 for dt in datas['data']):
                if not self.env['sale.recap.mail'].search(
                        [('supplier_id', '=', self.supplier_id.id), ('month_year', '=', month_year),
                         ('state', '=', 'to_send')]):
                    recap_mail = self.env['sale.recap.mail'].create({
                                                                    'supplier_id': self.supplier_id.id,
                                                                    'month_year': month_year,
                                                                    'state':'to_send',
                                                                    })
                else:
                    recap_mail = self.env['sale.recap.mail'].search(
                        [('supplier_id', '=', self.supplier_id.id), ('month_year', '=', month_year),
                         ('state', '=', 'to_send')])[0]
                pdf = self.env.ref('d4e_swiss_creative_2website.action_report_supp_invoice_recap')._render_qweb_pdf([], data=datas)[0]
                filename = self.supplier_id.name + '_' + month_year + '.pdf'
                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': base64.b64encode(pdf),
                    'store_fname': filename,
                    'res_model': 'sale.recap.mail',
                    'res_id': recap_mail.id,
                    'mimetype': 'application/x-pdf'
                })
                recap_mail.write({'recap_attach': attachment.id})
        else:
            for supp in self.env['res.partner'].search([]):
                datas = self.with_context(old_invoices=True).create_supp_invoice(supp)
                if any(len(dt['lst'][supp.name])> 0 for dt in datas['data']):
                    if not self.env['sale.recap.mail'].search(
                            [('supplier_id', '=', supp.id), ('month_year', '=', month_year),
                             ('state', '=', 'to_send')]):
                        recap_mail = self.env['sale.recap.mail'].create({
                            'supplier_id': supp.id,
                            'month_year': month_year,
                            'state': 'to_send',
                        })
                    else:
                        recap_mail = self.env['sale.recap.mail'].search(
                            [('supplier_id', '=', supp.id), ('month_year', '=', month_year),
                             ('state', '=', 'to_send')])[0]
                    pdf = self.env.ref('d4e_swiss_creative_2website.action_report_supp_invoice_recap')._render_qweb_pdf([], data=datas)[0]
                    filename = supp.name + '_' + month_year + '.pdf'
                    attachment = self.env['ir.attachment'].create({
                        'name': filename,
                        'type': 'binary',
                        'datas': base64.b64encode(pdf),
                        'store_fname': filename,
                        'res_model': 'sale.recap.mail',
                        'res_id': recap_mail.id,
                        'mimetype': 'application/x-pdf'
                    })
                    recap_mail.write({'recap_attach': attachment.id})