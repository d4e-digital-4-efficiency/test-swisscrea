# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    permitted_category_id = fields.Many2many('res.partner.category', 'permitted_user_category_id',
                                             'user_id', 'category_id', string='Tags')
    product_tag_id = fields.Many2many('product.tag', 'permitted_product_tag_id',
                                             'user_id', 'tag_id', string='Product Tags')
    permitted_website_id = fields.Many2many('website', 'permitted_user_website_id',
                                             'user_id', 'website_id', string='Website Tags')
