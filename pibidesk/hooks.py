from . import __version__ as app_version

app_name = "pibidesk"
app_title = "Pibidesk"
app_publisher = "PibiCo"
app_description = "MIoT Local"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "pibico.sl@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pibidesk/css/pibidesk.css"
# app_include_js = "/assets/pibidesk/js/pibidesk.js"

# include js, css files in header of web template
# web_include_css = "/assets/pibidesk/css/pibidesk.css"
# web_include_js = "/assets/pibidesk/js/pibidesk.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pibidesk/public/scss/website"

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

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
#role_home_page = {
#	"pibidesk": "greenhouse"
#}

brand_html = '<div><img width="27px" src="/assets/pibidesk/images/logo/logo-icon.png"> pibi<strong>Desk</strong></div>'

website_context = {
  "favicon": "/assets/pibidesk/images/favicon.ico",
  "splash_image": "/assets/pibidesk/images/logo/logo-horizontal.png"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pibidesk.install.before_install"
# after_install = "pibidesk.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pibidesk.uninstall.before_uninstall"
# after_uninstall = "pibidesk.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pibidesk.notifications.get_notification_config"

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

jenv = {
  "methods": [
    "get_qrcode:pibidesk.jinja_filters.get_qrcode",
    "get_svg:pibidesk.jinja_filters.get_svg",
    "timestamp_to_date:pibidesk.jinja_filters.timestamp_to_date",
    "ts_to_date:pibidesk.jinja_filters.ts_to_date"
  ]
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

#doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
#    "Device": {
#      "after_insert": "pibidesk.pibidesk.custom.update_alert"
#    }
#}

# Scheduled Tasks
# ---------------

scheduler_events = {
 	#"all": [
 	#	"pibidesk.pibidesk.custom.schedule_read_mqtt"
 	#],
# 	"daily": [
# 		"pibidesk.tasks.daily"
# 	],
# 	"hourly": [
# 		"pibidesk.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pibidesk.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pibidesk.tasks.monthly"
# 	]
 	"cron": {
    "0 0 * * *": [
			"pibidesk.pibidesk.custom.alerts_reschedule"
		],
    "*/1 * * * *": [
      "pibidesk.pibidesk.custom.check_status"
    ]
	}
}

#app_events = {
#  "after_bench_start": "pibidesk.pibidesk.custom.schedule_read_mqtt"
#}

# Testing
# -------

# before_tests = "pibidesk.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pibidesk.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pibidesk.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

fixtures = ['Role Profile', 'Role', 'Custom Field', 'Client Script', 'Property Setter', 'Translation']

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pibidesk.auth.validate"
# ]

default_mail_footer = """
    <div>
        Sent via <a href="https://iot-enidh.ddns.net" target="_blank">pibiCo</a>
    </div>
"""