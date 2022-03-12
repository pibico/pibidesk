# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import _, msgprint, throw
from frappe.utils import cstr, time_diff_in_seconds, get_files_path
from frappe.core.doctype.sms_settings.sms_settings import send_sms

from pibidesk.pibidesk.doctype.telegram_settings.telegram_settings import send_telegram
from pibidesk.pibidesk.doctype.mqtt_settings.mqtt_settings import send_mqtt

class Device(Document):
  pass


def get_timeline_data(doctype, name):
  '''Return timeline for messages'''
  return dict(frappe.db.sql('''select unix_timestamp(creation), count(*) from `tabAlert Log` where device=%s and creation > date_sub(curdate(), interval 1 year) and docstatus < 2 group by date(creation)''', name))