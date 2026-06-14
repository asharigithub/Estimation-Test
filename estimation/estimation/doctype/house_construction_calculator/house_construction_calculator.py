# Copyright (c) 2026, Cos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HouseConstructionCalculator(Document):
    def validate(self):
        material_cost_calculator = frappe.get_single("Material Quantity Calculator")
        if material_cost_calculator.structure_calculation:
            for i in self.cost_calculation_structural_materials:
                for j in material_cost_calculator.structure_calculation:
                    if j.structure == i.structural_materials:
                        if j.formula_basis:
                            formula_variables = {
                                "BUA": self.total_builtup_area or 0,
                                "wastage_factor_": self.wastage_factor_ or 0,
                            }

                            try:
                                base_qty = frappe.safe_eval(j.formula_basis, None, formula_variables)
                                i.base_qty = base_qty
                                i.total_cost = (i.base_qty or 0) * (i.cost_per_unit or 0)
                            except Exception as e:
                                frappe.throw(
                                    f"Error evaluating formula for {i.structural_materials}: {j.formula_basis}<br>Error: {str(e)}"
                                )

            # Sum up all row costs after the loop
            self.total_cost = sum(i.total_cost or 0 for i in self.cost_calculation_structural_materials)
				



