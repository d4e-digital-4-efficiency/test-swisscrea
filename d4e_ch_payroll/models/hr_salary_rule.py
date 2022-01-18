# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    rubrique_certificat = fields.Selection(string='Rubriques',selection=[('Aucune rubrique', 'Aucune rubrique'),('1 Salaire_Rente', '1 Salaire / Rente'), ('2.1 Prestations salariales accessoires (pension, logement)', '2.1 Prestations salariales accessoires (pension, logement)'),('2.2 Part privée voiture de service', '2.2 Part privée voiture de service'),
                                                                         ('2.3 Prestations salariales accessoires (autres)', '2.3 Prestations salariales accessoires (autres)'),
                                                                         ('3 Prestations non périodiques', '3 Prestations non périodiques'),
                                                                         ('4 Prestations en capital', '4 Prestations en capital'),
                                                                         ('5 Droits de participation', '5 Droits de participation'),
                                                                         ('6 Indemnités des membres de l administration', '6 Indemnités des membres de l administration'),
                                                                         ('7.1 Autres Prestations 1', '7.1 Autres Prestations 1'),
                                                                         ('7.2 Autres Prestations 2', '7.2 Autres Prestations 2'),
                                                                         ('9 Cotisations AVS/AI/APG/AC/AANP', '9 Cotisations AVS/AI/APG/AC/AANP'),
                                                                         ('10.1 Prévoyance professionnelle (cotisations ordinaires)', '10.1 Prévoyance professionnelle (cotisations ordinaires)'),
                                                                         ('10.2 Prévoyance professionnelle (cotisation pour le rachat)', '10.2 Prévoyance professionnelle (cotisation pour le rachat)'),
                                                                         ('12 Retenue de l impôt à la source', '12 Retenue de l"impôt à la source'),
                                                                         ('13.1.1 Frais effectifs (voyage, repas, nuitées)', '13.1.1 Frais effectifs (voyage, repas, nuitées)'),
                                                                         ('13.1.2 Frais effectifs (autres)', '13.1.2 Frais effectifs (autres)'),
                                                                         ('13.2.1 Frais forfaitaires (représentation)', '13.2.1 Frais forfaitaires (représentation)'),
                                                                         ('13.2.2 Frais forfaitaires (voiture) ', '13.2.2 Frais forfaitaires (voiture) '),
                                                                         ('13.2.3 Fris forfaitaires (autres)', '13.2.3 Fris forfaitaires (autres)'),
                                                                         ('13.3 Contribution au perfectionnement', '13.3 Contribution au perfectionnement'),
                                                                         ('15 Observations - Beobachtungen', '15 Observations - Beobachtungen')] , default= 'Aucune rubrique')





    rule_type = fields.Selection(string="Rule type", required=True, selection=[('section', 'Section'), ('calculation basis', 'Calculation basis'),('storage data', 'Storage data'),('Headings - Employer share', 'Headings - Employer share')],)
    base_test = fields.Selection(string="Base",  selection=[('fixed base', 'Fixed base'), ('free_base', 'Free base')], default ='free_base')
    rate_quantity = fields.Selection(string="Rate / Quantity",  selection=[('fixed_rate_quantity', 'Fixed rate quantity'),
                                                                           ('free_rate_quantity', 'Free rate quantity')],
                                                                    default='free_rate_quantity')
    verification = fields.Boolean(default=False)

    analytical_labels = fields.Many2one('account.analytic.tag',"Étiquettes analytiques")

    @api.onchange('base_test','rate_quantity')
    def _compute_value(self):
        if self.base_test == 'fixed base' and self.rate_quantity == 'fixed_rate_quantity':
            self.verification = True
        else:
            self.verification = False

    def _satisfy_condition(self, localdict):
        dict_cotisation = {}
        dict_cotisation['avs_contribution'] = []
        dict_cotisation['ac_contribution'] = []
        dict_cotisation['laac_contribution'] = []
        dict_cotisation['ijm_contribution'] = []
        dict_cotisation['lpp_contribution'] = []
        dict_cotisation['laa_contribution'] = {}
        dict_cotisation['tax_source'] = {}
        list_no_avs_contribution = []
        list_no_ac_contribution = []
        list_no_laac_contribution = []
        list_no_ijm_contribution = []
        list_no_lpp_contribution = []
        for line in localdict['contract'].date_validity_lines:
            if line.avs_contribution:
                dict_cotisation['avs_contribution'].append(str(line.validity_date.month))
            else:
                list_no_avs_contribution.append(str(line.validity_date.month))
            if line.ac_contribution:
                dict_cotisation['ac_contribution'].append(str(line.validity_date.month))
            else:
                list_no_ac_contribution.append(str(line.validity_date.month))
            if line.laac_contribution:
                dict_cotisation['laac_contribution'].append(str(line.validity_date.month))
            else:
                list_no_laac_contribution.append(str(line.validity_date.month))
            if line.ijm_contribution:
                dict_cotisation['ijm_contribution'].append(str(line.validity_date.month))
            else:
                list_no_ijm_contribution.append(str(line.validity_date.month))
            if line.lpp_contribution:
                dict_cotisation['lpp_contribution'].append(str(line.validity_date.month))
            else:
                list_no_lpp_contribution.append(str(line.validity_date.month))
            if line.laa_contribution:
                dict_cotisation['laa_contribution'][line.validity_date.month] = str(line.laa_contribution)
            if line.tax_source:
                dict_cotisation['tax_source'][line.validity_date.month] = str(line.tax_source)

        list_month = ['1','2','3','4','5','6','7','8','9','10','11','12']

        for month_index in list_month:
            if month_index not in list_no_avs_contribution:
                dict_cotisation['avs_contribution'].append(month_index)
            if month_index not in list_no_ac_contribution:
                dict_cotisation['ac_contribution'].append(month_index)
            if month_index not in list_no_laac_contribution:
                dict_cotisation['laac_contribution'].append(month_index)
            if month_index not in list_no_ijm_contribution:
                dict_cotisation['ijm_contribution'].append(month_index)
            if month_index not in list_no_lpp_contribution:
                dict_cotisation['lpp_contribution'].append(month_index)



        localdict['dict_cotisation'] = dict_cotisation
        self.ensure_one()
        if self.condition_select == 'none':
            return True
        if self.condition_select == 'range':
            try:
                result = safe_eval(self.condition_range, localdict)
                return self.condition_range_min <= result <= self.condition_range_max
            except:
                raise UserError(_('Wrong range condition defined for salary rule %s (%s).') % (self.name, self.code))
        else:  # python code
            try:
                safe_eval(self.condition_python, localdict, mode='exec', nocopy=True)
                return localdict.get('result', False)
            except:
                raise UserError(_('Wrong python condition defined for salary rule %s (%s).') % (self.name, self.code))

