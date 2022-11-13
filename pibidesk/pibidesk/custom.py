# -*- coding: utf-8 -*-
# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.utils import nowdate, now_datetime, cstr, time_diff_in_seconds, get_files_path

from pibidesk.pibidesk.doctype.mqtt_settings.mqtt_settings import send_mqtt
from pibidesk.pibidesk.doctype.device_log.device_log import manage_alert

import json, datetime, requests
#import urllib.request as urllib2

@frappe.whitelist()
def mqtt_command(host, action):
  topic = []
  topic.append(host + "/pibico/cmd")
  send_mqtt(topic, cstr(action))

@frappe.whitelist()
def call_api(url, action):
  try:
    urlapi = str(url) + "/" + str(action)
    #json_relay = urllib2.urlopen(urlapi)
    response = requests.get(urlapi)
    #relay = json.load(json_relay)
    relay = response.text
  except Exception as error:
    relay = {'data': {'error': error}}

  return relay

def check_status():
  devices = frappe.get_list(
    doctype = "Device",
    fields = ['*'],
    filters = [['docstatus', '<', 2], ['disabled', '=', 0]]
  )
  if len(devices) > 0:
    for device in devices:
      hostname = []
      hostname.append(device.hostname + "/pibico/cmd")
      lastseen = device.last_seen
      now = datetime.datetime.now()
      pos = device.device_shortcut.find("-")
      cmd = "take_" + device.device_shortcut[:pos]
      strcmd = "start_" + device.device_shortcut[:pos]
      strboot = "boot"
      ## Alert for lastseen taken from threshold items
      threshold = frappe.db.sql("""
        SELECT
          idx, sensor_var, uom, high_value, active_high, alert_high
        FROM `tabAlert Item`
        WHERE
         parent=%s AND docstatus<2 AND sensor_var='last_seen'
      """, device.name, as_dict = True)
      if len(threshold) > 0:
        gap_minutes = threshold[0]['high_value']
      else:
        gap_minutes = 12 #by default 12 minutes
        
      if lastseen:
        time_minutes = (now - lastseen).total_seconds()/60
      else:
        time_minutes = gap_minutes + 1
      ## Alert in case time is greater than admisible gap      
      dev = frappe.get_doc("Device", device.name)
      doAlert = False
      ## manage_alert(sensor_var, uom, value, cmd, reason, datadate, doc)
      if time_minutes < gap_minutes:
        if len(threshold) > 0:
          if threshold[0]['alert_high']:
            for n in dev.alert_item:
              if n.sensor_var == 'last_seen':
                if n.alert_high:
                  n.alert_high = False
                  n.save() 
                  manage_alert(threshold[0]['sensor_var'], threshold[0]['uom'], time_minutes, 'high', 'finish', now.strftime("%Y-%m-%d %H:%M:%S"), dev)
      elif gap_minutes < time_minutes <= gap_minutes * 5/4:
        doAlert = True
        send_mqtt(hostname, cstr(cmd))
      elif time_minutes <= gap_minutes * 3/2:
        doAlert = True
        send_mqtt(hostname, cstr(strcmd))
      elif time_minutes >= 2 * gap_minutes:   
        doAlert = True
        send_mqtt(hostname, cstr(strboot))    
      
      if doAlert: 
        for n in dev.alert_item:
          if n.sensor_var == 'last_seen':
            dev.connected = False
            dev.save()
            n.alert_high = True
            n.save()
            if len(threshold) > 0: 
              manage_alert(threshold[0]['sensor_var'], threshold[0]['uom'], time_minutes, 'high', 'start', now.strftime("%Y-%m-%d %H:%M:%S"), dev)  
      
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

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CHART_FORMAT = "%H:%M"

@frappe.whitelist()
def get_chart(doc):
  if not 'new-' in doc:
    data = frappe.get_doc("Device Log", doc)
    #print("data = {}".format(frappe.as_json(data)))
    if len(data.log_item) > 0:
      sensor_vars = []
      for d in data.log_item:
        if d.sensor_var not in sensor_vars:
          sensor_vars.append(d.sensor_var)
      for i in sensor_vars:
        chart_data = []
        for d in data.log_item:
          if d.sensor_var == i:
            chart_data.append(d)
      
        locals()[f"var_{i}"] = i
        locals()[f"uom_{i}"] = chart_data[0].uom
        locals()[f"lbl_{i}"] = [n.data_date.strftime(CHART_FORMAT) for n in chart_data]
        locals()[f"read_{i}"] = [n.value for n in chart_data]
      
      result = {}
      for i in sensor_vars:
        result["var_"+ i] = locals()[f"var_{i}"]
        result["uom_" + i] = locals()[f"uom_{i}"]
        result["lbl_"+ i] = locals()[f"lbl_{i}"]
        result["read_" + i] = locals()[f"read_{i}"]
      
      return result