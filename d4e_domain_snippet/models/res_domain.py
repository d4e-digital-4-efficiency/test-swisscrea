# -*- coding: utf-8 -*-
from odoo import models, fields


class ResDomain(models.Model):
    _name = 'res.domain'

    name = fields.Char(string='Name')
    is_published = fields.Boolean(string='Is published')
    image = fields.Binary(string='Image', attachment=True)
    description = fields.Html(string='Description')

    def website_publish_button(self):
        self.ensure_one()
        return self.write({'is_published': not self.is_published})
