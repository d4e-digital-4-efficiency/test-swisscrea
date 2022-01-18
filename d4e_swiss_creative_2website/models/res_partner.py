# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


CANTON_SUISSE= [
    ('Appenzell Rhodes-Extérieures', 'Appenzell Rhodes-Extérieures'),
    ('Appenzell Rhodes-Intérieures', 'Appenzell Rhodes-Intérieures'),
    ('Argovie', 'Argovie'),
    ('Bâle-Campagne', 'Bâle-Campagne'),
    ('Bâle-Ville', 'Bâle-Ville'),
    ('Berne', 'Berne'),
    ('Fribourg', 'Fribourg'),
    ('Genève', 'Genève'),
    ('Glaris', 'Glaris'),
    ('Grisons', 'Grisons'),
    ('Jura', 'Jura'),
    ('Lucerne', 'Lucerne'),
    ('Neuchâtel', 'Neuchâtel'),
    ('Nidwald', 'Nidwald'),
    ('Obwald', 'Obwald'),
    ('Saint-Gall', 'Saint-Gall'),
    ('Schaffhouse', 'Schaffhouse'),
    ('Schwytz', 'Schwytz'),
    ('Soleure', 'Soleure'),
    ('Tessin', 'Tessin'),
    ('Thurgovie', 'Thurgovie'),
    ('Uri', 'Uri'),
    ('Valais', 'Valais'),
    ('Vaud', 'Vaud'),
    ('Zoug', 'Zoug'),
    ('Zurich', 'Zurich')
]


class Partner(models.Model):
    _inherit = "res.partner"

    website_ids = fields.Many2many('website', 'website_partner_rel', 'partner_id', 'website_id', string='Websites')
    is_published = fields.Boolean('Is Published')
    web_desc = fields.Text("Descreption")
    web_image = fields.Image("Website Image", max_width=256, max_height=256)
    canton = fields.Selection(CANTON_SUISSE, "Canton")
    aoc = fields.Char("AOC", help="Appellation d'Origine Contrôlée")
    pass_provino = fields.Boolean("Accepte le Pass Provino", default=False)
    bool_compute = fields.Boolean(compute='_compute_bool_compute', store=True)

    # @api.onchange('website_ids')
    # def _onchange_website_ids(self):
    @api.depends('website_ids')
    def _compute_bool_compute(self):
        for rec in self:
            if not rec.website_ids:
                rec.website_id = False
                rec.is_published = False
                rec.bool_compute = False
            if rec.website_ids and len(rec.website_ids.ids) == 1:
                rec.website_id = rec.website_ids.ids[0]
                rec.is_published = True
                rec.bool_compute = True
            if rec.website_ids and len(rec.website_ids.ids) > 1:
                rec.website_id = False
                rec.is_published = True
                rec.bool_compute = True
