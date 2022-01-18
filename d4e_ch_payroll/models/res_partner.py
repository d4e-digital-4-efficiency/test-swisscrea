# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


CANTON_SUISSE= [
    ('AR', 'Appenzell Rhodes-Extérieures'),
    ('AI', 'Appenzell Rhodes-Intérieures'),
    ('AG', 'Argovie'),
    ('BL', 'Bâle-Campagne'),
    ('BS', 'Bâle-Ville'),
    ('BE', 'Berne'),
    ('FR', 'Fribourg'),
    ('GE', 'Genève'),
    ('GL', 'Glaris'),
    ('GR', 'Grisons'),
    ('JU', 'Jura'),
    ('LU', 'Lucerne'),
    ('NE', 'Neuchâtel'),
    ('NW', 'Nidwald'),
    ('OW', 'Obwald'),
    ('SG', 'Saint-Gall'),
    ('SH', 'Schaffhouse'),
    ('SZ', 'Schwytz'),
    ('SO', 'Soleure'),
    ('TI', 'Tessin'),
    ('TG', 'Thurgovie'),
    ('UR', 'Uri'),
    ('VS', 'Valais'),
    ('VD', 'Vaud'),
    ('ZG', 'Zoug'),
    ('ZH', 'Zurich')
]

class Partner(models.Model):
    _inherit = "res.partner"

    employee_id = fields.Many2one('hr.employee', string='Related Employee')
    canton = fields.Selection(CANTON_SUISSE, "Canton")
    num_commune_ofs = fields.Char("Numéro de commune OFS")
    npa_id = fields.Many2one('npa.commune.ofs')

    @api.onchange('npa_id')
    def _onchange_npa_id(self):
        if self.npa_id:
            npa_obj = self.env['npa.commune.ofs'].search([('name','=',self.npa_id.name)])[-1]
            self.num_commune_ofs = npa_obj.np_ofs
            self.canton = npa_obj.np_canton
            self.city = npa_obj.np_ville
            self.zip = npa_obj.np_numero
            self.country_id = self.env.ref('base.ch').id

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        res.employee_id.write({'address_home_id': res})
        return res


    # def write(self, vals):
    #     if vals['employee_id']:
    #         self.env['hr.employee'].browse(vals['employee_id']).write({'address_home_id': self})
    #     res = super(Partner, self).write(vals)
    #     return res

    def write(self, vals):
        res = super(Partner, self).write(vals)
        if self.employee_id:
            self.employee_id.write({'address_home_id': self})
        return res