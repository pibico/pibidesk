from __future__ import unicode_literals
from frappe import _

def get_data():
        return {
                'heatmap': True,
                'heatmap_message': _('This is based on Alerts received from this Device'),
                'fieldname': 'device',
                'transactions': [
                        {
                                'label': _('Device Readings'),
                                'items': ['Device Log']
                        },
                        {
                                'label': _('Alerts Received'),
                                'items': ['Alert Log']
                        }
                ]
        }