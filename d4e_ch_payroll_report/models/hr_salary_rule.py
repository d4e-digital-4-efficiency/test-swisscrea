# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    payslip_rubrique = fields.Selection([('salaire_brut', 'Salaire Brut'), ('charges_sociales', 'Charges Sociales'),
                                         ('divers', 'Divers')], string='Groupe', default=False)
    payslip_imprime_opt = fields.Selection([('no_imprime','Ne jamais imprimer'),
                                            ('tj_imprime','Toujours imprimer'),
                                            ('none_zero_imprime','Imprimer seulement si différent de 0')],
                                string="Option d'impression", default='tj_imprime')
