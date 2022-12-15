# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _
## if not installed pip3 install geopy 
## calculate distance https://en.wikipedia.org/wiki/Vincenty's_formulae
from geopy.distance import distance
import math,os
from datetime import datetime

class DataSession(WebsiteGenerator):
  def get_context(self, context):
    ## Retrieve every log in session
    device_logs = frappe.get_all("Device Log",
      fields=["*"],
      filters=[["data_session", "=", self.name], ["docstatus", "<", 2]],
      order_by="creation desc"
    )
    context.logs = device_logs
    
    ## Ais recording time
    ais = "/home/erpnext/erpnext-dev/apps/pibidesk/pibidesk/public/dist/leaflet/aisdata.js"
    now = datetime.now().timestamp()
    ais_ago = int((now - os.path.getmtime(ais))/60)
    context.ais_ago = ais_ago
    
    ## Retrieve last recorded value for devices
    devices = []
    result = {}
    coords = {}
    ## Get all devices in logs
    for log in device_logs:
      if log.device not in devices:
        devices.append(log.device)  
    context.devices = devices
    ## get all gps in logs
    for device in devices:
      if 'gps' in device:
        locals()[f"coord_{device}"] = []
        for log in reversed(device_logs):
          if log['device'] == device:
            device_log = frappe.get_doc("Device Log", {'device': device, 'data_session': self.name})
            for row in device_log.log_item:
              if row.sensor_var == 'Position':
                latlng = row.value.split(',')
                lat = float(latlng[0])
                lon = float(latlng[1])
                coord = [lon, lat]
                locals()[f"coord_{device}"].append(coord)
      
        coords[device] = locals()[f"coord_{device}"]        
    
    context.coords = coords
    
    ## calculate all distances
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
          if i == 'Position':
            location = locals()[f"{device}{i}"].split(',')
            lat = float(location[0])
            lon = float(location[1])
            result[device + '_lat'] = lat
            result[device + '_lon'] = lon  
    
    try:    
      result['rescue_bearing'] = rel_bearing(int(result['imu-iot-rescue_Heading']), float(result['gps-iot-rescue_lat']), float(result['gps-iot-rescue_lon']), float(result['gps-iot-dummy_lat']), float(result['gps-iot-dummy_lon']))
      result['life_bearing'] = rel_bearing(int(result['imu-iot-life_Heading']), float(result['gps-iot-life_lat']), float(result['gps-iot-life_lon']), float(result['gps-iot-dummy_lat']), float(result['gps-iot-dummy_lon']))
    except:
      pass  
        
    context.values = result
    
def rel_bearing(hdg1, lat1, lon1, lat2, lon2):
  dlat = (lat2 - lat1) * 60.
  lat_med = (lat1 + lat2) / 2.
  dlon = (lon2 - lon1) * 60.
  ap = dlon * math.cos(math.radians(lat_med))
  
  z = math.atan2(ap, dlat)*180./math.pi % 360
  
  diff = (z - hdg1) % 360
  if diff >= 180:
    diff -= 360
  
  return diff
                  