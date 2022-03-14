// Copyright (c) 2022, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Device', {
	refresh(frm) {
    if (frappe.session.user == 'Administrator') {
      frm.add_custom_button("ReStart Sensor", function() {
        var shortcut = frm.doc.name;
        var pos = shortcut.search("-");
        var action = "start_" + shortcut.substring(0,pos);
        // code to be executed after button is click
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          args: {
            host: frm.doc.hostname,
            action: action
          }
        });
      }, "MQTT Commands");
      frm.add_custom_button("UpDate LastSeen", function() {
        var shortcut = frm.doc.name;
        var pos = shortcut.search("-");
        var action = "take_" + shortcut.substring(0,pos);
        // code to be executed after button is click
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          args: {
            host: frm.doc.hostname,
            action: action
          }
        });
      }, "MQTT Commands");
      // Last Command
      frm.add_custom_button("Restart VNC", function() {
        // code to be executed after button is click
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          args: {
            host: frm.doc.hostname,
            action: "vnc"
          }
        });
      }, "MQTT Commands");
      frm.add_custom_button("ReBoot Server", function() {
        // code to be executed after button is click
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          args: {
            host: frm.doc.hostname,
            action: "boot"
          }
        });
      }, "MQTT Commands");
    }
  }
});