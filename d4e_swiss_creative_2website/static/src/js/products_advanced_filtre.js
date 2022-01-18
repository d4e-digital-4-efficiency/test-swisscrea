odoo.define('d4e_swiss_creative_2website.advanced_search', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');

publicWidget.registry.websiteAdvancedFilterSelect = publicWidget.Widget.extend({
    selector: '.contenance_select',
    events: {
        'change #contenance': '_onContenanceSelectChange',
    },

    _onContenanceSelectChange: function(sel){
        let select = document.querySelector('#contenance');
        let filters = {};
        if (!(select.value === "")){
           filters['contenance'] =  [select.value];
        }
        let val1 = document.getElementById('slider-range-value1').firstElementChild.innerHTML
        let val2 = document.getElementById('slider-range-value2').firstElementChild.innerHTML

        Array.from($(".elemcheckfiltre")).forEach((check) => {
            if (check.checked){
                if(!(check.attributes.parent.value in filters)){
                    filters[check.attributes.parent.value] = []
                    filters[check.attributes.parent.value].push(check.name);
                } else {
                    filters[check.attributes.parent.value].push(check.name);
                    }
            }
        });
        let url_filter = '';
        let prices = [val1.replace(/\s+/g, '').replace(/[\n\r]/g, ''), val2.replace(/\s+/g, '').replace(/[\n\r]/g, '')];
        url_filter = 'list_price' + '=' + prices;
        for(var key in filters){
            let val = filters[key];
            url_filter = url_filter + '&' + key + '=' + val.toString();
        }

        if (url_filter){
            window.location.href = '/shop/filter/'+ url_filter;
        }
    }
})


publicWidget.registry.websiteAdvancedFilter = publicWidget.Widget.extend({
    selector: '.checkfiltre',
    events: {
        'click .elemcheckfiltre': '_onClickcheckfiltre',
    },

    _onClickcheckfiltre: function (cb) {
        let select = document.querySelector('#contenance');
        let filters = {};
        if (!(select.value === "")){
           filters['contenance'] =  [select.value];
        }
        Array.from($(".elemcheckfiltre")).forEach((check) => {
            if (check.checked){
                if(!(check.attributes.parent.value in filters)){
                    filters[check.attributes.parent.value] = []
                    filters[check.attributes.parent.value].push(check.name);
                } else {
                    filters[check.attributes.parent.value].push(check.name);
                    }
            }
        });
        let url_filter = '';
//        debugger;
        let val1 = document.getElementById('slider-range-value1').firstElementChild.innerHTML
        let val2 = document.getElementById('slider-range-value2').firstElementChild.innerHTML
        let prices = [val1.replace(/\s+/g, '').replace(/[\n\r]/g, ''), val2.replace(/\s+/g, '').replace(/[\n\r]/g, '')];
        url_filter = 'list_price' + '=' + prices;

        for(var key in filters){
            let val = filters[key]
            url_filter = url_filter + '&' + key + '=' + val.toString();
        }
        if (url_filter){
            window.location.href = '/shop/filter/'+ url_filter;
            }
    }
});


publicWidget.registry.websiteAdvancedFilterPrice = publicWidget.Widget.extend({
    selector: '.price-slider',
    events: {
        'mouseup input[type=range]': '_onMouseUpRangePrice',
    },

    _onMouseUpRangePrice: function (pr){
//        debugger;
        let val1 = document.getElementById('slider-range-value1').innerHTML
        let val2 = document.getElementById('slider-range-value2').innerHTML

        let select = document.querySelector('#contenance');
        let filters = {};
        if (!(select.value === "")){
           filters['contenance'] =  [select.value];
        }
        Array.from($(".elemcheckfiltre")).forEach((check) => {
            if (check.checked){
                if(!(check.attributes.parent.value in filters)){
                    filters[check.attributes.parent.value] = []
                    filters[check.attributes.parent.value].push(check.name);
                } else {
                    filters[check.attributes.parent.value].push(check.name);
                    }
            }
        });

        let url_filter = '';
        let prices = [val1, val2];
        url_filter = 'list_price' + '=' + prices;
        for(var key in filters){
            let val = filters[key];
            url_filter = url_filter + '&' + key + '=' + val.toString();
        }

        if (url_filter){
            window.location.href = '/shop/filter/'+ url_filter;
        }

    }

});

(function() {
  var parent = document.querySelector(".price-slider");
  if(!parent) return;

  var rangeS = parent.querySelectorAll("input[type=range]");

  rangeS.forEach(function(el) {
    el.oninput = function() {
      var slide1 = parseFloat(rangeS[0].value),
        	slide2 = parseFloat(rangeS[1].value);

      if (slide1 > slide2) {
		[slide1, slide2] = [slide2, slide1];
      }

      document.getElementById('slider-range-value1').innerHTML = slide1;
      document.getElementById('slider-range-value2').innerHTML = slide2;
    }

  });

//  numberS.forEach(function(el) {
//    el.oninput = function() {
//		var number1 = parseFloat(numberS[0].value),
//		number2 = parseFloat(numberS[1].value);
//
//      if (number1 > number2) {
//        var tmp = number1;
//        numberS[0].value = number2;
//        numberS[1].value = tmp;
//      }
//
//      rangeS[0].value = number1;
//      rangeS[1].value = number2;
//
//    }
//  });

})();


publicWidget.registry.websiteAppAdvancedFilter = publicWidget.Widget.extend({
    selector: '.appfiltre',
    events: {
        'click .elemprappfiltre': '_onClickprappfiltre',
        'click .elemappfiltre': '_onClickappfiltre',
    },

    _onClickprappfiltre: function (pr_cb) {
        let del_filtre = pr_cb.currentTarget.name;
        let select = document.querySelector('#contenance');
        let filters = {};
        if (del_filtre != "contenance"){
            if (!(select.value === "")){
               filters['contenance'] =  [select.value];
            }
        }
        Array.from($(".elemcheckfiltre")).forEach((check) => {
            if (check.checked && check.attributes.parent.value != del_filtre){
                if(!(check.attributes.parent.value in filters)){
                    filters[check.attributes.parent.value] = []
                    filters[check.attributes.parent.value].push(check.name);
                } else {
                    filters[check.attributes.parent.value].push(check.name);
                    }
            }
        });
        let url_filter = '';
//            debugger;
        let val1 = document.getElementById('slider-range-value1').firstElementChild.innerHTML
        let val2 = document.getElementById('slider-range-value2').firstElementChild.innerHTML
        let prices = [val1.replace(/\s+/g, '').replace(/[\n\r]/g, ''), val2.replace(/\s+/g, '').replace(/[\n\r]/g, '')];
        url_filter = 'list_price' + '=' + prices;

        for(var key in filters){
            let val = filters[key]
            url_filter = url_filter + '&' + key + '=' + val.toString();
        }
        if (url_filter){
            window.location.href = '/shop/filter/'+ url_filter;
            }
    },

    _onClickappfiltre: function (app_cb) {
        let del_filtre = app_cb.currentTarget.name;
        let filters = {};
        Array.from($(".elemcheckfiltre")).forEach((check) => {
            if (check.checked && check.name != del_filtre){
                if(!(check.attributes.parent.value in filters)){
                    filters[check.attributes.parent.value] = []
                    filters[check.attributes.parent.value].push(check.name);
                } else {
                    filters[check.attributes.parent.value].push(check.name);
                    }
            }
        });
        let url_filter = '';
//            debugger;
        let val1 = document.getElementById('slider-range-value1').firstElementChild.innerHTML
        let val2 = document.getElementById('slider-range-value2').firstElementChild.innerHTML
        let prices = [val1.replace(/\s+/g, '').replace(/[\n\r]/g, ''), val2.replace(/\s+/g, '').replace(/[\n\r]/g, '')];
        url_filter = 'list_price' + '=' + prices;

        for(var key in filters){
            let val = filters[key]
            url_filter = url_filter + '&' + key + '=' + val.toString();
        }
        if (url_filter){
            window.location.href = '/shop/filter/'+ url_filter;
            }
    }
});

publicWidget.registry.websiteSearchFilters = publicWidget.Widget.extend({
    selector: '.search_filtre',
    events: {
        'click .search_filtre_btn': '_onSearchSubmitClick',
        'keyup input[type=search]': '_onSearchInputKeyup',
    },

    /**
     * @private
     */
    _search: function () {
          let srch = this.el.firstElementChild.value
          let filtre = this.el.firstElementChild.name

            Array.from($(".elemcheckfiltre")).forEach((check) => {
                if (check.attributes.parent.value == filtre){
                    let node = check.parentNode;
                    if (!(srch.length === 0)){
                        if ((!(srch.includes(check.name))) && (!(check.name.includes(srch)))){
                            node.style.display = "none";
                        } else {
                            node.style.display = "inherit";
                        }
                    } else {
                        node.style.display = "inherit";
                    }
                }
            });
    },

    /**
     * @private
     */
    _onSearchSubmitClick: function () {
        this._search();
    },

    /**
     * @private
     */
    _onSearchInputKeyup: function (ev) {
        if (ev.keyCode === $.ui.keyCode.ENTER) {
            this._search();
        }
    },

});

$('.search_filtre_input').on('search', function() {
        let srch = this.value
        let filtre = this.name
        if (srch.length === 0){
            Array.from($(".elemcheckfiltre")).forEach((check) => {
                if (check.attributes.parent.value == filtre){
                    let node = check.parentNode;
                    node.style.display = "inherit";
                }
            });
        }
    });
});