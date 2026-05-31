frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Site Analysis', function() {
                frappe.new_doc('Site Analysis', {
                    lead: frm.doc.name,
                    lead_name: frm.doc.lead_name,
                    project_name: frm.doc.project_name,
                    project_location: frm.doc.project_location
                });
            }, 'Create');
        }
    }
});