# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class NpaCommuneOfs(models.Model):
    _name = "npa.commune.ofs"
    _description = 'Record for Commune OFS for each Zip Code '

    name = fields.Char("Name", compute="_get_np_name", store= True)
    np_numero = fields.Char("NP NUMERO", required= True)
    np_ville = fields.Char("NP VILLE", required= True)
    np_canton = fields.Char("NP CANTON", required= True)
    np_type = fields.Char("NP TYPE")
    np_ofs = fields.Char("NP OFS", required= True)
    np_version = fields.Char("NP VERSION")

    _sql_constraints = [
        ('_unique_NPA', 'unique (np_numero, np_ville, np_canton, np_type, np_ofs, np_version)', 'This record already exist !')
    ]

    @api.depends('np_numero', 'np_ville', 'np_canton')
    def _get_np_name(self):
        for rec in self:
            rec.name = ''
            if rec.np_numero:
                rec.name = "[" + rec.np_numero + "] "
            if rec.np_numero and rec.np_ville:
                rec.name = "[" + rec.np_numero + "] " + rec.np_ville
            if rec.np_numero and rec.np_ville and rec.np_canton:
                rec.name = "[" + rec.np_numero + "] " + rec.np_ville + " (" + rec.np_canton + ")"

    @api.model
    def create(self, values):
        res = super(NpaCommuneOfs, self).create(values)
        if res.name :
            old_rec = self.env['npa.commune.ofs'].search([('name','=', res.name)], order='id asc')
            if len(old_rec) > 1:
                old_rec[0].unlink()
        return res