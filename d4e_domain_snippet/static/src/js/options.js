odoo.define('d4e_domain_snippet.dynamic_domain_snippet_options', function (require) {
'use strict';

const snippetsOptions = require('web_editor.snippets.options');

const DynamicSnippetOwlItemOptions = snippetsOptions.Class.extend({
    start: function () {
        var self = this;
        self.$el.find('.duplicateCarouselItem').click(function (event) {
            self._duplicateCarouselItem(event);
        });
    },
    _duplicateCarouselItem: function (event) {
        var self = this;
        const item = self.$target.find('.item').clone();
        const $container = self.$target.parent().parent().parent();
        $container.trigger('add.owl.carousel', item.get(0).outerHTML);
        $container.trigger('refresh.owl.carousel');
    },
});

snippetsOptions.registry.dynamic_domain_snippet_owl_item = DynamicSnippetOwlItemOptions;

return DynamicSnippetOwlItemOptions;

});
