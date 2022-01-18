# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HierarchyStatus(models.Model):
    _name = "hierarchy.status"
    _description = 'Hierarchy particular statut'

    name = fields.Char("Name")