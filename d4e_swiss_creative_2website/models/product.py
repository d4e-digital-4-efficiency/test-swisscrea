# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import float_compare

class WineStyle(models.Model):
    _name = "wine.style"
    _description = "Style de Vin"

    name= fields.Char("Nom")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Style name already exists!'),
    ]

class WineAccord(models.Model):
    _name = "wine.accord"
    _description = "Accord de Vin"

    name = fields.Char("Nom")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Accord name already exists!'),
    ]

class ProductProduct(models.Model):
    _inherit = "product.product"


    def _select_seller_with_website(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False,
                                   website_id=False):
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        res = self.env['product.supplierinfo']
        sellers = self._prepare_sellers(params)
        sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.company.id)
        # if website_id and len(sellers) == 1 and not sellers[0].website_id:
        if website_id and (len(sellers) > 0) and (len(sellers.filtered(lambda s: s.website_id.id != False)) == 0):
            # res |= sellers[0]
            return self._select_seller(
            partner_id=partner_id,
            quantity=quantity,
            date=date,
            uom_id=uom_id,
            params=params)
        else:
            for seller in sellers:
                # Set quantity in UoM of seller
                quantity_uom_seller = quantity
                if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                    quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)

                if seller.date_start and seller.date_start > date:
                    continue
                if seller.date_end and seller.date_end < date:
                    continue
                if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                    continue
                if float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
                    continue
                if seller.product_id and seller.product_id != self:
                    continue
                # if website_id and seller.website_id.id != website_id.id:
                #     break
                if not res or res.name == seller.name:
                    if website_id and seller.website_id.id == website_id.id:
                        res |= seller
        return res.sorted('price')[:1]


class Product(models.Model):
    _inherit = "product.template"

    website_ids = fields.Many2many('website', 'website_product_rel', 'product_id', 'website_id', string='Websites')
    # is_published = fields.Boolean('Is Published', copy=False, default=lambda self: self._default_is_published(),index=True)
    is_published = fields.Boolean(copy=True)
    special_reappro = fields.Boolean("réapprovisionnement Specifique ")
    cepage = fields.Char("Cépage")
    vin_type = fields.Char("Type de vin")
    # style = fields.Char("Style")
    # accord = fields.Char("Accord")
    style_ids = fields.Many2many('wine.style','product_wine_style_rel', 'product_id', 'style_id', string='Styles')
    accord_ids = fields.Many2many('wine.accord','product_wine_accord_rel', 'product_id', 'accord_id', string='Accords')
    num_article = fields.Char("n°article ")
    contenance = fields.Char("Contenance")
    millesime = fields.Char("Millésime", compute='_get_lot_info')
    website_desc = fields.Text("Description site web ")
    aoc = fields.Char("AOC", help="Appellation d'Origine Contrôlée")
    bool_compute = fields.Boolean(compute='_compute_bool_compute', store=True)

    @api.onchange('special_reappro')
    def _onchange_special_reappro(self):
        if self.special_reappro:
            self.uom_po_id = self.env.ref('d4e_swiss_creative_2website.product_uom_six_unit').id
        else:
            self.uom_po_id = False

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
            print(rec.is_published)

    def _get_lot_info(self):
        # self.ensure_one()
        for rec in self:
            prod = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)])
            lots = self.env['stock.production.lot'].search([('product_id', '=', prod.id)])
            sorted_lots = sorted(lots.filtered(lambda x: x.product_qty > 0.0), key=lambda s: (s.name, s.create_date))
            if len(sorted_lots)>0:
                rec.millesime = str(sorted_lots[0].name)
            else:
                rec.millesime = False

    def get_producteur(self):
        website_id = self.env.context.get('website_id',False)
        prod = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if prod and website_id:
            website = self.env['website'].browse(website_id)
            seller = prod[0]._select_seller_with_website(website_id=website)
            return seller.name
        else:
            return False

    def get_similar_products(self):
        producteur = self.get_producteur()
        cant_frs_prods = []
        if not producteur.is_published:
            return cant_frs_prods
        current_website = self.env['website'].get_current_website()
        cant_frs_prods_lst = []
        lst = []
        if producteur.canton:
            for cant_frs in self.env['res.partner'].search([('is_published','=', True),('canton', '=', producteur.canton)]):
                if current_website.id in cant_frs.website_ids.ids:
                    for prod in self.env['product.template'].search([('id','!=', self.id),('is_published','=', True)]):
                        if cant_frs in prod.seller_ids.mapped('name') and current_website.id in prod.website_ids.ids:
                            cant_frs_prods_lst.append({'prod':prod, 'cant_frs':cant_frs})
        if cant_frs_prods_lst:
            for ind, elem in enumerate(cant_frs_prods_lst):
                lst.append(elem)
                if ((ind + 1) % 3 == 0):
                    cant_frs_prods.append(lst)
                    lst = []
            if len(lst) > 0:
                cant_frs_prods.append(lst)
                lst = []
        if len(cant_frs_prods)>1:
            cant_frs_prods = cant_frs_prods[::-1]
        return cant_frs_prods

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    website_id = fields.Many2one("website", string="Website", ondelete="restrict", index=True)
