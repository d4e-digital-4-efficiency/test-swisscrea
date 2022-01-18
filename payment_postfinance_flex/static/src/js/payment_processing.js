odoo.define('payment_postfinance_flex.payment_processing', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');

	var PaymentProcessing = publicWidget.registry.PaymentProcessing;

	PaymentProcessing.include({
	    xmlDependencies: PaymentProcessing.prototype.xmlDependencies.concat(
	        ['/payment_postfinance_flex/static/src/xml/payment.xml']
	    ),
    });
});

