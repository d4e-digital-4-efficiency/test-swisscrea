# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductTag(models.Model):
    _name = "product.tag"
    _description = "Product Tag"


    name = fields.Char('Tag', index=True, required=True)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    tag_id = fields.Many2many('product.tag', column1='product_id',
                                    column2='tag_id', string='Tags')
