// Copyright (c) 2026, Cos and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Analysis', {
    lengthft: function(frm) { calc_area(frm); },
    widthft:  function(frm) { calc_area(frm); }
});
function calc_area(frm) {
    frm.set_value('total_area', 
        (frm.doc.lengthft || 0) * (frm.doc.widthft || 0));
}