# Copyright (c) 2026, Cos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HouseConstructionCalculator(Document):
    def validate(self):
        bua = (self.plot_lengthft) * (self.plot_widthft) * (self.builtup_area_per_floor_of_plot / 100) * (self.no_of_floors)
        self.total_builtup_area = bua

        material_cost_calculator = frappe.get_single("Material Quantity Calculator")

        if material_cost_calculator.structure_calculation:

            # Get existing rows as a dict {structural_materials: row}
            existing_rows = {i.structural_materials: i for i in self.cost_calculation_structural_materials}

            # Sync rows from Material Quantity Calculator
            for j in material_cost_calculator.structure_calculation:
                if j.structure not in existing_rows:
                    # Add missing rows automatically
                    self.append("cost_calculation_structural_materials", {
                        "structural_materials": j.structure,
                    })

            # Recalculate after sync
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
            self.total_cost_structural_materials = sum(i.total_cost or 0 for i in self.cost_calculation_structural_materials)
        if material_cost_calculator.finishing_calculation:

            # Get existing rows as a dict {structural_materials: row}
            existing_rows = {i.structural_materials: i for i in self.cost_calculation_finishing_materials}

            # Sync rows from Material Quantity Calculator
            for j in material_cost_calculator.finishing_calculation:
                if j.finishing not in existing_rows:
                    # Add missing rows automatically
                    self.append("cost_calculation_finishing_materials", {
                        "structural_materials": j.finishing,
                    })

            # Recalculate after sync
            for i in self.cost_calculation_finishing_materials:
                for j in material_cost_calculator.finishing_calculation:
                    if j.finishing == i.structural_materials:
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
            self.total_cost_finishing_materials = sum(i.total_cost or 0 for i in self.cost_calculation_finishing_materials)    
	

        if material_cost_calculator.waterproofing_calculation:

            # Get existing rows as a dict {structural_materials: row}
            existing_rows = {i.structural_materials: i for i in self.cost_calculation_waterproofing_materials}

            # Sync rows from Material Quantity Calculator
            for j in material_cost_calculator.waterproofing_calculation:
                if j.waterproofing not in existing_rows:
                    # Add missing rows automatically
                    self.append("cost_calculation_waterproofing_materials", {
                        "structural_materials": j.waterproofing,
                    })

            # Recalculate after sync
            for i in self.cost_calculation_waterproofing_materials:
                for j in material_cost_calculator.waterproofing_calculation:
                    if j.waterproofing == i.structural_materials:
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

            self.total_cost_waterproofing_materials = sum(i.total_cost or 0 for i in self.cost_calculation_waterproofing_materials)
            # Sum up all row costs after the loop
            self.total_cost = self.total_cost_waterproofing_materials + self.total_cost_structural_materials + self.total_cost_finishing_materials

