# Copyright (c) 2026, Cos and contributors
# For license information, please see license.txt

import json
import os

import frappe


def _load_template():
	template_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)), "data", "scope_of_work_template.json"
	)
	with open(template_path, "r") as f:
		return json.load(f)


@frappe.whitelist()
def create_scope_of_work_tasks(project):
	"""
	Creates 15 parent Tasks (categories) and 84 child Tasks (scope items)
	under the given Project. Skips categories that already have a task to
	keep this idempotent — safe to call more than once.
	"""
	frappe.has_permission("Task", "create", throw=True)

	project_doc = frappe.get_doc("Project", project)
	template = _load_template()

	created_parents = 0
	created_children = 0

	for category in template:
		category_name = category["category"]

		# Check if a parent task for this category already exists under the project
		existing_parent = frappe.db.get_value(
			"Task",
			{"project": project, "subject": category_name, "parent_task": ("is", "not set")},
			"name",
		)

		if existing_parent:
			parent_task_name = existing_parent
		else:
			parent_task = frappe.get_doc({
				"doctype": "Task",
				"project": project,
				"subject": category_name,
				"is_group": 1,
				"status": "Open",
				"priority": "Medium",
				"description": f"Category {category['order']} of 15 — {category_name}",
			})
			parent_task.insert(ignore_permissions=True)
			parent_task_name = parent_task.name
			created_parents += 1

		# Create child tasks (scope items) under this parent
		for item in category["items"]:
			existing_child = frappe.db.get_value(
				"Task",
				{
					"project": project,
					"subject": item["name"],
					"parent_task": parent_task_name,
				},
				"name",
			)
			if existing_child:
				continue

			child_task = frappe.get_doc({
				"doctype": "Task",
				"project": project,
				"subject": item["name"],
				"parent_task": parent_task_name,
				"status": "Open",
				"priority": "Medium",
			})
			child_task.insert(ignore_permissions=True)
			created_children += 1

	frappe.db.commit()

	return {
		"message": f"Scope of Work loaded: {created_parents} categories and {created_children} tasks created.",
		"parents_created": created_parents,
		"children_created": created_children,
	}
