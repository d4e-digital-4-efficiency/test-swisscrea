# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class TaxRate(models.Model):
    _name = "tax.rate"
    _description = "Liste de  barèmes de l'impôt à la source"

    code_canton = fields.Char("Canton")
    perception_scale = fields.Char("Barême de perception")
    church_tax = fields.Char("Impôt ecclésiastique")
    validity_start_date = fields.Date("Date début de validité")
    monthly_taxable_income = fields.Monetary("Revenu mensuel imposable")
    francs_taxes = fields.Float("Impôts en Francs")
    taxes_percent = fields.Float("Impôts en %")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.company.currency_id)
