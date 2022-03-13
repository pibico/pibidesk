# Copyright (c) 2022, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Device(Document):
  pass
          
def get_timeline_data(doctype, name):
  '''Return timeline for messages'''
  return dict(frappe.db.sql('''select unix_timestamp(creation), count(*) from `tabAlert Log` where device=%s and creation > date_sub(curdate(), interval 1 year) and docstatus < 2 group by date(creation)''', name))