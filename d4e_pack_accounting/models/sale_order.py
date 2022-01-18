# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    update_sequence = fields.Char(string='Update sequence')

    def action_subtotal(self):
        for l in self.order_line:
            if l.new_line:
                res = l.unlink()
        subtotal = 0
        section_1 = False
        section_2 = False
        seq = 0
        order_line = self.env["sale.order.line"].search([
            ('order_id', '=', self.id)], order="sequence")
        for line in order_line:
            if line.display_type == 'line_section':
                section_1 = True
            if line.display_type == 'line_section' and subtotal:
                section_2 = True
            if not line.display_type and section_1:
                subtotal += line.price_subtotal
            if section_2 and subtotal != 0:
                line_vals_list = {
                    'sequence': seq,
                    'name': _('Sub-Total:      ') + str("%.2f" % subtotal) + ' ' + line.currency_id.symbol,
                    'currency_id': line.currency_id.symbol,
                    'currency_id': 5,
                    'product_uom_qty': 0,
                    'display_type': 'line_sub_total',
                    'new_line': True,
                    'order_id': self.id
                }

                new_line = self.env['sale.order.line'].create(line_vals_list)
                subtotal = 0
                section_2 = False
            seq = line.sequence
        if subtotal != 0:
            line_vals_list = {
                'sequence': seq,
                'name': _('Sub-Total:      ') + str("%.2f" % subtotal) + ' ' + line.currency_id.symbol,
                'currency_id': line.currency_id.symbol,
                'currency_id': 5,
                'product_uom_qty': 0,
                'display_type': 'line_sub_total',
                'new_line': True,
                'order_id': self.id
            }
            new_line = self.env['sale.order.line'].with_context(request_from_action_subtotal=True).create(line_vals_list)

    def add_subtotal(self):
        subtotal = 0
        seq = 0
        order_line = self.env["sale.order.line"].search([
            ('order_id', '=', self.id)], order="sequence")
        for line in order_line:
            if not line.display_type:
                subtotal += line.price_subtotal
            if line.display_type == 'line_subtotal':
                seq = line.sequence
                line_vals_list = {
                    'sequence': seq,
                    'name': _('Sub-Total-manuel:      ')+str("%.2f" % subtotal) + ' ' + line.currency_id.symbol,
                    'currency_id': line.currency_id.symbol,
                    'currency_id': 5,
                    'product_uom_qty': 0,
                    'display_type': 'line_subtotal',
                    'new_line': False,
                    'order_id': self.id
                }
                new_line = line.write(
                    line_vals_list)
                subtotal = 0

    def action_subtotal_create(self):
        subtotal = 0
        section_1 = False
        section_2 = False
        seq = 0
        order_line = self.env["sale.order.line"].search([
            ('order_id', '=', self.id)])
        line_index = 1
        for line in order_line:
            line.sequence = line_index
            line_index += 1
            if line.display_type == 'line_section':
                section_1 = True
            if line.display_type == 'line_section' and subtotal:
                section_2 = True
                seq = line.sequence
            if not line.display_type and section_1:
                subtotal += line.price_subtotal
            if section_2 and subtotal != 0:
                increment_sequence_order_line = self.env["sale.order.line"].search([
                    ('order_id', '=', self.id),
                    ('sequence', '>=', line.sequence)], order="sequence DESC")
                for element in increment_sequence_order_line:
                    element.sequence = element.sequence + 2
                line_vals_list = {
                    'sequence': line_index,
                    'name': _('Sub-Total:      ') + str("%.2f" % subtotal) + ' ' + line.currency_id.symbol,
                    'currency_id': line.currency_id.symbol,
                    'currency_id': 5,
                    'product_uom_qty': 0,
                    'display_type': 'line_sub_total',
                    'new_line': True,
                    'order_id': self.id
                }
                new_line = self.env['sale.order.line'].create(line_vals_list)
                line_index += line.sequence
                subtotal = 0
                section_2 = False
            seq = line.sequence
        if subtotal != 0:
            line_vals_list = {
                'sequence': seq,
                'name': _('Sub-Total:      ') + str("%.2f" % subtotal) + ' ' + line.currency_id.symbol,
                'currency_id': line.currency_id.symbol,
                'currency_id': 5,
                'product_uom_qty': 0,
                'display_type': 'line_sub_total',
                'new_line': True,
                'order_id': self.id
            }
            new_line = self.env['sale.order.line'].with_context(request_from_action_subtotal=True).create(line_vals_list)

    def add_subtotal_create(self):
        subtotal = 0
        seq = 0
        order_line = self.env["sale.order.line"].search([
            ('order_id', '=', self.id)])
        line_index = 1
        for line in order_line:
            line_index += 1
            line.sequence = line_index
            if not line.display_type:
                subtotal += line.price_subtotal
            if line.display_type == 'line_subtotal':
                seq = line.sequence
                line_vals_list = {
                    'sequence': seq,
                    'name': _('Sub-Total-manuel:      ')+str("%.2f" % subtotal) + ' ' + line.currency_id.symbol,
                    'currency_id': line.currency_id.symbol,
                    'currency_id': 5,
                    'product_uom_qty': 0,
                    'display_type': 'line_subtotal',
                    'new_line': False,
                    'order_id': self.id
                }
                new_line = line.write(
                    line_vals_list)
                subtotal = 0

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if not self._context.get('request_from_action_subtotal'):
            for order in self:
                order.action_subtotal()
                order.add_subtotal()
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        print('vals :', vals)
        if not self._context.get('request_from_action_subtotal'):
            for order in res:
                order.action_subtotal_create()
                order.add_subtotal_create()
        res.write({'update_sequence': 'test'})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    new_line = fields.Boolean(default=False)
    display_type = fields.Selection(
        selection_add=[('line_sub_total', 'Subtotal'), ('line_title', 'Titre'), ('line_subtotal', 'Subtotal')])


    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        print('vals Line:', vals)
        return res

    def write(self, values):
        result = super(SaleOrderLine, self).write(values)
        return result

