from __future__ import unicode_literals

import frappe
from frappe import _, msgprint, throw

import json, requests

no_cache = True

def get_context(context):
  if frappe.session.user == 'Guest':
    context._login_required = True
    frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)
    
  ## load some data and put it in context
  
  device_list = frappe.get_list(
    doctype = "Device",
    fields = ["*"],
    filters = [['assigned_to', '=', 'pibidesk@gmail.com']]
  )
  context.device_list = device_list
 
  data_items = []
  for sensor in device_list:
    data_item = frappe.get_list(
      doctype = "Data Item",
      fields = ["*"],
      filters = [['parent', '=', sensor.name]]
    )  
    data_items.append(data_item)
  context.data_items = data_items
  
  alert_items= []
  for sensor in device_list:
    alert_low = frappe.get_list(
      doctype = "Alert Item",
      fields = ["*"],
      filters = [['parent', '=', sensor.name],['alert_low','=',1]]
    )  
    alert_items.append(alert_low)
    alert_high = frappe.get_list(
      doctype = "Alert Item",
      fields = ["*"],
      filters = [['parent', '=', sensor.name],['alert_high','=',1]]
    )  
    alert_items.append(alert_high)
  context.alert_items = alert_items
  
  ## Get Location and Weather for Client Logged In
  weather_set = frappe.get_doc("Weather Settings", "Weather Settings")
  client = frappe.get_doc("Client", "pibidesk@gmail.com")
  ## json.loads(customer[0].location).features[0].geometry.coordinates
  strloc = json.loads(client.location)
  if weather_set:
    jsonloc = json.dumps(strloc['features'][0], indent = 4)
    location = json.loads(jsonloc)['geometry']['coordinates']
    lat = str(location[1])
    lon = str(location[0])
    url = weather_set.weather_url
    apikey = weather_set.api_key
    base_url = url + "?lat=" + lat + "&lon=" + lon + "&units=metric&appid=" + apikey + "&exclude=minutely,hourly&mode=json"
    req = requests.get(base_url)
    if not req.content:
      context.weather = {}
    else:  
      # We only want the data associated with the "response" key
      context.weather = json.loads(req.content.decode('utf-8')) 
  else:
    context.weather = {}
      
  return context