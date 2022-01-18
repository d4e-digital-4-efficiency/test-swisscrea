# -*- coding: utf-8 -*-
#################################################################################
# Author      : PIT Solutions AG. (<https://www.pitsolutions.ch/>)
# Copyright(c): 2019 - Present PIT Solutions AG.
# License URL : https://www.webshopextension.com/en/licence-agreement/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.webshopextension.com/en/licence-agreement/>
#################################################################################

import datetime
from odoo import fields, models, api, _

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

EXCEPTION_LOG_TYPE = {
    ('red', _("Danger")),
    ('olive', _("Warning")),
    ('gray', _("Info")),
    ('green', _("Success")),
}


class PaymentAcquirerLog(models.Model):
    _name = "payment.acquirer.log"
    _description = "Payment acquirer log details"
    _order = "id desc"

    name = fields.Char(string="Description", required=True)
    detail = fields.Html(string="Detail",)
    origin = fields.Char(string="Origin", default='postfinance', readonly=True)
    type = fields.Selection(EXCEPTION_LOG_TYPE, string="Type",
                            default='gray', readonly=True, required=True)

    @api.model
    def clean_old_logging(self, days=90):
        """
        Function called by a cron to clean old loggings.
        @return: True
        """
        last_days = datetime.datetime.now() +\
            datetime.timedelta(days=-days)
        domain = [
            ('create_date', '<', last_days.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT))
        ]
        logs = self.search(domain)
        logs.unlink()
        message = " %d logs are deleted" % (len(logs))
        return self._post_log({'name': message})

    @api.model
    def _post_log(self, vals):
        self.create(vals)
        self.env.cr.commit()
        
