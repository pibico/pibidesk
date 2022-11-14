# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _

class DataSession(WebsiteGenerator):
  def get_context(self, context):
    ## Retrieve every log in session
    device_logs = frappe.get_all("Device Log",
      fields=["*"],
      filters=[["data_session", "=", self.name], ["docstatus", "<", 2]],
      order_by="creation desc"
    )
    context.logs = device_logs
    ## Retrieve last recorded value for devices
    devices = []
    result = {}
    coords = {}
    ## Get all devices in logs
    for log in device_logs:
      if log.device not in devices:
        devices.append(log.device)  
    ## get all gps in logs
    for device in devices:
      if 'gps' in device:
        locals()[f"coord_{device}"] = []
        for log in reversed(device_logs):
          if log['device'] == device:
            device_log = frappe.get_doc("Device Log", {'device': device})
            for row in device_log.log_item:
              if row.sensor_var == 'Position':
                latlng = row.value.split(',')
                lat = float(latlng[0])
                lon = float(latlng[1])
                coord = [lon, lat]
                locals()[f"coord_{device}"].append(coord)
      
        coords[device] = locals()[f"coord_{device}"]        
    
    context.coords = coords      
    
    for device in devices:
      dev = frappe.get_doc("Device", device)
      if len(dev.data_item) > 0:
        sensor_vars = []
        for d in dev.data_item:
          if d.sensor_var not in sensor_vars:
            sensor_vars.append(d.sensor_var)
        for i in sensor_vars:
          for row in dev.data_item:
            if row.sensor_var == i:
              locals()[f"{device}{i}"] = row.value
            
        for i in sensor_vars:
          result[device + '_' + i] = locals()[f"{device}{i}"]
    
    context.values = result                  