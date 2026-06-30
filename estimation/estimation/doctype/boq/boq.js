// Copyright (c) 2026, Cos and contributors
// For license information, please see license.txt

frappe.ui.form.on("BOQ", {
	onload(frm) {
		if (frm.is_new()) {
			if (!frm.doc.prepared_by) frm.set_value("prepared_by", frappe.session.user);
			if (!frm.doc.date) frm.set_value("date", frappe.datetime.get_today());
		}
	},

	refresh(frm) {
		_add_buttons(frm);
	},

	// When Site Analysis is selected, pull lead + plot area from it
	site_analysis(frm) {
		if (!frm.doc.site_analysis) return;
		frappe.db.get_doc("Site Analysis", frm.doc.site_analysis).then((sa) => {
			if (sa.lead && !frm.doc.lead)
				frm.set_value("lead", sa.lead);
			if (sa.lengthft && sa.widthft)
				frm.set_value("plot_area_sqft", flt(flt(sa.lengthft) * flt(sa.widthft), 2));
			if (!frm.doc.project_title && sa.lead_name)
				frm.set_value("project_title", `${sa.lead_name} Residence`);
		});
	},

	// Building dimension triggers — recalc BUA then formula quantities live
	ground_floor_bua_sqft(frm) { _calc_bua(frm); _recalculate_formula_qtys(frm); },
	first_floor_bua_sqft(frm)  { _calc_bua(frm); _recalculate_formula_qtys(frm); },
	no_of_floors(frm)          { _recalculate_formula_qtys(frm); },
	plot_area_sqft(frm)        { _recalculate_formula_qtys(frm); },
	wastage_percent(frm)       { _recalculate_formula_qtys(frm); },
	external_wall_mm(frm)      { _recalculate_formula_qtys(frm); },
	internal_wall_mm(frm)      { _recalculate_formula_qtys(frm); },
	floor_height_mm(frm)       { _recalculate_formula_qtys(frm); },

	contingency_percent(frm)   { _calc_grand_total(frm); },
	overhead_percent(frm)      { _calc_grand_total(frm); },
});

frappe.ui.form.on("BOQ Section Item", {
	qty(frm, cdt, cdn)           { _calc_row(frm, cdt, cdn); },
	material_rate(frm, cdt, cdn) { _calc_row(frm, cdt, cdn); },
	labour_rate(frm, cdt, cdn)   { _calc_row(frm, cdt, cdn); },
	boq_items_remove(frm)        { _calc_section_totals(frm); },
});

// ─── Buttons ────────────────────────────────────────────────────────────────

function _add_buttons(frm) {
	if (frm.is_new()) return;

	frm.add_custom_button(__("Load from MQC Settings"), () => _load_from_settings(frm), __("Action"));

	if (!frm.doc.linked_quotation) {
		frm.add_custom_button(__("Create Quotation"), () => _create_quotation(frm), __("Action"));
	} else {
		frm.add_custom_button(__("Open Quotation"), () => {
			frappe.set_route("Form", "Quotation", frm.doc.linked_quotation);
		}, __("Action"));
	}
}

function _load_from_settings(frm) {
	frappe.confirm(
		`Load BOQ line items from <b>Material Quantity Calculator → BOQ Quantity Formulas</b>?<br><br>
		Auto-calculated rows will be replaced. Manually entered rows are kept.`,
		() => {
			frappe.show_alert({message: __("Loading items and calculating quantities…"), indicator: "blue"});
			frappe.call({
				method: "estimation.estimation.doctype.boq.boq.populate_boq_from_settings",
				args: {boq_name: frm.doc.name},
				callback(r) {
					if (r.message) {
						frappe.show_alert({message: __(r.message.message), indicator: "green"});
						frm.reload_doc();
					}
				},
			});
		}
	);
}

function _create_quotation(frm) {
	frappe.confirm(
		`Create an ERPNext Quotation for <b>${frm.doc.project_title}</b>?<br><br>
		Grand Total: <b>₹ ${format_number(frm.doc.grand_total, null, 0)}</b>`,
		() => {
			frappe.show_alert({message: __("Creating Quotation…"), indicator: "blue"});
			frappe.call({
				method: "estimation.estimation.doctype.boq.boq.create_quotation",
				args: {boq_name: frm.doc.name},
				callback(r) {
					if (r.message) {
						frm.reload_doc();
						frappe.show_alert({message: __("Quotation {0} created.", [r.message]), indicator: "green"});
						frappe.set_route("Form", "Quotation", r.message);
					}
				},
			});
		}
	);
}

// ─── Row calculation ────────────────────────────────────────────────────────

function _calc_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const mat = flt(row.qty) * flt(row.material_rate);
	const lab = flt(row.qty) * flt(row.labour_rate);
	frappe.model.set_value(cdt, cdn, "material_cost", flt(mat, 2));
	frappe.model.set_value(cdt, cdn, "labour_cost",   flt(lab, 2));
	frappe.model.set_value(cdt, cdn, "total_cost",    flt(mat + lab, 2));
	_calc_section_totals(frm);
}

// ─── Formula-based qty recalculation (client-side, no server round-trip) ───

function _build_formula_vars(frm) {
	const bua = flt(frm.doc.total_bua_sqft);
	return {
		BUA:           bua,
		GF_BUA:        flt(frm.doc.ground_floor_bua_sqft),
		FF_BUA:        flt(frm.doc.first_floor_bua_sqft),
		BUA_SQM:       flt(frm.doc.total_bua_sqm),
		FLOORS:        flt(frm.doc.no_of_floors) || 2,
		PLOT_AREA:     flt(frm.doc.plot_area_sqft),
		EXT_WALL:      flt(frm.doc.external_wall_mm) || 250,
		INT_WALL:      flt(frm.doc.internal_wall_mm) || 150,
		FLOOR_HEIGHT:  flt(frm.doc.floor_height_mm) || 3000,
		wastage_factor_: flt(frm.doc.wastage_percent) || 5,
	};
}

function _recalculate_formula_qtys(frm) {
	const vars = _build_formula_vars(frm);
	const varNames  = Object.keys(vars);
	const varValues = Object.values(vars);

	let changed = false;
	(frm.doc.boq_items || []).forEach(row => {
		if (!row.auto_calculated || !row.formula_basis) return;
		try {
			// Evaluate the Python-compatible arithmetic expression in JS
			// eslint-disable-next-line no-new-func
			const fn  = new Function(...varNames, `return (${row.formula_basis});`);
			const qty = flt(fn(...varValues), 3);
			if (qty !== flt(row.qty)) {
				frappe.model.set_value(row.doctype, row.name, "qty", qty);
				const mat = flt(qty) * flt(row.material_rate);
				const lab = flt(qty) * flt(row.labour_rate);
				frappe.model.set_value(row.doctype, row.name, "material_cost", flt(mat, 2));
				frappe.model.set_value(row.doctype, row.name, "labour_cost",   flt(lab, 2));
				frappe.model.set_value(row.doctype, row.name, "total_cost",    flt(mat + lab, 2));
				changed = true;
			}
		} catch (e) {
			console.warn(`BOQ formula error for "${row.description}":`, e);
		}
	});

	if (changed) {
		frm.refresh_field("boq_items");
		_calc_section_totals(frm);
	}
}

// ─── Section and grand total rollups ────────────────────────────────────────

function _calc_bua(frm) {
	const total = flt(frm.doc.ground_floor_bua_sqft) + flt(frm.doc.first_floor_bua_sqft);
	frm.set_value("total_bua_sqft", flt(total, 2));
	frm.set_value("total_bua_sqm",  flt(total * 0.0929, 2));
}

function _calc_section_totals(frm) {
	const sectionFieldMap = {
		"Civil Works":         "section_civil_total",
		"Flooring":            "section_flooring_total",
		"Bathroom Tiles":      "section_bathroom_total",
		"Doors & Windows":     "section_doors_total",
		"Painting":            "section_painting_total",
		"Electrical":          "section_electrical_total",
		"Plumbing & Sanitary": "section_plumbing_total",
	};

	const totals = {};
	Object.values(sectionFieldMap).forEach(f => { totals[f] = 0; });

	let totalMat = 0, totalLab = 0;
	(frm.doc.boq_items || []).forEach(row => {
		const f = sectionFieldMap[row.section];
		if (f) totals[f] += flt(row.total_cost);
		totalMat += flt(row.material_cost);
		totalLab += flt(row.labour_cost);
	});

	Object.entries(totals).forEach(([f, v]) => frm.set_value(f, flt(v, 2)));
	frm.set_value("total_material_cost", flt(totalMat, 2));
	frm.set_value("total_labour_cost",   flt(totalLab, 2));
	_calc_grand_total(frm);
}

function _calc_grand_total(frm) {
	const subA  = flt(frm.doc.total_material_cost) + flt(frm.doc.total_labour_cost);
	const contAmt = flt(subA * flt(frm.doc.contingency_percent) / 100, 2);
	const subB  = subA + contAmt;
	const ovhAmt = flt(subB * flt(frm.doc.overhead_percent) / 100, 2);

	frm.set_value("subtotal_a",         flt(subA, 2));
	frm.set_value("contingency_amount", contAmt);
	frm.set_value("subtotal_b",         flt(subB, 2));
	frm.set_value("overhead_amount",    ovhAmt);
	frm.set_value("grand_total",        flt(subB + ovhAmt, 2));
}
