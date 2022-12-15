// Copyright (c) 2022, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Data Session', {
	onload(frm) {
    // Fill Child Table with Devices on doctype first creation if any device exists
    if (frm.doc.__islocal) {
      frappe.db.get_list('Device', { filters: { disabled: ['=', 0] }, fields: ['name'], limit: 500 }).then(res => {
	      for(var i in res){
	        let devs = frm.add_child('session_item');
		    devs.device = res[i].name;
	      }  
		  frm.refresh_fields('session_item');
	   }); 
    }
  },    
  refresh(frm) {
    frm.add_custom_button("ReStart AIS", function() {
      var action = "ais";
      // code to be executed after button is click
      frappe.call({
        method: "pibidesk.pibidesk.custom.mqtt_command",
        args: {
          host: 'iot-enidh',
          action: action
        }
      });
    }, "MQTT Commands");
  }  
});
