# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw
from frappe.utils import nowdate, now_datetime

import json

class DeviceLog(Document):
  def on_update(self):
    """ Get data from device's daily log """
    data = frappe.db.sql("""
      SELECT
        idx,sensor_var,uom,value,data_date from `tabLog Item`
      WHERE
        parent=%s and docstatus<2
      ORDER BY idx DESC
    """, self.name, as_dict = True)
    ## Calculate statistics for each recorded var
    if len(data) > 0:
      ## Locate Sensor Vars
      sensor_var = []
      for d in data:
        if d['sensor_var'] not in sensor_var:
          sensor_var.append(d['sensor_var'])
      ## Prepare Statistics for Device on each Sensor Var
      for i in sensor_var:
        ## Recover Data from Device
        device = frappe.get_doc("Device", self.device)
        if device and not device.disabled:
          ## Split dictionaries for selected variable
          _data = []
          for d in data:
            if d['sensor_var'] == i:
              _data.append(d)
          ## Select sensor_var and data_date from last recorded data
          var_uom = _data[0]['uom']
          last_recorded = _data[0]['data_date']
          ## Extract all values from dictionary
          seq = [float(x['value']) for x in _data]
          ## Prepares data_item values for childtable
          data_item = {}
          data_item['sensor_var'] = i
          data_item['uom'] = var_uom
          data_item['last_recorded'] = last_recorded
          data_item['value'] = seq[0]
          data_item['reading'] = len(seq)
          data_item['average'] = sum(seq)/len(seq)
          data_item['minimum'] = min(seq)
          data_item['maximum'] = max(seq)
          ## Check in thresholds if seq[0] is an alert (last recorded value)
          if len(device.alert_item) > 0:
            thresholds = device.alert_item
            threshold = [n for n in thresholds if n.sensor_var == i]
            if len(threshold) > 0:
              if not threshold[0].warning_disabled:
                ## Low Alert
                if threshold[0].active_low:
                  ## If value in low alert and not alerted before
                  if float(seq[0]) < threshold[0].low_value and not threshold[0].alert_low:
                    threshold[0].alert_low = True
                    threshold[0].save()
                  ## If value recovered and alerted before
                  if float(seq[0]) >= threshold[0].low_value and threshold[0].alert_low:
                    threshold[0].alert_low = False
                    threshold[0].save()  
                ## High Alert
                if threshold[0].active_high:
                  ## If value in high alert and not alerted before
                  if float(seq[0]) > threshold[0].high_value and not threshold[0].alert_high:
                    threshold[0].alert_high = True
                    threshold[0].save()
                  ## If value recovered and alerted before
                  if float(seq[0]) <= threshold[0].high_value and threshold[0].alert_high:
                    threshold[0].alert_high = False
                    threshold[0].save()
                    
                     
          ## Check if Data Item Childtable has values or not
          ## And Append or Update data_item to device
          if len(device.data_item) > 0:
            doCreate = True
            for row in device.data_item:
              if row.sensor_var == i:
                ## Update existing data in childtable
                doCreate = False
                row.last_recorded = data_item['last_recorded']
                row.value = data_item['value']
                row.reading = data_item['reading']
                row.average = data_item['average']
                row.minimum = data_item['minimum']
                row.maximum = data_item['maximum']
                row.save()
            if doCreate:
              ## Append non existing data to childtable 
              stat = device.append("data_item", data_item)
              device.save()
              frappe.db.commit()  
          else:
            stat = device.append("data_item", data_item)
            ## Save and Commit Modifications
            device.save()
            frappe.db.commit()
    else:
      frappe.msgprint(_("No data yet registered"))    