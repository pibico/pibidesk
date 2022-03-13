# -*- coding: utf-8 -*-
# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.utils import nowdate, now_datetime

import json, datetime

def alerts_reschedule():
  ## Get list of all Alerts in last day to check if there are still open
  still_open = frappe.get_list(
    doctype = "Alert Log",
    fields = ["name"],
    filters = {"docstatus": ("<", 2), "name": ("like", frappe.utils.add_days(frappe.utils.getdate(), -1).strftime("%y%m%d") + "_%")}
  )
  for log in still_open:
    alert = frappe.get_doc("Alert Log", log.name)
    if len(alert.alert_log_item) > 0:
      for row in alert.alert_log_item:
        if not row.to_time:
          ## Creating new Alert Log Start Warning
          alert_log = frappe.new_doc("Alert Log")
          alert_log.device = alert.device
          alert_log.date = frappe.utils.getdate().strftime("%Y-%m-%d")
          ## Write Data for new Alert
          alert_log_item = {
            "sensor_var": row.sensor_var,
            "from_time": row.from_time,
            "to_time": None,
            "value": row.value,
            "uom": row.uom,
            "alert_type": row.alert_type,
            "by_sms": row.by_sms,
            "by_email": row.by_email,
            "by_telegram": row.by_telegram
          }
          ## Adds log to array  
          alert_log.append("alert_log_item", alert_log_item)
          alert_log.save()
          frappe.db.commit()  