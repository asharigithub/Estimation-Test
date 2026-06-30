// Copyright (c) 2026, Cos and contributors
// For license information, please see license.txt

frappe.ui.form.on("Site Analysis", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("BOQ"), () => _create_boq(frm), __("Create"));
		}
	},
});

function _create_boq(frm) {
	const plotArea = flt(frm.doc.lengthft) * flt(frm.doc.widthft);
	const projectTitle = frm.doc.lead_name ? `${frm.doc.lead_name} Residence` : "";

	frappe.new_doc("BOQ", {
		site_analysis: frm.doc.name,
		lead: frm.doc.lead || "",
		project_title: projectTitle,
		plot_area_sqft: flt(plotArea, 2),
		date: frappe.datetime.get_today(),
	});
}
