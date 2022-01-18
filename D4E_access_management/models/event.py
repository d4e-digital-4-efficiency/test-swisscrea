# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Event(models.Model):
    _inherit = 'event.event'

    def _domain_sale_person_id(self):
        if self.user_has_groups('D4E_access_management.group_event'):
            return ['&', '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id), ('salesperson_id','=' , self.env.user.id)]
        return ['|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)]

    website_id = fields.Many2one(
        "website",
        string="Website",
        ondelete="restrict",
        help="Restrict publishing to this website.",
        index=True,
        domain=_domain_sale_person_id
    )
