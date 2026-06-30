// Copyright (c) 2026, Cos and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Load Scope of Work"),
				() => _load_scope_of_work(frm),
				__("Estimation")
			);

			frm.add_custom_button(
				__("New Site Visit Report"),
				() => _new_site_visit_report(frm),
				__("Estimation")
			);
		}
	},
});

function _load_scope_of_work(frm) {
	frappe.confirm(
		`This will create <b>15 category tasks</b> and <b>84 scope-of-work child tasks</b> under project <b>${frm.doc.name}</b>.<br><br>
		Already-existing tasks will be skipped (safe to re-run). Continue?`,
		() => {
			frappe.show_alert({message: __("Creating tasks…"), indicator: "blue"});
			frappe.call({
				method: "estimation.estimation.utils.project_tasks.create_scope_of_work_tasks",
				args: {project: frm.doc.name},
				callback(r) {
					if (r.message) {
						frappe.show_alert({
							message: r.message.message,
							indicator: "green",
						});
					}
				},
			});
		}
	);
}

function _new_site_visit_report(frm) {
	frappe.new_doc("Site Visit Report", {project: frm.doc.name});
}
