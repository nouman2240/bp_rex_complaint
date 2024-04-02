/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.rex_complaint_form_address = publicWidget.Widget.extend({
    selector: '.rex_complaint_form_address',
    events: {
        'change select[name="building_id"]': '_onBuildingChange',
    },

    start: function () {
        var def = this._super.apply(this, arguments);

        this.$flat = this.$('select[name="flat_id"]');
        this.$flatOptions = this.$flat.filter(':enabled').find('option:not(:first)');
        this._adaptTenantAddress();

        return def;
    },

    _adaptTenantAddress: function () {
        var $building = this.$('select[name="building_id"]');
        var buildingID = ($building.val() || 0);
        this.$flatOptions.detach();
        var $displayedFlat = this.$flatOptions.filter('[data-building_id=' + buildingID + ']');
        var nb = $displayedFlat.appendTo(this.$flat).show().length;
        this.$flat.parent().parent().toggle(nb >= 1);
    },

    _onBuildingChange: function () {
        this._adaptTenantAddress();
    },
});