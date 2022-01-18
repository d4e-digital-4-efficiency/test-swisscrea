from odoo import api, fields, models, _

class HrContractHistory(models.Model):
    _name = "hr.contract.history"





    history_id = fields.Many2one('hr.contract', string='History')
    validity_date = fields.Datetime('validity date',readonly=True)
    avs_contribution = fields.Boolean("AVS contribution", default=True,readonly=True )
    ac_contribution = fields.Boolean("AC contribution", default=True,readonly=True)
    compensation_fund = fields.Many2one('hr.funds', string='Compensation Fund',
                                        domain="[('type_of_crate','=','AVS/AC')]", readonly=True)
    # LAA***********************
    laa_contribution = fields.Selection(string="LAA contribution",
                                        selection=[('A0-Not subject to LAA', 'A0-Not subject to LAA'), (
                                        'A1 - AAP and AANP insured - with AANP deductions',
                                        'A1 - AAP and AANP insured - with AANP deductions'),
                                                   ('A2 - AAP and AANP insured - without AANP deduction',
                                                    'A2 - AAP and AANP insured - without AANP deduction'), (
                                                   'A3 - AAP insured only - without AANP deduction',
                                                   'A3 - AAP insured only - without AANP deduction'),
                                                   ('B0-Not subject to LAA', 'B0-Not subject to LAA'), (
                                                   'B1 - AAP and AANP insured - with AANP deductions',
                                                   'B1 - AAP and AANP insured - with AANP deductions'), (
                                                   'B2 - AAP and AANP insured - without AANP deduction',
                                                   'B2 - AAP and AANP insured - without AANP deduction'), (
                                                       'B3 - AAP insured only - without AANP deduction',
                                                       'B3 - AAP insured only - without AANP deduction'),
                                                   ('C0-Not subject to LAA', 'C0-Not subject to LAA'), (
                                                   'C1- AAP and AANP insured - with AANP deductions',
                                                   'C1 - AAP and AANP insured - with AANP deductions'), (
                                                   'C2 - AAP and AANP insured - without AANP deduction',
                                                   'C2 - AAP and AANP insured - without AANP deduction'), (
                                                   'C3 - AAP insured only - without AANP deduction',
                                                   'C3 - AAP insured only - without AANP deduction'),
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
                                                   ('Z1- AAP and AANP insured - with AANP deductions',
                                                    'Z1- AAP and AANP insured - with AANP deductions'),
                                                   ('Z2 - AAP and AANP insured - without AANP deduction',
                                                    'Z2 - AAP and AANP insured - without AANP deduction'),
                                                   ('Z3 - AAP insured only - without AANP deduction',
                                                    'Z3 - AAP insured only - without AANP deduction')
                                                   ], readonly=True)

    laa_fund = fields.Many2one('hr.funds', string='LAA fund', domain="[('type_of_crate', '=', 'LAA')]", readonly=True)
    # LAAC******************************
    laac_contribution = fields.Boolean("LAAC contribution", default=True,readonly=True)
    laac_code = fields.Many2one('codes.laac', string='LAAC code',readonly=True )
    laac_cashier = fields.Many2one('hr.funds', string='LAAC Cashier', domain="[('type_of_crate', '=', 'LAAC'),]",
                                   readonly=True)
    #   *IJM********************************
    ijm_contribution = fields.Boolean("IJM contribution", default=True, tracking=True)
    ijm_code = fields.Many2one('codes.ijm', string='IJM code',readonly=True)
    ijm_cashier = fields.Many2one('hr.funds', string='IJM Cashier', domain="[('type_of_crate', '=', 'IJM')]", readonly=True
                                  )
    #  LPP****************************
    lpp_contribution = fields.Boolean("LPP contribution", default=True, tracking=True)
    lpp_code = fields.Many2one('codes.lpp', string='LPP code',readonly=True)
    lpp_cashier = fields.Many2one('hr.funds', string='LPP Cashier', domain="[('type_of_crate', '=', 'LPP')]", readonly=True
                                  )
    tax_source = fields.Selection(string="Subject to source tax", selection=[('not_submitted', 'Not submitted'), (
    'submitted_with_scale', 'Submitted with scale'), ('submitted_without_scale', 'Submitted without scale'), ],
                                  default='not_submitted')
    canton = fields.Selection(string="Canton",
                              selection=[('ag', 'AG'), ('ai', 'AI'), ('ar', 'AR'), ('be', 'BE'), ('bl', 'BL'),
                                         ('bs', 'BS'), ('fr', 'FR'), ('ge', 'GE'), ('GL', 'GL'), ('ge', 'GE'),
                                         ('gr', 'GR'), ('ju', 'JU'), ('lu', 'LU'), ('ne', 'NE'), ('nw', 'NW'),
                                         ('ow', 'OW'), ('sg', 'SG'), ('h', 'H'), ('so', 'SO'), ('sz', 'SZ'),
                                         ('tg', 'TG'),
                                         ('it', 'TI'), ('ur', 'UR'), ('vd', 'VD'), ('vs', 'VS'), ('zg', 'ZG'),
                                         ('zh', 'ZH'), ])
    tax_rate = fields.Float(string="Tax Rate")
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

