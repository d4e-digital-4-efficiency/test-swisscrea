# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.image import image_data_uri
import json


class Website(http.Controller):

    @http.route('/d4e_domain_snippet/snippets/domain', type='json', auth='public', website=True)
    def get_dynamic_domain(self, limit=None, search_domain=None):
        default_domain = []
        if search_domain:
            default_domain += search_domain
        if limit:
            dynamic_domains = request.env['res.domain'].sudo().search(default_domain, limit=limit)
        else:
            dynamic_domains = request.env['res.domain'].sudo().search(default_domain)
        return json.dumps([{
            'id': doc.id,
            'name': doc.name,
            'description': doc.description,
            'image': image_data_uri(doc.image),
        } for doc in dynamic_domains])
