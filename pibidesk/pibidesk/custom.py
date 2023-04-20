# -*- coding: utf-8 -*-
# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.utils import nowdate, now_datetime, cstr, time_diff_in_seconds, get_files_path
from frappe.utils.background_jobs import enqueue
from frappe.utils.password import get_decrypted_password

from pibidesk.pibidesk.doctype.mqtt_settings.mqtt_settings import send_mqtt
from pibidesk.pibidesk.doctype.device_log.device_log import manage_alert

import json, datetime, requests, os, sys
from datetime import timedelta
#import urllib.request as urllib2
import paho.mqtt.client as mqtt

from influxdb import InfluxDBClient

@frappe.whitelist()
def mqtt_command(host, action):
  topic = []
  topic.append(host + "/command")
  send_mqtt(topic, cstr(action))

@frappe.whitelist()
def boiler():
  server = 'pidev.net-freaks.com'
  port = 1883
  #user = 'user'
  #secret = 'secret'
  #do_ssl = False
  # connect to MQTT Broker to Publish Message
  pid = os.getpid()
  client_id = '{}:{}'.format('client', str(pid))
  try:
    backend = mqtt.Client(client_id=client_id, clean_session=True)
    #backend.username_pw_set(user, password=secret)
    backend.connect(server, port)

    payload = cstr('boiler')
    mqtt_topic = 'picaldera/mqttdevices'
    backend.publish(mqtt_topic, payload)
    backend.disconnect()
  except:
    frappe.msgprint(_("Error in MQTT Broker sending to " + str(mqtt_topic)))
    pass

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
      hostname.append(device.hostname + "/command")
      lastseen = device.last_seen
      now = datetime.datetime.now()
      pos = device.device_shortcut.find("-")
      cmd = "take_" + device.device_shortcut[:pos]
      strcmd = "start_" + device.device_shortcut[:pos]
      strboot = "__boot__"
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
      #elif gap_minutes < time_minutes <= gap_minutes * 5/4:
      #  doAlert = True
      #  send_mqtt(hostname, cstr(cmd))
      #elif time_minutes <= gap_minutes * 3/2:
      #  doAlert = True
      #  send_mqtt(hostname, cstr(strcmd))
      #elif time_minutes >= 2 * gap_minutes:   
      #  doAlert = True
      #  send_mqtt(hostname, cstr(strboot))    
      
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

@frappe.whitelist()
def read_mqtt_log():
  ## Get all devices in active and recording sessions that are not disabled
  device = frappe.db.sql("""
      SELECT
        device as name
      FROM `tabSession Item`
      WHERE
        parent IN
        (
         SELECT name 
         FROM `tabData Session`
         WHERE docstatus < 2 AND is_active AND recording
        )
      INTERSECT
        SELECT name
        FROM tabDevice
        WHERE docstatus < 2 AND NOT disabled 
      """, as_dict = True)
  devices = set()
  sensor_type = set()
  deltas = set()
  for dev in device:
    dev_type = dev['name'].split('-')[0]
    if dev_type not in sensor_type:
      sensor_type.add(dev_type)
    if dev['name'] not in devices:
      devices.add(dev['name'])
      sensor_vars = frappe.db.sql("""
          SELECT LOWER(sensor_var) as sensor_var
          FROM `tabVar Item`
          WHERE parent = %s
          """, (dev_type), as_dict = True)
      for var in sensor_vars:
        delta = ".".join([ dev['name'], var['sensor_var'] ])
        if not delta in deltas:
          deltas.add(delta)
  
  influx = frappe.get_doc('InfluxDB Settings', 'InfluxDB Settings')
  influx_host = influx.influxdb_host
  influx_port = influx.port
  influx_user = influx.user
  influx_key = get_decrypted_password('InfluxDB Settings', 'InfluxDB Settings', 'secret', False)
  current_date = datetime.datetime.now().strftime("%Y-%m-%d")
  influx_db = current_date #influx.database
  ## connect to influxdb
  influx_client = InfluxDBClient(host=influx_host, port=influx_port, username=influx_user, password=influx_key)
  influx_client.switch_database(influx_db)
  
  ## query for all measurements in database
  existing_measurements = influx_client.query('SHOW MEASUREMENTS')
  for measurement_name in existing_measurements:
    for meas in measurement_name:
      if (meas['name']) in deltas:
        ## Calculate start and end times for query
        end_time = datetime.datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)
        ## Build and execute the query
        # for all values
        #query = 'SELECT * FROM "' + meas['name'] + '" WHERE time >= \'' + start_time.isoformat() + 'Z\' AND time <= \'' + end_time.isoformat() + 'Z\''
        # for mean of values
        query = 'SELECT MEAN("value") FROM "' + meas['name'] + '" WHERE time >= \'' + start_time.isoformat() + 'Z\' AND time <= \'' + end_time.isoformat() + 'Z\''
        result = influx_client.query(query)
        # Process the result
        for values in result:
          if values:
            #print(meas['name'], values[0]['mean'], start_time)
            sdate = datetime.datetime.now().strftime("%y%m%d")
            sdelta = meas['name'].split(".")
            device_log = "".join([sdate, '_', sdelta[0], '%'])
            #get last log for variable and device and date in device_log
            last = frappe.db.sql("""
                SELECT
                  *
                FROM `tabLog Item`
                WHERE
                  parent LIKE %s AND docstatus < 2 AND sensor_var = %s
                ORDER BY data_date DESC
                LIMIT 1
              """, (device_log, sdelta[1]), as_dict = True)
            if last:
              # 
              if sdelta[1].capitalize() == 'Position':
                value = '0,0'
              else:
                value = round(values[0]['mean'],1)
              log = frappe.get_doc('Device Log', last[0]['parent'])
              if sdelta[1].capitalize() == 'Position':
                location = {}
                location['type'] = "FeatureCollection"
                
                features = []
                
                feature = {}
                feature['type'] = "Feature"
                feature['properties'] = {}
                
                coords = []
                for row in log.log_item:
                  if row.sensor_var == 'Position':
                    latlng = row.value.split(',')
                    lat = latlng[0]
                    lon = latlng[1]
                    coords.append([ lon, lat ])
                
                    feature['geometry'] = {"type": "LineString", "coordinates": coords}
                
                    features.append(feature)
                    location['features'] = features
                
                    log.move = str(json.dumps(location))
                    
              log_item = {
                "sensor_var": sdelta[1].capitalize(),
                "value": value,
                "data_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              }
              log.append("log_item", log_item)
              log.save()
              frappe.db.commit()
              #print(f"Updating {log.name} with {log_item}")
              logger.info(f"Updating {log.name} with {log_item}")

            else:
              # new device_log
              log = frappe.db.sql("""
                  SELECT
                    name
                  FROM `tabDevice Log`
                  WHERE
                    device=%s AND docstatus < 2 AND date=%s
                  LIMIT 1   
                """, (sdelta[0], sdate), as_dict = True)
              if sdelta[1] == 'position':
                value = '0,0'
              else:
                value = round(values[0]['mean'],1)
              
              log_item = {
                "sensor_var": sdelta[1].capitalize(),
                "value": value,
                "data_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              }  
              if log:
                doc = frappe.get_doc("Device Log", log[0]['name'])
              
                doc.append("log_item", log_item)
                doc.save()
                frappe.db.commit()
                #print(f"Inserting {doc.name} with {log_item}")
                logger.info(f"Inserting {doc.name} with {log_item}")
              else:
                session = frappe.db.sql("""
                  SELECT
                    parent
                  FROM `tabSession Item`
                  WHERE
                    device=%s AND docstatus < 2
                  LIMIT 1   
                """, (sdelta[0]), as_dict = True)
              
                doc = frappe.get_doc({
                  "doctype": 'Device Log',
                  "date": datetime.datetime.now().strftime(DATETIME_FORMAT),
                  "data_session": session[0]['parent'],
                  "device": sdelta[0]
                })
                doc.append("log_item", log_item)
                  
                doc.insert()
                frappe.db.commit()
                #print(f"Inserting: {doc}")      
                logger.info(f"Inserting: {doc}")

def sync_now():
  enqueue('pibidesk.pibidesk.custom.read_mqtt_log', timeout=30000, queue="long")

import paho.mqtt.client as mqtt
logger = frappe.logger("mqtt_msg", allow_site=True, file_count=3)

def on_message(client, userdata, message):
  """
    {
      "hostname": "iot-atvirtual",
      "deviceID": "sim868-gps",
      "location": "GPS Buoy",
      "type": "gps",
      "model": "WVSIM868",
      "class": "sensor",
      "reading": {
        "lat": "43.537595",
        "lon": "-5.659457",
        "alt": 21.081,
        "sats": 8,
        "time": "20:43:22UTC",
        "cog": "338",
        "sog": "0",
        "decmag": "-0.499",
        "record": "true",
        "data_date": "2023-03-21 20:44:04.581347"
      }
    }
  """
  #message = '{"hostname": "bc572900d0be", "deviceid": "b827eb904c41", "type": "th", "model": "K6P", "class": "sensor", "reading": {"temperature": 26.29, "humidity": 36.3, "record": "true", "data_date": "2023-03-21 22:16:04.581347"}}'
  strvalue = str(message.payload.decode("utf-8"))
  #logger.info(f"Processing: {strvalue}")
  if message.retain == True:
    logger.warning(f"Retained message: {strvalue} on topic {str(message.topic)}")  
  # Converts message to dict
  strjson = json.loads(strvalue)
  ## Defines alias for device
  device = '-'.join([strjson['type'], strjson['hostname']])
  device_log = '_'.join([datetime.datetime.now().strftime("%y%m%d"), device + '-%']) 
  logger.info("{} --- {} ---".format(datetime.datetime.now().strftime("%H:%M:%S"),device))
  try:
    ## Update connection on device
    device_doc = frappe.get_doc("Device", device)
    if device_doc:
      if not device_doc.disabled:
        device_doc.connected = True
        device_doc.last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device_doc.save()
  
        ddate = datetime.datetime.now().strftime("%Y-%m-%d")
        
        ## Get variable names from device type
        svars = []
        sensor_var = frappe.get_doc("Sensor Type", strjson['type'])
        if sensor_var:
          for var in sensor_var.var_item:
            if not var.sensor_var in svars:
              svars.append(var.sensor_var)
        ## Check if message has record key     
        if len(svars) > 0 and 'record' in strjson['reading']:
          ## Check if record mode is on
          if strjson['reading']['record'] == 'true':
            ## Get data session from device
            course = frappe.db.sql("""
            SELECT
              parent
            FROM `tabSession Item`
            WHERE
              device=%s AND docstatus<2
            """, device, as_dict = True)
            session = frappe.get_doc('Data Session', course[0]['parent'])
            ## If session is active and allow recording then records
            if session.is_active and session.recording:
              ## Get last device log item for each var
              for var in svars:
                last = frappe.db.sql("""
                SELECT
                  *
                FROM `tabLog Item`
                WHERE
                  parent LIKE %s AND docstatus < 2 AND sensor_var=%s
                ORDER BY data_date DESC
                LIMIT 1
                """, (device_log, var), as_dict = True)
                if last:
                  if var == 'Position':
                    value = ','.join([ strjson['reading']['lat'], strjson['reading']['lon'] ])
                  else:
                    value = strjson['reading'][var.lower()]
                
                  if str(last[0]['value']) != str(value):
                    log = frappe.get_doc('Device Log', last[0]['parent'])
                    if var == 'Position':
                      location = {}
                      location['type'] = "FeatureCollection"
                
                      features = []
                
                      feature = {}
                      feature['type'] = "Feature"
                      feature['properties'] = {}
                
                      coords = []
                      for row in log.log_item:
                        if row.sensor_var == 'Position':
                          latlng = row.value.split(',')
                          lat = latlng[0]
                          lon = latlng[1]
                          coords.append([ lon, lat ])
                
                      feature['geometry'] = {"type": "LineString", "coordinates": coords}
                
                      features.append(feature)
                      location['features'] = features
                
                      log.move = str(json.dumps(location))
                    
                    log_item = {
                      "sensor_var": var,
                      "value": value,
                      "data_date": strjson['reading']['data_date']
                    }
                    log.append("log_item", log_item)
                    log.save()
                    frappe.db.commit()
                    #print(f"Updating {log.name} with {log_item}")
                    logger.info(f"Updating {log.name} with {log_item}")
                else:
                  log = frappe.db.sql("""
                  SELECT
                    name
                  FROM `tabDevice Log`
                  WHERE
                    device=%s AND docstatus < 2 AND date=%s
                  LIMIT 1   
                  """, (device, ddate), as_dict = True)
                  if var == 'Position':
                    value = ','.join([ strjson['reading']['lat'], strjson['reading']['lon'] ])
                    print(value)
                  else:
                    value = strjson['reading'][var.lower()]
              
                  log_item = {
                    "sensor_var": var,
                    "value": value,
                    "data_date": strjson['reading']['data_date']
                  }
                  if log:
                    doc = frappe.get_doc("Device Log", log[0]['name'])
              
                    doc.append("log_item", log_item)
                    doc.save()
                    frappe.db.commit()
                    #print(f"Inserting {doc.name} with {log_item}")
                    logger.info(f"Inserting {doc.name} with {log_item}")
                  else:
                    
                    doc = frappe.get_doc({
                      "doctype": 'Device Log',
                      "date": datetime.datetime.now().strftime(DATETIME_FORMAT),
                      "data_session": session.name,
                      "device": device
                    })
                    doc.append("log_item", log_item)
                  
                    doc.insert()
                    frappe.db.commit()
                    #print(f"Inserting: {doc}")      
                    logger.info(f"Inserting: {doc}")
      else:
        logger.warning("Device disabled {}".format(strvalue))
        #print("Device disabled {}".format(strvalue))
    else:
      logger.warning("Error processing (not found device) {}".format(strvalue))
      #print("Error processing (not found device) {}".format(strvalue))
  
  except KeyboardInterrupt:
    print("[INFO] Keyboard Escape")
    sys.exit()  
  except Exception as error:
    logger.warning("Error on_message {}".format(error))
    logger.info("Error processing {}".format(strvalue))
    #print("Exception [ {} ] in message {}".format(error, strvalue))
    pass
  finally:
    message = None
  
def start_reading():
  broker = frappe.get_doc('MQTT Settings', 'MQTT Settings')
  client = mqtt.Client()
  client.username_pw_set(broker.user, get_decrypted_password('MQTT Settings', 'MQTT Settings', 'secret', False))
  client.connect(broker.broker_gateway, broker.port, 60)
  topics = [('home/pibico/#', 0)]
  client.subscribe(topics)
  client.on_message = on_message
  client.loop_forever()

@frappe.whitelist()
def read_mqtt_messages():
  start_reading()