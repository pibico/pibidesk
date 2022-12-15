// Copyright (c) 2022, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Data Session', {
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
