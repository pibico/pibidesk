from __future__ import unicode_literals
from frappe import _

def get_data():
  return [
    {
      "label": _("pibiDesk"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Device",
          "description": _("MIoT Devices"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Device Log",
          "description": _("Device Log"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Device Alert",
          "description": _("Device Alert"),
          "onboard": 1,
        },
        {
					"type": "report",
					"is_query_report": True,
					"name": "Device Log",
					"doctype": "Device Log",
					"onboard": 1,
					"dependencies": ["Device"],
				},
      ]
    },
    {
      "label": _("Settings"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Sensor Type",
          "description": _("Sensor Type"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Sensor Var",
          "description": _("Sensor Variable"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Area",
          "description": _("Area"),
          "onboard": 1,
        }
      ]
    },
    {
      "label": _("Channels"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "MQTT Settings",
          "description": _("MQTT Settings"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Telegram Settings",
          "description": _("Telegram Settings"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "SMS Settings",
          "description": _("SMS Settings"),
          "onboard": 1,
        }
      ]
    }
  ]