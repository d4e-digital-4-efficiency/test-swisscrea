# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrderAction(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrderAction, self).button_confirm()
        if res:
            return

    def action_pos_send(self):
        ir_model_data = self.env['ir.model.data']
        for rec in self:
            try:
                if rec.state == 'purchase':
                    template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
                else:
                    template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
            except ValueError:
                template_id = False
            self.env['mail.template'].browse(template_id).send_mail(rec.id, force_send=True)
            rec.message_post_with_template(template_id, composition_mode='comment')
