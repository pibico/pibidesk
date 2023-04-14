# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import _, msgprint, throw, enqueue
from frappe.utils import cstr, time_diff_in_seconds, get_files_path
from frappe.utils import nowdate, now_datetime
from frappe.core.doctype.sms_settings.sms_settings import send_sms

from pibidesk.pibidesk.doctype.telegram_settings.telegram_settings import send_telegram

import json, datetime

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
          _pos = []
          ## Include items except those tuples like position
          data_item = {}
          for d in data:
            if d['sensor_var'] == i and not ',' in d['value']:
              _data.append(d)
            if d['sensor_var'] == i and ',' in d['value']:
              _pos.append(d)
              
          ## Calculates for float values
          if len(_data) > 0:
            ## Select sensor_var and data_date from last recorded data
            var_uom = _data[0]['uom']
            last_recorded = _data[0]['data_date']
            ## Extract all values from dictionary
            seq = [float(x['value']) for x in _data]
            ## Prepares data_item values for childtable
            data_item['sensor_var'] = i
            data_item['uom'] = var_uom
            data_item['last_recorded'] = last_recorded
            data_item['value'] = seq[0]
            data_item['reading'] = len(seq)
            data_item['average'] = sum(seq)/len(seq)
            data_item['minimum'] = min(seq)
            data_item['maximum'] = max(seq)
          
          doLoc = False
          ## Calculates for
          if len(_pos) > 0:
            ## Select sensor_var and data_date from last recorded data
            var_uom = _pos[0]['uom']
            last_recorded = _pos[0]['data_date']
            ## Extract all values from dictionary
            loc = [(item['value']) for item in _pos]
            ## Prepares data_item values for childtable
            data_item['sensor_var'] = i
            data_item['uom'] = var_uom
            data_item['last_recorded'] = last_recorded
            data_item['value'] = str(_pos[0]['value'])
            doLoc = True
            data_item['reading'] = len(loc)
            data_item['average'] = 0
            data_item['minimum'] = 0
            data_item['maximum'] = 0         
          ## Check in thresholds if seq[0] is an alert (last recorded value)
          if len(device.alert_item) > 0:
            thresholds = device.alert_item
            threshold = [n for n in thresholds if n.sensor_var == i]
            if len(threshold) > 0:
              if not threshold[0].warning_disabled:
                ## Low Alert
                if threshold[0].active_low:
                  ## If value in low alert and not alerted before
                  if float(seq[0]) <= float(threshold[0].low_value) and not threshold[0].alert_low:
                    threshold[0].alert_low = True
                    threshold[0].save()
                    manage_alert(i, var_uom, seq[0], 'low', 'start', last_recorded, device) 
                  ## If value recovered and alerted before
                  if float(seq[0]) > float(threshold[0].low_value) and threshold[0].alert_low:
                    threshold[0].alert_low = False
                    threshold[0].save()
                    manage_alert(i, var_uom, seq[0], 'low', 'finish', last_recorded, device)   
                ## High Alert
                if threshold[0].active_high:
                  ## If value in high alert and not alerted before
                  if float(seq[0]) >= float(threshold[0].high_value) and not threshold[0].alert_high:
                    threshold[0].alert_high = True
                    threshold[0].save()
                    manage_alert(i, var_uom, seq[0], 'high', 'start', last_recorded, device) 
                  ## If value recovered and alerted before
                  if float(seq[0]) < float(threshold[0].high_value) and threshold[0].alert_high:
                    threshold[0].alert_high = False
                    threshold[0].save()
                    manage_alert(i, var_uom, seq[0], 'high', 'finish', last_recorded, device)
          ## Check if Data Item Childtable has values or not
          ## And Append or Update data_item to device
          if len(device.data_item) > 0:
            doCreate = True
            for row in device.data_item:
              ## Update table with calculations if data_item has float values
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
              #device.last_seen = now_datetime()
              #device.connected = True
              device.save()
              frappe.db.commit()
          else:
            stat = device.append("data_item", data_item)
            ## Save and Commit Modifications
            #device.last_seen = now_datetime()
            #device.connected = True
            device.save()
            frappe.db.commit()         
          
          ## Update route in map
          if doLoc:
            ## Update gps route on log
            location = {}
            location['type'] = "FeatureCollection"
            
            features = []
              
            feature = {}
            feature['type'] = "Feature"
            feature['properties'] = {}
          
            coords = []
          
            for row in device.data_item:
              if row.sensor_var == 'Position':
                latlng = row.value
                latlng = latlng.split(',')
                lat = float(latlng[0])
                lon = float(latlng[1])
                coords.append([lon, lat])
            
            feature['geometry'] = {"type": "LineString", "coordinates": coords}
            
            features.append(feature)
            location['features'] = features    
          
            self.move = json.dumps(location)
            self.reload()    
          ## End Code           
    else:
      frappe.msgprint(_("No data yet registered"))   

def manage_alert(sensor_var, uom, value, cmd, reason, datadate, doc):
  ## Get all channels for sending Alerts
  channels = frappe.db.sql("""
    SELECT *
    FROM `tabWarning Item`
    WHERE
    parent=%s AND docstatus<2 AND active
  """, doc.name, as_dict = True)
  alert_channel = []
  sms_recipients = []
  email_recipients = []
  telegram_recipients = []
  for c in channels:
    if c['channel_type'] not in alert_channel:
      alert_channel.append(c['channel_type'])      
    if c['channel_type'] == 'Email':
      if c['email'] not in email_recipients:
        email_recipients.append(c['email'])
    if c['channel_type'] == 'SMS':
      if c['mobile'] not in sms_recipients:
       sms_recipients.append(c['mobile'])
    if c['channel_type'] == 'Telegram':
      if c['mobile'] not in telegram_recipients:
        telegram_recipients.append(c['mobile'])
  ## Prepare Alerts for Device on each Sensor Var
  alert_log_item = frappe.get_list(
    doctype = "Alert Log Item",
    fields = ["*"],
    filters = {"docstatus": ("<", 2), "parent": ("=", frappe.utils.getdate().strftime("%y%m%d") + "_" + doc.name)},
    limit_page_length = 1
  )
  if len(alert_log_item) > 0:
    ## Check active alerts for each var 
    alert_log = frappe.get_doc("Alert Log", frappe.utils.getdate().strftime("%y%m%d") + "_" + doc.name)
    if len(alert_log.alert_log_item) > 0:
      doStart = True
      for row in alert_log.alert_log_item:
        if row.sensor_var == sensor_var:
          if not row.to_time and reason == 'finish':
            doStart = False
            row.to_time = datadate
            row.save()
      if doStart and reason == 'start':
        _alert_log_item = {}
        _alert_log_item['sensor_var'] = sensor_var
        _alert_log_item['uom'] = uom
        _alert_log_item['from_time'] = datadate
        if 'Email' in alert_channel:
          _alert_log_item['by_email'] = True
        if 'SMS' in alert_channel:
          _alert_log_item['by_sms'] = True
        if 'Telegram' in alert_channel:
          _alert_log_item['by_telegram'] = True  
        _alert_log_item['value'] = value
        _alert_log_item['alert_type'] = cmd
        log_item = alert_log.append("alert_log_item", _alert_log_item)
        alert_log.save()
        frappe.db.commit()    
  else:
    ## Create new empty Daily Alert Log
    alert_log = frappe.new_doc("Alert Log")
    alert_log.device = doc.name
    alert_log.date = datetime.datetime.now().strftime("%Y-%m-%d")
    ## Create new Alert Log and ChildTable in case new Alert
    _alert_log_item = {}
    _alert_log_item['sensor_var'] = sensor_var
    _alert_log_item['uom'] = uom
    _alert_log_item['from_time'] = datadate
    if 'Email' in alert_channel:
      _alert_log_item['by_email'] = True
    if 'SMS' in alert_channel:
      _alert_log_item['by_sms'] = True
    if 'Telegram' in alert_channel:
      _alert_log_item['by_telegram'] = True  
    _alert_log_item['value'] = value
    _alert_log_item['alert_type'] = cmd
    log_item = alert_log.append("alert_log_item", _alert_log_item)
    alert_log.save()
    frappe.db.commit()
  
  date_alert = datadate.strftime("%d/%m/%y %H:%M")
    
  ## Finally enqueu to send messages through channels
  if reason == 'start':
    if cmd == 'high':
      strAlert = "{} high by {}{} at {}.Please check".format(sensor_var, str(value), str(uom), date_alert)
      #strAlert = sensor_var + " high by " + str(value) + uom + ' at ' + date_alert + ". Please check"
    if cmd == 'low':
      strAlert = "{} low by {}{} at {}.Please check".format(sensor_var, str(value), str(uom), date_alert)
      strAlert = sensor_var + " low by " + str(value) + uom + ' at ' + date_alert + ". Please check"
  if reason == 'finish':
    if cmd == 'high':
      strAlert = sensor_var + " high finished by " + str(value) + uom + ' at ' + date_alert + ". Please check"
    if cmd == 'low':
      strAlert = sensor_var + " low finished by " + str(value) + uom + ' at ' + date_alert + ". Please check"  
  if len(email_recipients) > 0:
    subject = ""
    if reason == 'start':
      subject = "Alert Started by pibiDesk on " + doc.alias + " (" + doc.name + ")"
    if reason == 'finish':
      subject = "Alert Finished by pibiDesk on " + doc.alias + " (" + doc.name + ")"
    emlAlert = "[Email pibiDesk]: " + strAlert + " in " + doc.alias + " (" + doc.name + ")"
    #frappe.sendmail(recipients=email_recipients, subject=subject, message=cstr(emlAlert))
    email_args = {
		  'recipients': email_recipients,
		  'sender': None,
		  'subject': subject,
		  'message': cstr(emlAlert),
		  'header': [_('pibiDesk Alert Information'), 'blue'],
		  'delayed': False,
		  'retry':3
	  }
    enqueue(method=frappe.sendmail,queue='short',timeout=300,now=True,**email_args)  
    
  if len(sms_recipients) > 0:
    smsAlert = "[SMS pibiDesk]: " + strAlert + " in " + doc.alias + " (" + doc.name + ")"
    #send_sms(sms_recipients, cstr(smsAlert))
    sms_args = {
      'receiver_list': sms_recipients,
      'msg': cstr(smsAlert),
      'sender_name': '',
      'success_msg': True
    }
    enqueue(method=send_sms,queue='short',timeout=300,now=True,**sms_args)             
  if len(telegram_recipients) > 0:
    tgAlert = "[TGM pibiDesk]: " + strAlert + " in " + doc.alias + " (" + doc.name + ")"
    #send_telegram(telegram_recipients, cstr(tgAlert))
    tg_args = {
      'receiver_list': telegram_recipients,
      'msg': cstr(tgAlert),
      'sender_name': '',
      'success_msg': True
    }
    enqueue(method=send_telegram,queue='short',timeout=300,now=True,**tg_args) 