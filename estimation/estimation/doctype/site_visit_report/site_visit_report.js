// Copyright (c) 2026, Cos and contributors
// For license information, please see license.txt

const CHECKLIST_BY_VISIT_TYPE = {
	"Weekly QC Visit": [
		{checklist_item: "Check workmanship quality of ongoing work", category: "Quality"},
		{checklist_item: "Verify materials used match approved specifications", category: "Material"},
		{checklist_item: "Confirm drawings are being followed on site", category: "Quality"},
		{checklist_item: "Check structural member dimensions and alignment", category: "Quality"},
		{checklist_item: "Inspect reinforcement cover and placement", category: "Quality"},
		{checklist_item: "Review site safety conditions and PPE compliance", category: "Safety"},
	],
	"Progress Review": [
		{checklist_item: "Verify tasks completed since last visit", category: "Progress"},
		{checklist_item: "Confirm work is on schedule per project plan", category: "Progress"},
		{checklist_item: "Check pending approvals or hold points", category: "Progress"},
		{checklist_item: "Review material availability for next stage", category: "Material"},
		{checklist_item: "Identify any rework or remedial work needed", category: "Quality"},
	],
	"Finishing Stage Daily Check": [
		{checklist_item: "Tile works — alignment, grouting, breakage", category: "Quality"},
		{checklist_item: "Ceiling works — level, cracks, finish", category: "Quality"},
		{checklist_item: "Painting — consistency, brush marks, coverage", category: "Quality"},
		{checklist_item: "Wardrobes and kitchen cabinets — fit and finish", category: "Quality"},
		{checklist_item: "Electrical fixtures — switches, sockets, fittings", category: "Quality"},
		{checklist_item: "Plumbing fittings — leaks, water pressure test", category: "Quality"},
		{checklist_item: "Door and window operation — gaps, latches", category: "Quality"},
		{checklist_item: "Handover checklist items verified", category: "Progress"},
	],
	"Safety Check": [
		{checklist_item: "Scaffolding secured and tagged", category: "Safety"},
		{checklist_item: "Workers wearing PPE (helmet, boots, gloves)", category: "Safety"},
		{checklist_item: "Electrical temporary connections are safe", category: "Safety"},
		{checklist_item: "No open trenches left unprotected", category: "Safety"},
		{checklist_item: "Fire extinguisher available on site", category: "Safety"},
		{checklist_item: "First aid kit present and stocked", category: "Safety"},
	],
	"Material Verification": [
		{checklist_item: "Cement brand and grade verified", category: "Material"},
		{checklist_item: "Steel TMT grade and manufacturer verified", category: "Material"},
		{checklist_item: "Bricks/blocks — size, quality, quantity check", category: "Material"},
		{checklist_item: "Sand — source, cleanliness, silt content", category: "Material"},
		{checklist_item: "Tiles — brand, shade, quantity match BOQ", category: "Material"},
		{checklist_item: "Electrical and plumbing materials — approved brands", category: "Material"},
		{checklist_item: "Material delivery challan matched to purchase order", category: "Material"},
	],
};

frappe.ui.form.on("Site Visit Report", {
	onload(frm) {
		if (frm.is_new() && !frm.doc.inspector) {
			frm.set_value("inspector", frappe.session.user);
		}
		if (frm.is_new() && !frm.doc.visit_date) {
			frm.set_value("visit_date", frappe.datetime.get_today());
		}
	},

	visit_type(frm) {
		if (!frm.doc.visit_type) return;
		const items = CHECKLIST_BY_VISIT_TYPE[frm.doc.visit_type] || [];
		if (!items.length) return;

		frappe.confirm(
			`Load default checklist for <b>${frm.doc.visit_type}</b>? This will replace any existing checklist rows.`,
			() => {
				frm.clear_table("checklist");
				items.forEach(row => frm.add_child("checklist", row));
				frm.refresh_field("checklist");
			}
		);
	},
});
