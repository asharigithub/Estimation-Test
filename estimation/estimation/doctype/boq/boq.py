# Copyright (c) 2026, Cos and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

# Maps BOQ section names to summary fields on the BOQ doctype
SECTION_FIELD_MAP = {
	"Civil Works": "section_civil_total",
	"Flooring": "section_flooring_total",
	"Bathroom Tiles": "section_bathroom_total",
	"Doors & Windows": "section_doors_total",
	"Painting": "section_painting_total",
	"Electrical": "section_electrical_total",
	"Plumbing & Sanitary": "section_plumbing_total",
}

# Stable item codes used in Quotation line items
BOQ_ITEM_CODES = {
	"Civil Works": "BOQ-CIVIL-WORKS",
	"Flooring": "BOQ-FLOORING",
	"Bathroom Tiles": "BOQ-BATHROOM-TILES",
	"Doors & Windows": "BOQ-DOORS-WINDOWS",
	"Painting": "BOQ-PAINTING",
	"Electrical": "BOQ-ELECTRICAL",
	"Plumbing & Sanitary": "BOQ-PLUMBING-SANITARY",
	"Contingencies": "BOQ-CONTINGENCIES",
	"Contractor Overhead & Profit": "BOQ-OVERHEAD-PROFIT",
}


class BOQ(Document):
	def before_insert(self):
		if not self.prepared_by:
			self.prepared_by = frappe.session.user
		if not self.date:
			self.date = frappe.utils.today()

	def validate(self):
		self._calc_bua()
		self._recalc_formula_quantities()
		self._calc_row_costs()
		self._calc_section_totals()
		self._calc_grand_total()

	def _calc_bua(self):
		self.total_bua_sqft = flt(self.ground_floor_bua_sqft) + flt(self.first_floor_bua_sqft)
		self.total_bua_sqm = flt(self.total_bua_sqft * 0.0929, 2)

	def _recalc_formula_quantities(self):
		"""Re-evaluate qty for rows that were loaded from MQC settings (auto_calculated = 1)."""
		formula_vars = _build_formula_vars(self)
		for row in self.boq_items:
			if row.auto_calculated and row.formula_basis:
				try:
					qty = flt(frappe.safe_eval(row.formula_basis, None, formula_vars), 3)
					row.qty = qty
				except Exception:
					pass  # keep existing qty if formula errors

	def _calc_row_costs(self):
		for row in self.boq_items:
			row.material_cost = flt(flt(row.qty) * flt(row.material_rate), 2)
			row.labour_cost = flt(flt(row.qty) * flt(row.labour_rate), 2)
			row.total_cost = flt(row.material_cost + row.labour_cost, 2)

	def _calc_section_totals(self):
		totals = {field: 0.0 for field in SECTION_FIELD_MAP.values()}
		total_material = 0.0
		total_labour = 0.0

		for row in self.boq_items:
			field = SECTION_FIELD_MAP.get(row.section)
			if field:
				totals[field] += flt(row.total_cost)
			total_material += flt(row.material_cost)
			total_labour += flt(row.labour_cost)

		for field, value in totals.items():
			self.set(field, flt(value, 2))

		self.total_material_cost = flt(total_material, 2)
		self.total_labour_cost = flt(total_labour, 2)

	def _calc_grand_total(self):
		subtotal_a = flt(self.total_material_cost) + flt(self.total_labour_cost)
		self.subtotal_a = flt(subtotal_a, 2)
		self.contingency_amount = flt(subtotal_a * flt(self.contingency_percent) / 100, 2)
		subtotal_b = subtotal_a + flt(self.contingency_amount)
		self.subtotal_b = flt(subtotal_b, 2)
		self.overhead_amount = flt(subtotal_b * flt(self.overhead_percent) / 100, 2)
		self.grand_total = flt(subtotal_b + flt(self.overhead_amount), 2)


def _build_formula_vars(boq):
	"""Return the variable dict used when evaluating BOQ quantity formulas."""
	return {
		"BUA": flt(boq.total_bua_sqft),
		"GF_BUA": flt(boq.ground_floor_bua_sqft),
		"FF_BUA": flt(boq.first_floor_bua_sqft),
		"BUA_SQM": flt(boq.total_bua_sqm),
		"FLOORS": flt(boq.no_of_floors) or 2,
		"PLOT_AREA": flt(boq.plot_area_sqft),
		"EXT_WALL": flt(boq.external_wall_mm) or 250,
		"INT_WALL": flt(boq.internal_wall_mm) or 150,
		"FLOOR_HEIGHT": flt(boq.floor_height_mm) or 3000,
		"wastage_factor_": flt(boq.wastage_percent) or 5,
	}


@frappe.whitelist()
def populate_boq_from_settings(boq_name):
	"""
	Load BOQ line items from Material Quantity Calculator → BOQ Quantity Formulas.
	Existing auto_calculated rows are replaced; manually-entered rows are kept.
	"""
	boq = frappe.get_doc("BOQ", boq_name)
	mqc = frappe.get_single("Material Quantity Calculator")

	if not mqc.get("boq_quantity_formulas"):
		frappe.throw(
			_("No BOQ Quantity Formulas are configured in Material Quantity Calculator. "
			  "Please set them up first.")
		)

	# Remove existing auto-calculated rows, keep manual ones
	boq.boq_items = [row for row in boq.boq_items if not row.auto_calculated]

	formula_vars = _build_formula_vars(boq)

	for idx, frow in enumerate(mqc.boq_quantity_formulas, 1):
		qty = 0.0
		if frow.formula_basis:
			try:
				qty = flt(frappe.safe_eval(frow.formula_basis, None, formula_vars), 3)
			except Exception as e:
				frappe.log_error(
					f"BOQ formula error for '{frow.description}': {e}",
					"BOQ Qty Formula"
				)

		boq.append("boq_items", {
			"section": frow.section,
			"sl_no": idx,
			"description": frow.description,
			"unit": frow.unit,
			"qty": qty,
			"material_rate": flt(frow.default_material_rate),
			"labour_rate": flt(frow.default_labour_rate),
			"formula_basis": frow.formula_basis or "",
			"auto_calculated": 1,
		})

	boq.save(ignore_permissions=True)
	return {
		"message": f"{len(mqc.boq_quantity_formulas)} items loaded and quantities calculated.",
		"count": len(mqc.boq_quantity_formulas),
	}


@frappe.whitelist()
def create_quotation(boq_name):
	"""Create an ERPNext Quotation from a saved BOQ and link it back."""
	frappe.has_permission("Quotation", "create", throw=True)

	boq = frappe.get_doc("BOQ", boq_name)

	if boq.linked_quotation:
		frappe.throw(
			_(f"A Quotation {boq.linked_quotation} is already linked to this BOQ. "
			  "Open the existing quotation or unlink it first."),
		)

	_ensure_boq_items_exist()
	_ensure_contact_schema()

	# Determine party
	if boq.customer:
		quotation_to = "Customer"
		party_name = boq.customer
	elif boq.lead:
		quotation_to = "Lead"
		party_name = boq.lead
	else:
		frappe.throw(_("Please set a Customer or Lead on the BOQ before creating a Quotation."))

	quotation = frappe.new_doc("Quotation")
	quotation.quotation_to = quotation_to
	quotation.party_name = party_name
	quotation.title = boq.project_title
	quotation.transaction_date = frappe.utils.today()
	quotation.order_type = "Sales"

	# One line per section with a non-zero total
	section_totals = {
		"Civil Works": boq.section_civil_total,
		"Flooring": boq.section_flooring_total,
		"Bathroom Tiles": boq.section_bathroom_total,
		"Doors & Windows": boq.section_doors_total,
		"Painting": boq.section_painting_total,
		"Electrical": boq.section_electrical_total,
		"Plumbing & Sanitary": boq.section_plumbing_total,
	}

	for section, total in section_totals.items():
		if not total:
			continue
		quotation.append("items", {
			"item_code": BOQ_ITEM_CODES[section],
			"item_name": section,
			"description": section,
			"qty": 1,
			"uom": "Nos",
			"rate": total,
		})

	if boq.contingency_amount:
		quotation.append("items", {
			"item_code": BOQ_ITEM_CODES["Contingencies"],
			"item_name": f"Contingencies @ {boq.contingency_percent}%",
			"description": f"Contingencies @ {boq.contingency_percent}%",
			"qty": 1,
			"uom": "Nos",
			"rate": boq.contingency_amount,
		})

	if boq.overhead_amount:
		quotation.append("items", {
			"item_code": BOQ_ITEM_CODES["Contractor Overhead & Profit"],
			"item_name": f"Contractor Overhead & Profit @ {boq.overhead_percent}%",
			"description": f"Contractor Overhead & Profit @ {boq.overhead_percent}%",
			"qty": 1,
			"uom": "Nos",
			"rate": boq.overhead_amount,
		})

	quotation.terms = (
		f"BOQ Reference: {boq_name}\n"
		f"Project: {boq.project_title}\n"
		f"Location: {boq.location or ''}\n\n"
		"This is a Preliminary BOQ & Cost Estimate based on Architectural Drawings. "
		"Final quantities shall be verified after Structural Drawings & site verification.\n\n"
		"EXCLUDED ITEMS (client scope):\n"
		"E1 - Water & electricity connection charges\n"
		"E2 - Government fees and approvals\n"
		"E3 - Interior furniture and movable fixtures\n"
		"E4 - External utility connections beyond site boundary\n"
		"E5 - Any items not explicitly listed in the BOQ"
	)

	quotation.insert(ignore_permissions=True)

	# Link quotation back on BOQ
	frappe.db.set_value("BOQ", boq_name, "linked_quotation", quotation.name)
	frappe.db.set_value("BOQ", boq_name, "status", "Sent to Client")

	return quotation.name


def _ensure_boq_items_exist():
	"""Create placeholder Service items for BOQ sections if they don't exist."""
	item_group = _get_service_item_group()

	for section, item_code in BOQ_ITEM_CODES.items():
		if frappe.db.exists("Item", item_code):
			continue
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": item_code,
			"item_name": section,
			"item_group": item_group,
			"is_stock_item": 0,
			"include_item_in_manufacturing": 0,
			"description": f"Construction service — {section}",
		})
		item.insert(ignore_permissions=True)


def _get_service_item_group():
	for group in ("Services", "Service", "All Item Groups"):
		if frappe.db.exists("Item Group", group):
			return group
	ig = frappe.get_doc({"doctype": "Item Group", "item_group_name": "Services", "parent_item_group": "All Item Groups"})
	ig.insert(ignore_permissions=True)
	return "Services"


def _ensure_contact_schema():
	"""
	ERPNext added is_billing_contact to Contact in a later patch.
	If the column is missing, Quotation.validate() crashes when it looks
	up the default contact.  DDL requires ending the active transaction
	first (MySQL would do an implicit commit anyway).
	"""
	if not frappe.db.has_column("Contact", "is_billing_contact"):
		frappe.db.commit()  # end active transaction before DDL
		frappe.db.sql(
			"ALTER TABLE `tabContact` ADD COLUMN `is_billing_contact` INT(1) NOT NULL DEFAULT 0"
		)
