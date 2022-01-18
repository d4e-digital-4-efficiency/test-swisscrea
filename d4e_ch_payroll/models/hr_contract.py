# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from dateutil import relativedelta


class Contract(models.Model):
    _inherit = 'hr.contract'

    analytical_labels = fields.Many2one('account.analytic.tag',"Étiquettes analytiques")
    observation = fields.Text("Observations")
    tax_rate_source = fields.Float("Tax rate at source")
    avs_ded_year = fields.Float("Réserve des déductions AVS reportable sur l'année")
    seniority = fields.Char(string="Seniority", compute='_compute_seniority')
    # Cumulative_annual_salary = fields.Monetary('Cumul de salaire annuel')
    private_share_service_car = fields.Monetary("Part privée voiture de service")
    lump_sum_representation_costs = fields.Monetary("Frais forfaitaires de représentation")
    allocation_for_child = fields.Monetary("Allocation for child ")

    # ********new task of contribution ********
    validity_date = fields.Datetime('validity date', tracking=True)
    avs_contribution = fields.Boolean("AVS contribution", default=True, tracking=True)
    ac_contribution = fields.Boolean("AC contribution", default=True, tracking=True)
    compensation_fund = fields.Many2one('hr.funds', string='Compensation Fund',
                                        domain="[('type_of_crate','=','AVS/AC')]", tracking=True)
    # LAA***********************
    laa_contribution = fields.Selection(string="LAA contribution",
                                     selection=[('A0-Not subject to LAA', 'A0-Not subject to LAA'), ('A1 - AAP and AANP insured - with AANP deductions', 'A1 - AAP and AANP insured - with AANP deductions'),
                                               ('A2 - AAP and AANP insured - without AANP deduction', 'A2 - AAP and AANP insured - without AANP deduction'),('A3 - AAP insured only - without AANP deduction', 'A3 - AAP insured only - without AANP deduction'),
                                                ('B0-Not subject to LAA', 'B0-Not subject to LAA'), ('B1 - AAP and AANP insured - with AANP deductions','B1 - AAP and AANP insured - with AANP deductions'),('B2 - AAP and AANP insured - without AANP deduction','B2 - AAP and AANP insured - without AANP deduction'), (
                                                'B3 - AAP insured only - without AANP deduction',
                                                'B3 - AAP insured only - without AANP deduction'),('C0-Not subject to LAA', 'C0-Not subject to LAA'), ('C1- AAP and AANP insured - with AANP deductions', 'C1 - AAP and AANP insured - with AANP deductions'), ('C2 - AAP and AANP insured - without AANP deduction', 'C2 - AAP and AANP insured - without AANP deduction'),('C3 - AAP insured only - without AANP deduction', 'C3 - AAP insured only - without AANP deduction'),
                                                ('D0-Not subject to LAA', 'D0-Not subject to LAA'), (
                                                'D1- AAP and AANP insured - with AANP deductions',
                                                'D1 - AAP and AANP insured - with AANP deductions'), (
                                                'D2 - AAP and AANP insured - without AANP deduction',
                                                'D2 - AAP and AANP insured - without AANP deduction'), (
                                                'D3 - AAP insured only - without AANP deduction',
                                                'D3 - AAP insured only - without AANP deduction'),
                                                ('H0-Not subject to LAA', 'H0-Not subject to LAA'), (
                                                'H1- AAP and AANP insured - with AANP deductions',
                                                'H1 - AAP and AANP insured - with AANP deductions'), (
                                                'H2 - AAP and AANP insured - without AANP deduction',
                                                'H2 - AAP and AANP insured - without AANP deduction'), (
                                                'H3 - AAP insured only - without AANP deduction',
                                                'H3 - AAP insured only - without AANP deduction'),
                                                ('Z0-Not subject to LAA', 'Z0-Not subject to LAA'),
                                                ('Z1- AAP and AANP insured - with AANP deductions', 'Z1- AAP and AANP insured - with AANP deductions'),
                                                ('Z2 - AAP and AANP insured - without AANP deduction', 'Z2 - AAP and AANP insured - without AANP deduction'),
                                                ('Z3 - AAP insured only - without AANP deduction', 'Z3 - AAP insured only - without AANP deduction')
                                                ], tracking=True)

    laa_fund = fields.Many2one('hr.funds', string='LAA fund', domain="[('type_of_crate', '=', 'LAA')]", tracking=True)
    # LAAC******************************
    laac_contribution = fields.Boolean("LAAC contribution", default=True, tracking=True)
    laac_code = fields.Many2one('codes.laac', string='LAAC code', tracking=True)
    laac_cashier = fields.Many2one('hr.funds', string='LAAC Cashier', domain="[('type_of_crate', '=', 'LAAC')]", tracking=True)
    #   *IJM********************************
    ijm_contribution = fields.Boolean("IJM contribution", default=True, tracking=True)
    ijm_code = fields.Many2one('codes.ijm', string='IJM code', tracking=True)
    ijm_cashier = fields.Many2one('hr.funds', string='IJM Cashier', domain="[('type_of_crate', '=', 'IJM')]", tracking=True)
    #  LPP****************************
    lpp_contribution = fields.Boolean("LPP contribution", default=True, tracking=True)
    lpp_code = fields.Many2one('codes.lpp', string='LPP code', tracking=True)
    lpp_cashier = fields.Many2one('hr.funds', string='LPP Cashier', domain="[('type_of_crate', '=', 'LPP')]", tracking=True)
    # ****************

    date_validity_lines = fields.One2many('hr.contract.history', 'history_id', string='Date Lines')

    # Frais forfaitaire de voiture
    Car_flat_fee = fields.Monetary('Car flat fee')
    # Frais forfaitaire pour expatriés
    Flat_rate_for_expatriates = fields.Monetary('Flat rate for expatriates')
    # Autre frais forfaitaires
    Other_flat_rate_costs = fields.Monetary('Other flat-rate costs')



    lpp_fixe = fields.Monetary('Fixed LPP')
    lpp_fixe_pp = fields.Monetary('PP_Fixed LPP')

    tax_source = fields.Selection(string="Subject to source tax", selection=[('not_submitted', 'Not submitted'), ('submitted_with_scale',
                                        'Submitted with scale'), ('submitted_without_scale', 'Submitted without scale'), ], default='not_submitted')
    canton = fields.Selection(string="Canton", selection=[('ag', 'AG'),('ai','AI'),('ar','AR'),('be','BE'),('bl','BL'),('bs','BS'),('fr','FR'),('ge','GE'),('GL','GL'),('ge','GE'),
                                                          ('gr','GR'),('ju','JU'),('lu','LU'),('ne','NE'),('nw','NW'),('ow','OW'),('sg','SG'),('so','SO'),('sz','SZ'),('tg','TG'),
                                                          ('it','TI'),('ur','UR'),('vd','VD'),('vs','VS'),('zg','ZG'),('zh','ZH'), ])
    tax_rate = fields.Float(string="Tax Rate", store=True)

    rent_deduction = fields.Monetary("Rent deduction")
    withholding_prosecution_office = fields.Monetary("Withholding for prosecution office")
    various1 = fields.Monetary("Various 1")
    various2 = fields.Monetary("Various 2")
    tabelle = fields.Selection(string="Tabelle",
                               selection=[('A0', 'A0'), ('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('A4', 'A4'),
                                          ('A5', 'A5'), ('A6', 'A6'), ('A7', 'A7'), ('A8', 'A8'), ('A9', 'A9'),
                                          ('B0', 'B0'),
                                          ('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'),
                                          ('B5', 'B5'), ('B6', 'B6'), ('B7', 'B7'), ('B8', 'B8'), ('B9', 'B9'),
                                          ('C0', 'C0'), ('C1', 'C1'), ('C2', 'C2'), ('C3', 'C3'), ('C4', 'C4'),
                                          ('C5', 'C5'), ('C6', 'C6'),
                                          ('C7', 'C7'), ('C8', 'C8'), ('C9', 'C9'), ('E0', 'E0'), ('F0', 'F0'),
                                          ('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'), ('F4', 'F4'), ('F5', 'F5'),
                                          ('F6', 'F6'), ('F7', 'F7'),
                                          ('F8', 'F8'), ('F9', 'F9'), ('G9', 'G9'), ('H1', 'H1'), ('H2', 'H2'),
                                          ('H3', 'H3'), ('H4', 'H4'), ('H5', 'H5'), ('H6', 'H6'), ('H7', 'H7'),
                                          ('H8', 'H8'), ('H9', 'H9'), ('L0', 'L0'),
                                          ('L1', 'L1'), ('L2', 'L2'), ('L3', 'L3'), ('L4', 'L4'), ('L5', 'L5'),
                                          ('L6', 'L6'), ('L7', 'L7'), ('L8', 'L8'), ('L9', 'L9'), ('M0', 'M0'),
                                          ('M1', 'M1'), ('M2', 'M2'), ('M3', 'M3'),
                                          ('M4', 'M4'), ('M5', 'M5'), ('M6', 'M6'), ('M7', 'M7'), ('M8', 'M8'),
                                          ('M9', 'M9'), ('N0', 'N0'), ('N1', 'N1'), ('N2', 'N2'), ('N3', 'N3'),
                                          ('N4', 'N4'), ('N5', 'N5'), ('N6', 'N6'),
                                          ('N7', 'N7'), ('N8', 'N8'), ('N9', 'N9'), ('P1', 'P1'), ('P2', 'P2'),
                                          ('P3', 'P3'), ('P4', 'P4'), ('P5', 'P5'), ('P6', 'P6'), ('P7', 'P7'),
                                          ('P8', 'P8'), ('P9', 'P9'), ('Q9', 'Q9'),
                                          ('HE', 'HE'), ('ME', 'ME'), ('NO', 'NO'), ('SF', 'SF'), ('PP', 'PP'),
                                          ('PE', 'PE')])

    church_tax = fields.Selection(string="Church tax", selection=[('true', 'True'), ('false', 'False')])



    @api.depends('date_start')
    def _compute_seniority(self):
        for rec in self:
            if rec.date_start < datetime.now().date():
                diff = relativedelta.relativedelta(datetime.now().date(), rec.date_start)
                rec.seniority = str(diff.years) + ' Years - ' + str(diff.months) + ' Months - ' + str(diff.days) + ' Days'
            else:
                rec.seniority = '0'


    # **********************task date
    @api.model
    def create(self, vals):
       res = super(Contract, self).create(vals)
       self.env['hr.contract.history'].create({
           'history_id': res.id,
           'validity_date':'validity_date' in vals and vals['validity_date'] or self.validity_date,
           'avs_contribution': vals['avs_contribution'],
           'ac_contribution': vals['ac_contribution'],
           'compensation_fund': vals['compensation_fund'],
           'laac_contribution': vals['laac_contribution'],
           'laa_contribution': vals['laa_contribution'],
           'laa_fund': vals['laa_fund'],
           'laac_code': vals['laac_code'],
           'laac_cashier': vals['laac_cashier'],
           'ijm_contribution':vals['ijm_contribution'],
           'ijm_code': vals['ijm_code'],
           'ijm_cashier': vals['ijm_cashier'],
           'lpp_contribution':vals['lpp_contribution'],
           'lpp_code': vals['lpp_code'],
           'lpp_cashier': vals['lpp_cashier'],
           'tax_source': vals['tax_source'],
           'canton': vals['canton'] if ('canton' in vals) else res.canton,
           'tax_rate': vals['tax_rate'],
       })
       return res

    def write(self, vals):
        result = super(Contract, self).write(vals)
        # Todo tester le cas des fields devient = False
        for contract in self:
            if 'validity_date' in vals.keys() :
                self.env['hr.contract.history'].create({
               'history_id': contract.id,
               'validity_date': 'validity_date' in vals and vals['validity_date'] or contract.validity_date,
                    # partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
               'avs_contribution':   vals['avs_contribution'] if ('avs_contribution' in vals) else contract.avs_contribution,
               'ac_contribution': vals['ac_contribution'] if ('ac_contribution' in vals) else contract.ac_contribution ,
               'compensation_fund': vals['compensation_fund'] if ('compensation_fund' in vals) else contract.compensation_fund.id,
               'laa_contribution': vals['laa_contribution'] if ('laa_contribution' in vals) else contract.laa_contribution,
               'laa_fund': vals['laa_fund'] if ('laa_fund' in vals) else contract.laa_fund.id,
               'laac_code': vals['laac_code'] if ('laac_code' in vals) else contract.laac_code.id,
               'laac_cashier': vals['laac_cashier'] if ('laac_cashier' in vals) else contract.laac_cashier.id,
               'laac_contribution': vals['laac_contribution'] if ('laac_contribution' in vals) else contract.laac_contribution,
               # 'ijm_code': 'ijm_code' in vals and vals['ijm_code'] ,
               'ijm_contribution':vals['ijm_contribution'] if ('ijm_contribution' in vals) else contract.ijm_contribution,
               'ijm_code': vals['ijm_code'] if ('ijm_code' in vals) else contract.ijm_code.id,
               'ijm_cashier': vals['ijm_cashier'] if ('ijm_cashier' in vals) else contract.ijm_cashier.id,
               'lpp_contribution': vals['lpp_contribution'] if ('lpp_contribution' in vals) else contract.lpp_contribution,
               'lpp_code': vals['lpp_code'] if ('lpp_code' in vals) else contract.lpp_code.id,
               'lpp_cashier': vals['lpp_cashier'] if ('lpp_cashier' in vals) else  contract.lpp_cashier.id,
               'tax_source': vals['tax_source'] if (
                            'tax_source' in vals) else contract.tax_source,
               'canton': vals['canton'] if ('canton' in vals) else contract.canton,
               'tax_rate': vals['tax_rate'] if ('tax_rate' in vals) else contract.tax_rate,
                'tabelle':vals['tabelle'] if ('tabelle' in vals) else contract.tabelle,
                'church_tax':vals['church_tax'] if ('church_tax' in vals) else contract.church_tax,

           })

        return result










