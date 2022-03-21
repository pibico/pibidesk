from __future__ import unicode_literals

import frappe
import qrcode
from PIL import Image
import base64
from io import BytesIO
from datetime import tzinfo, timedelta, datetime

def timestamp_to_date(value, format='%H:%M'):
  if value:
    return datetime.fromtimestamp(int(value)).strftime(format)
def ts_to_date(value, format='a% %d/%m/%y %H:%M'):
  if value:
    return datetime.fromtimestamp(int(value)).strftime(format)

def get_qrcode(input_str):
  qr = qrcode.make(input_str)
  temp = BytesIO()
  qr.save(temp, "PNG")
  temp.seek(0)
  b64 = base64.b64encode(temp.read())
  return "data:image/png;base64,{0}".format(b64.decode("utf-8"))

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def get_svg(svg):
  drawing = svg2rlg(svg)
  temp = BytesIO()
  renderPM.drawToFile(drawing, temp, fmt="PNG")
  temp.seek(0)
  b64 = base64.b64encode(temp.read())
  return "data:image/png;base64,{0}".format(b64.decode("utf-8"))