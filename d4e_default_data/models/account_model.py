# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    name = fields.Char(string='Name', required=True, translate=True)
    match_text_location_note = fields.Boolean(
        default=True,
        help="Search in the Statement's Note to find the Invoice/Payment's reference",
    )
    match_text_location_reference = fields.Boolean(
        default=True,
        help="Search in the Statement's Reference to find the Invoice/Payment's reference",
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    internal_reference = fields.Char(string='Internal Reference')

