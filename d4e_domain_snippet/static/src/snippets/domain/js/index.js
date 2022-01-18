odoo.define('d4e_domain_snippet.dynamic_domain_snippet', function (require) {
'use strict';

const core = require('web.core');
const config = require('web.config');
const publicWidget = require('web.public.widget');

const DynamicSnippet = publicWidget.Widget.extend({
    selector: '.res_domain_snippet',
    xmlDependencies: [
        '/d4e_domain_snippet/static/src/snippets/domain/xml/data.xml',
    ],
    disabledInEditableMode: false,
    templateKey: 'd4e_domain_snippet.dynamic_domain_snippet.container',
    containerKey: '.dynamic_snippet_container',
    chunkSize: 3,
    init: function () {
        this.data = [];
        this.renderedContent = '';
        this.uniqueId = _.uniqueId('dynamic_domain_snippet_');
        this._super.apply(this, arguments);
    },
    willStart: function () {
        return this._super.apply(this, arguments).then(
            () => Promise.all([
                this._fetchData(),
            ])
        );
    },
    start: function () {
        const self = this;
        return this._super.apply(this, arguments).then(() => {
            self._render();
        });
    },
    destroy: function () {
        this._clearContent();
        this._super.apply(this, arguments);
    },
    _clearContent: function () {
        this.$el.find(this.containerKey).html('');
    },
    _isConfigComplete: function () {
        return this.templateKey !== undefined;
    },
    _getSearchDomain: function () {
        return [['is_published', '=', true]];
    },
    _fetchData: function () {
        const self = this;
        if (self._isConfigComplete()) {
            return self._rpc({
                'route': '/d4e_domain_snippet/snippets/domain',
                'params': {
                    'search_domain': self._getSearchDomain(),
                },
            }).then((data) => {
                self.data = JSON.parse(data);
            });
        } else {
            return new Promise((resolve) => {
                self.data = [];
                resolve();
            });
        }
    },
    _prepareContent: function () {
        const self = this;
        if (self.data.length) {
            self.renderedContent = core.qweb.render(self.templateKey, self._getQWebRenderOptions());
        } else {
            self.renderedContent = '';
        }
    },
    _getQWebRenderOptions: function () {
        return {
            data: this.data,
            uniqueId: this.uniqueId,
            chunkSize: (config.device.isMobile) ? 1 : this.chunkSize,
        };
    },
    _render: function () {
        this._prepareContent();
        this._renderContent();
    },
    _renderContent: function () {
        this.$el.find(this.containerKey).html(this.renderedContent);
    },
});

publicWidget.registry.dynamic_domain_snippet = DynamicSnippet;

return DynamicSnippet;

});
