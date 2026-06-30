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
	// Fetch the lead's project_location so we can pre-fill BOQ location
	const lead = frm.doc.lead;
	const getLocation = lead
		? frappe.db.get_value("Lead", lead, ["project_location", "lead_name"])
		: Promise.resolve({ message: {} });

	Promise.resolve(getLocation).then((r) => {
		const lead_data = (r && r.message) ? r.message : {};
		const plot_area = flt(frm.doc.lengthft) * flt(frm.doc.widthft);
		const project_title = (frm.doc.lead_name || lead_data.lead_name || "")
			? `${frm.doc.lead_name || lead_data.lead_name} Residence`
			: "";

		frappe.new_doc("BOQ", {
			site_analysis: frm.doc.name,
			lead: frm.doc.lead,
			location: lead_data.project_location || "",
			project_title: project_title,
			plot_area_sqft: flt(plot_area, 2),
			date: frappe.datetime.get_today(),
		});
	});
}
