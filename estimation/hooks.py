app_name = "estimation"
app_title = "Estimation"
app_publisher = "Cos"
app_description = "Estimation"
app_email = "cos@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "estimation",
# 		"logo": "/assets/estimation/logo.png",
# 		"title": "Estimation",
# 		"route": "/estimation",
# 		"has_permission": "estimation.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------
fixtures = [
    {"dt":"Custom Field",
        "filters":[
        ["module","in",(
            "Estimation"

        )]
    ]
    },
    {"dt":"Property Setter",
        "filters":[
        ["module","in",(
            "Estimation"

        )]
    ]
    },
]
# include js, css files in header of desk.html
# app_include_css = "/assets/estimation/css/estimation.css"
# app_include_js = "/assets/estimation/js/estimation.js"

# include js, css files in header of web template
# web_include_css = "/assets/estimation/css/estimation.css"
# web_include_js = "/assets/estimation/js/estimation.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "estimation/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "estimation/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "estimation.utils.jinja_methods",
# 	"filters": "estimation.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "estimation.install.before_install"
# after_install = "estimation.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "estimation.uninstall.before_uninstall"
# after_uninstall = "estimation.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "estimation.utils.before_app_install"
# after_app_install = "estimation.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "estimation.utils.before_app_uninstall"
# after_app_uninstall = "estimation.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "estimation.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "estimation.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }
# include js in doctype views
doctype_js = {
    "Lead":"public/js/lead.js",
}
# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"estimation.tasks.all"
# 	],
# 	"daily": [
# 		"estimation.tasks.daily"
# 	],
# 	"hourly": [
# 		"estimation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"estimation.tasks.weekly"
# 	],
# 	"monthly": [
# 		"estimation.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "estimation.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "estimation.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "estimation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "estimation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["estimation.utils.before_request"]
# after_request = ["estimation.utils.after_request"]

# Job Events
# ----------
# before_job = ["estimation.utils.before_job"]
# after_job = ["estimation.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"estimation.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

