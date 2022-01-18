from odoo import api, fields, models, _

class CodesLaac(models.Model):
    _name = "codes.laac"



    code = fields.Char(string='Code')
    description = fields.Text(string='Description')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s %s' % (record.code, record.description or '')))
        return result

class CodesIjm(models.Model):
    _name = "codes.ijm"


    code = fields.Char(string='Code')
    description = fields.Text(string='Description')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id,'%s %s' %(record.code,record.description or '')))
        return result

class CodesLpp(models.Model):
    _name = "codes.lpp"


    code = fields.Char(string='Code')
    description = fields.Text(string='Description')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s %s' % (record.code, record.description or '')))
        return result
