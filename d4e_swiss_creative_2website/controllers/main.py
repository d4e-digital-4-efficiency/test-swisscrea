# -*- coding: utf-8 -*-

import logging
from werkzeug.exceptions import NotFound
import math

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.osv import expression
_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    def _get_advanced_filtre_element(self):
        styles_ids = styles = []
        accords_ids = accords = []
        prods = request.env['product.template'].search([], order='id asc').filtered(lambda prod: request.website.id in prod.website_ids.ids)
        for prod in prods.filtered('accord_ids'):
            accords_ids = accords_ids + prod.accord_ids.ids
        accords_ids = list(set(accords_ids))
        if len(accords_ids):
            accords = list(set(request.env['wine.accord'].browse(accords_ids).mapped('name')))
        for prod in prods.filtered('style_ids'):
            styles_ids = styles_ids + prod.style_ids.ids
        styles_ids = list(set(styles_ids))
        if len(styles_ids):
            styles = list(set(request.env['wine.style'].browse(styles_ids).mapped('name')))
        vin_types = list(set(prods.filtered('vin_type').mapped('vin_type')))
        cepages = list(set(prods.filtered('cepage').mapped('cepage')))
        contenances = list(set(prods.filtered('contenance').mapped('contenance')))
        aocs = list(set(prods.filtered('aoc').mapped('aoc')))
        prices = sorted(list(set(prods.mapped('list_price'))))
        # aocs = []
        # for prod in prods:
        #     for line in prod.seller_ids:
        #         if line.name.aoc and line.name.aoc not in aocs:
        #             aocs.append(line.name.aoc)
        # aocs = list(set(aocs))
        return {'contenance': contenances, 'vin_type': vin_types, 'Région': aocs, 'cepage': cepages, 'style': styles, 'accord': accords, 'prices':prices}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/filter/<string:filters>''',
        '''/shop/filter/<string:filters>/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, filters='', **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            # ppg = request.env['website'].get_current_website().shop_ppg or 20
            ppg = 9

        # ppr = request.env['website'].get_current_website().shop_ppr or 4
        ppr = 3

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)
        frs_prods = []
        prods = request.env['product.template'].search([], order='id asc').filtered(
            lambda prod: request.website.id in prod.website_ids.ids)
        if search:
            for srch in search.split(" "):
                for prod in prods:
                    if (len(prod.seller_ids) > 0) and all((line.website_id == False) for line in prod.seller_ids):
                        frs_prods.append(prod.id)
                    else:
                        for line in prod.seller_ids:
                            if ((line.name.name.lower() in srch.lower()) or (srch.lower() in line.name.name.lower())) and line.website_id.id == request.website.id:
                                frs_prods.append(prod.id)
                                break
        if len(frs_prods)>0:
            frs_prods = list(set(frs_prods))
            domain.insert(0,('id', 'in', frs_prods))
            if len(domain)>1:
                domain.insert(0, '|')

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        # search_product = Product.search(domain, order=self._get_search_order(post))
        search_product = Product.browse([])
        for prod in Product.search(domain, order=self._get_search_order(post)):
            if request.website.id in prod.website_ids.ids :
                search_product |= prod

        # filtres
        app_filters = {}
        app_dom_price = []
        if len(filters) > 0:
            lst_filters = filters.split('&')
            for elem in lst_filters:
                lst = elem.split('=')
                app_filters[lst[0]] = lst[1].split(',')
            dom = []
            ids_region = []
            ids_style = []
            ids_accord = []
            ids = []
            for key in app_filters:
                if key in ['Région', 'style', 'accord']:
                    if key == 'Région':
                        # for prod in prods:
                        #     for line in prod.seller_ids:
                        #         if line.name.aoc in list(set(app_filters[key])):
                        #             ids_region.append(prod.id)
                        # if not(len(ids_region)> 0):
                        #     prods = request.env['product.template']
                        # else:
                        #     prods = request.env['product.template'].browse(ids_region)
                        dom.append(('aoc', 'in', list(set(app_filters[key]))))
                    elif key == 'style':
                        styles = request.env['wine.style'].search([('name', 'in', list(set(app_filters[key])))])
                        styles_ids = [] if not styles else styles.mapped('id')
                        for prod in prods:
                            if any(style in styles_ids for style in prod.style_ids.ids):
                                ids_style.append(prod.id)
                        if not(len(ids_style)> 0):
                            prods = request.env['product.template']
                        else:
                            prods = request.env['product.template'].browse(ids_style)
                    elif key == 'accord':
                        accords = request.env['wine.accord'].search([('name', 'in', list(set(app_filters[key])))])
                        accord_ids = [] if not accords else accords.mapped('id')
                        for prod in prods:
                            if any(accord in accord_ids for accord in prod.accord_ids.ids):
                                ids_accord.append(prod.id)
                        if not(len(ids_accord) > 0):
                            prods = request.env['product.template']
                        else:
                            prods = request.env['product.template'].browse(ids_accord)
                elif key == 'list_price':
                    app_dom_price = [float(app_filters[key][0]), float(app_filters[key][1])]
                else:
                    dom.append((key, 'in', list(set(app_filters[key]))))

            if len(app_dom_price) > 0:
                # ids = []
                for prod in prods:
                    price = pricelist.get_product_price(prod, [1.0], [request.env.user.partner_id])
                    fpos = request.env['account.fiscal.position'].get_fiscal_position(request.env.user.partner_id.id)
                    taxes = prod.taxes_id.filtered(lambda t: t.company_id == request.website.company_id)
                    tax_id = fpos.map_tax(taxes, prod, request.env.user.partner_id)
                    taxes = tax_id.compute_all(price, pricelist.currency_id, 1.0,
                                                    product=prod, partner=request.env.user.partner_id)
                    price = taxes['total_excluded']
                    if (price >= app_dom_price[0]) and (price <= app_dom_price[1]):
                        ids.append(prod.id)

            if len(ids) > 0:
                ids = list(set(ids))
                dom.append(('id', 'in', ids))
            if len(dom)>0:
                search_product = search_product.search(dom)
            else:
                search_product = request.env['product.template']

        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)
        if len(app_filters)>0:
            url = http.request.httprequest.full_path
            if url[-1] == '?':
                url = url[:-1]
            if '/page' in url:
                url = url[:url.find('/page/')]

        product_count = len(search_product)
        # pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=int(math.ceil(float(product_count) / ppg)), url_args=post)
        offset = pager['offset']
        search_product = search_product.sorted('qty_available', reverse=True)
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        adv_filtre = self._get_advanced_filtre_element()
        if len(adv_filtre['prices'])>0:
            min_max_prices = [float(int(adv_filtre['prices'][0])-1), float(int(adv_filtre['prices'][-1])+1)]
        else:
            min_max_prices = [1.0,100.0]
        del adv_filtre['prices']
        values = {
            'adv_filtre': adv_filtre,
            'filters' : app_filters,
            'min_max_prices':min_max_prices,
            'dom_price':app_dom_price,
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)


    @http.route([
        '''/producteurs''',
        '''/producteurs/page/<int:page>'''], type='http', auth="public", website=True, sitemap=True)
    def get_producteurs(self, page=0, search='', ppg=False, **post):
        ppg = 9
        ppr = 3
        current_website = request.env['website'].get_current_website()
        producteurs = []
        lst_producteurs = []
        subdomains = []
        domains = []
        if search:
            for srch in search.split(" "):
                subdomains.append([('name', 'ilike', srch)])
                # domains.append(expression.OR(subdomains))
        if len(subdomains) > 0:
            domains.append(expression.OR(subdomains))

        domains = domains[0] if len(domains)>0 else []
        # for rec in request.env['res.partner'].search(domains):
        #     lst_producteurs.append(rec)

        for rec in request.env['res.partner'].search(domains):
            if rec.is_published and current_website.id in rec.website_ids.ids:
                lst_producteurs.append(rec)
        # pager = request.website.pager(url="/producteurs", total=len(lst_producteurs), page=page, step=ppg, scope=7, url_args=post)
        pager = request.website.pager(url="/producteurs", total=len(lst_producteurs), page=page, step=ppg, scope=int(math.ceil(float(len(lst_producteurs)) / ppg)), url_args=post)
        offset = pager['offset']
        lst_producteurs = lst_producteurs[offset: offset + ppg]
        lst = []
        for ind, elem in enumerate(lst_producteurs):
            lst.append(elem)
            if((ind+1) % ppr == 0):
                producteurs.append(lst)
                lst = []
        if len(lst)>0:
            producteurs.append(lst)
            lst = []

        values={
            'search': search,
            'pager': pager,
            'ppg': ppg,
            'ppr': ppr,
            'producteurs': producteurs,
        }
        return request.render("d4e_swiss_creative_2website.producteurs", values)

    def _get_producteur_product(self, producteur):
        lst_prods = []
        current_website = request.env['website'].get_current_website()
        if producteur:
            for prod in request.env['product.template'].search([('is_published','=', True)]):
                if producteur in prod.seller_ids.mapped('name') and current_website.id in prod.website_ids.ids:
                    lst_prods.append(prod)
        # prods = []
        # lst = []
        # if lst_prods:
        #     for ind, elem in enumerate(lst_prods):
        #         lst.append(elem)
        #         if ((ind + 1) % 2 == 0):
        #             prods.append(lst)
        #             lst = []
        #     if len(lst) > 0:
        #         prods.append(lst)
        #         lst = []
        # return prods
        return lst_prods

    @http.route(['/producteurs/<model("res.partner"):producteur>'], type='http', auth="public", website=True, sitemap=True)
    def producteur(self, producteur, **kwargs):
        if not producteur.is_published:
            raise NotFound()
        current_website = request.env['website'].get_current_website()
        cant_frs_prods_lst = []
        lst = []
        cant_frs_prods = []
        vin_domain = self._get_producteur_product(producteur)
        if len(vin_domain)>2:
            for vin in vin_domain[2:] :
                cant_frs_prods_lst.append({'prod': vin, 'cant_frs': producteur})
            vin_domain = vin_domain[:2]
        if producteur.canton:
            for cant_frs in request.env['res.partner'].search([('id', '!=', producteur.id),('is_published','=', True),('canton', '=', producteur.canton)]):
                if current_website.id in cant_frs.website_ids.ids:
                    for prod in request.env['product.template'].search([('is_published','=', True)]):
                        if cant_frs in prod.seller_ids.mapped('name') and current_website.id in prod.website_ids.ids:
                            cant_frs_prods_lst.append({'prod':prod, 'cant_frs':cant_frs})

        if not len(cant_frs_prods_lst)>0:
            if producteur.aoc:
                for cant_frs in request.env['res.partner'].search(
                        [('id', '!=', producteur.id), ('is_published', '=', True), ('aoc', '=', producteur.aoc)]):
                    if current_website.id in cant_frs.website_ids.ids:
                        for prod in request.env['product.template'].search([('is_published', '=', True)]):
                            if cant_frs in prod.seller_ids.mapped(
                                    'name') and current_website.id in prod.website_ids.ids:
                                cant_frs_prods_lst.append({'prod': prod, 'cant_frs': cant_frs})

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
        values = {
            'producteur': producteur,
            'products': vin_domain,
            'cant_frs_prods': cant_frs_prods,
            }

        return request.render("d4e_swiss_creative_2website.producteur", values)

    @http.route([
        '''/pass-provino'''], type='http', auth="public", website=True, sitemap=True)
    def get_pass_provino(self, page=0, search='', ppg=False, **post):
        values={}
        vignerons={}
        for line in request.env['res.partner'].search([('pass_provino','=', True)]):
            if line.canton not in vignerons.keys():
                vignerons[line.canton] = [line.name]
            else:
                vignerons[line.canton].append(line.name)

        lim = len(list(vignerons))//2 + len(list(vignerons))%2 if len(list(vignerons))>1 else len(list(vignerons))
        values = {
            'vignerons':vignerons,
            'lim': lim,
        }
        return request.render("d4e_swiss_creative_2website.pass_provino", values)