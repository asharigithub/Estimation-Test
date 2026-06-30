// Copyright (c) 2026, Cos and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lead", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Site Analysis"), () => {
				frappe.new_doc("Site Analysis", {
					lead: frm.doc.name,
					lead_name: frm.doc.lead_name,
				});
			}, __("Create"));

			frm.add_custom_button(__("BOQ"), () => _create_boq_from_lead(frm), __("Create"));

			frm.add_custom_button(__("House Construction Calculator"), () => {
				frappe.new_doc("House Construction Calculator", {
					owner_name: frm.doc.lead_name,
				});
			}, __("Create"));
		}
	},
});

function _create_boq_from_lead(frm) {
	frappe.db.get_value(
		"Site Analysis",
		{lead: frm.doc.name},
		["name", "lengthft", "widthft"],
		(sa) => {
			const plotArea = sa ? flt(sa.lengthft) * flt(sa.widthft) : 0;
			frappe.new_doc("BOQ", {
				lead: frm.doc.name,
				site_analysis: sa ? sa.name : "",
				project_title: frm.doc.lead_name ? `${frm.doc.lead_name} Residence` : "",
				plot_area_sqft: flt(plotArea, 2),
				date: frappe.datetime.get_today(),
			});
		}
	);
}
