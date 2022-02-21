from __future__ import unicode_literals

import frappe
from frappe import _, msgprint

def get_context(context):
  ## load some data and put it in context
  context.message = "Hello Portal!"
  context.pibico = ["pibiCo", "pibiDesk"]
  
  if frappe.session.user == "Administrator":
    frappe.msgprint("Here are you")
  return context