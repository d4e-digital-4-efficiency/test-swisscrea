odoo.define('d4e_pack_accounting.section_and_note_subtotal_backend', function (require) {
// The goal of this file is to contain JS hacks related to allowing
// section and note on sale order and invoice.

// [UPDATED] now also allows configuring products on sale order.

"use strict";
var FieldChar = require('web.basic_fields').FieldChar;
var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
var fieldRegistry = require('web.field_registry');
var ListFieldText = require('web.basic_fields').ListFieldText;
var SectionAndNoteListRenderer = require('account.section_and_note_backend');

var SubSectionAndNoteListRenderer = SectionAndNoteListRenderer.extend({

    _renderBodyCell: function (record, node, index, options) {
    console.log("d4e_pack_accounting  _renderBodyCell ")
        var $cell = this._super.apply(this, arguments);

        var isSection = record.data.display_type === 'line_section';
        var isNote = record.data.display_type === 'line_note';
        var isSubTotal = record.data.display_type === 'line_sub_total';
        var isSubTotalLine = record.data.display_type === 'line_subtotal';
        var isTitle = record.data.display_type === 'line_title';

        if (isSection || isNote || isSubTotal || isTitle || isSubTotalLine) {
            if (node.attrs.widget === "handle") {
                return $cell;
            } else if (node.attrs.name === "name") {
                var nbrColumns = this._getNumberOfCols();
                if (this.handleField) {
                    nbrColumns--;
                }
                if (this.addTrashIcon) {
                    nbrColumns--;
                }
                $cell.attr('colspan', nbrColumns);
            } else {
                $cell.removeClass('o_invisible_modifier');
                return $cell.addClass('o_hidden');
            }

        }

        return $cell;
    },

});

// We create a custom widget because this is the cleanest way to do it:
// to be sure this custom code will only impact selected fields having the widget
// and not applied to any other existing ListRenderer.
var SectionAndNoteFieldOne2Many = FieldOne2Many.extend({
    /**
     * We want to use our custom renderer for the list.
     *
     * @override
     */
    _getRenderer: function () {
        if (this.view.arch.tag === 'tree') {
            return SubSectionAndNoteListRenderer;
        }
        return this._super.apply(this, arguments);
    },
});

// This is a merge between a FieldText and a FieldChar.
// We want a FieldChar for section,
// and a FieldText for the rest (product and note).
var SectionAndNoteFieldText = function (parent, name, record, options) {
    var isSection = record.data.display_type === 'line_section';
    var Constructor = isSection ? FieldChar : ListFieldText;
    return new Constructor(parent, name, record, options);
};

fieldRegistry.add('section_and_note_one2many', SectionAndNoteFieldOne2Many);
fieldRegistry.add('section_and_note_text', SectionAndNoteFieldText);

return SubSectionAndNoteListRenderer;
});
