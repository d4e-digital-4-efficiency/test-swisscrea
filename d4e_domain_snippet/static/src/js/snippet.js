odoo.define('d4e_domain_snippet.dynamic_domain_snippet', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

const DynamicSnippet = publicWidget.Widget.extend({
    selector: '.res_domain_snippet',
    disabledInEditableMode: false,
    start: function () {
        const self = this;
        return this._super.apply(this, arguments).then(() => {
            const customOptions = self._readSnippetOptions();
            const options = {
                margin: 0,
                touchDrag: !self.options.editableMode,
                mouseDrag: !self.options.editableMode,
                items: customOptions.nb,
            };
            var $items = self.$el.find('.owl-carousel .owl-item:not(.cloned) .item').clone();
            if ($items.length === 0) {
                $items = self.$el.find('.carousel-items .item').clone();
            }
            if ($items.length === 0) {
                $items = $('<tmp />');
                self._rpc({
                    'route': '/d4e_domain_snippet/snippets/domain',
                    'params': {
                        'search_domain': self._getSearchDomain(),
                    },
                }).then(function (data) {
                    const result = JSON.parse(data) || [];
                    for (var i = 0; i < result.length; i++) {
                        const element = result[i];
                        var $img = $('<img />', {
                            class: 'd-block img-fluid figure-img rounded shadow-lg',
                            style: 'width: 100%;',
                            src: element.image,
                            alt: element.name,
                            loading: 'lazy',
                            'data-original-id': element.id,
                            'data-original-src': element.image,
                        });
                        var $title = $('<h3 />', {
                            style: 'text-align: center;',
                            text: element.name,
                            class: 'element-title o_default_snippet_text',
                        });
                        var $description = $(element.description);
                        var $item = $('<div />', {
                            class: 'item',
                        });
                        var $itemRow = $('<div />', {
                            class: 'row pl-4 pr-4',
                        });
                        $item.append($itemRow);
                        var $itemContent = $('<div />', {
                            class: 'col-12',
                        });
                        $itemRow.append($itemContent);
                        $itemContent.append($img);
                        $itemContent.append($title);
                        $itemContent.append($description);
                        $items.append($item);
                    }
                    const $itemChildren = $items.children();
                    const allowActivation = $itemChildren.length > options.items;
                    options.nav = allowActivation;
                    options.loop = allowActivation;
                    self.slider(self.$el.find('.owl-carousel'), options, $itemChildren);
                });
            } else {
                const allowActivation = $items.length > options.items;
                options.nav = allowActivation;
                options.loop = allowActivation;
                self.slider(self.$el.find('.owl-carousel'), options, $items);
            }
        });
    },
    slider: function (container, options, items) {
        const $carouselItemsHolder = this.$el.find('.carousel-items');
        $carouselItemsHolder.empty();
        $carouselItemsHolder.append(items.clone());
        container.trigger('destroy.owl.carousel');
        container.empty();
        container.owlCarousel(options);
        const itemsToAdd = items.clone();
        for (var i = 0; i < itemsToAdd.length; i++) {
            container.trigger('add.owl.carousel', itemsToAdd.get(i).outerHTML);
        }
        container.trigger('refresh.owl.carousel');
    },
    _getSearchDomain: function () {
        return [['is_published', '=', true]];
    },
    _readSnippetOptions: function () {
        var options = {
            nb: 1,
        };
        const $carousel = this.$el.find('.owl-carousel');
        var classes = $carousel.attr('class');
        if (classes) {
            classes = classes.split(' ');
            for (var i = 0; i < classes.length; i++) {
                var matches = /^carousel\-(.+)/.exec(classes[i]);
                if (matches != null) {
                    options.nb = parseInt(classes[i].split('-')[1]);
                    break;
                }
            }
        }
        return options;
    },
    destroy: function () {
        const $carousel = this.$el.find('.owl-carousel');
        const $carouselItems = $carousel.find('.owl-item:not(.cloned) .item');
        if ($carouselItems.length > 0) {
            const $carouselItemsHolder = this.$el.find('.carousel-items');
            $carouselItemsHolder.empty();
            $carouselItemsHolder.append($carouselItems.clone());
        }
        $carousel.trigger('destroy.owl.carousel');
        $carousel.empty();
        this._super.apply(this, arguments);
    },
});

publicWidget.registry.dynamic_domain_snippet = DynamicSnippet;

return DynamicSnippet;

});
