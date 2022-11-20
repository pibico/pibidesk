function camara() {
  var d = new frappe.ui.Dialog({
    'fields': [
      {'fieldname': 'ht', 'fieldtype': 'HTML'}
    ],
    primary_action_label: 'Salir',
    primary_action: function(){
      d.hide();
    }
  });
  d.fields_dict.ht.$wrapper.html(
   '<div class="container-fluid"><iframe src="https://valduvieco.pibico.es:8443" width="100%" height="390px"/></div>'
  );
  d.show();
};

function switch_on(name, alias) {
  let message = "";
  message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Device Control</h3>";
  message+="<b>Switch On Device </b>"+alias+" ("+name+")";
  message+="<br>Irreversible Action. Please Confirm.";
        
  var straction = '';              
  
  frappe.confirm(
    message,
    function(){
      frappe.call({
        method: "pibidesk.pibidesk.custom.mqtt_command",
        type: "GET",
        args: {"host": "rpb3b-nmci", "action": straction},
        error: function(r) {
          frappe.show_alert('Error. Check Execution');  
        },
        async: true,
      });
      frappe.show_alert('Switching On ' + name);
      window.setTimeout(function(){location.reload()},12000);
    },
    function(){
      frappe.show_alert('Lighting Command not sent to ' + alias);
    }
  );
};
function switch_off(name, alias) {
  let message = "";
  message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Device Control</h3>";
  message+="<b>Switching Off Device </b>"+alias+" ("+name+")";
  message+="<br>Irreversible Action. Please Confirm."; 
  
  var straction = '';
              
  frappe.confirm(
    message,
    function(){
      frappe.call({
        method: "pibidesk.pibidesk.custom.mqtt_command",
        type: "GET",
        args: {"host": "rpb3b-nmci", "action": straction},
        error: function(r) {
          frappe.show_alert('Error. Check Execution');  
        },
        async: true,
      });
      frappe.show_alert('Switching Off ' + name);
      window.setTimeout(function(){location.reload()},12000)
    },
    function(){
      frappe.show_alert('Switching Off Command not sent to ' + alias);
    }
  );
};

function _datainfo(name, alias) {
  let message="";
  message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Datos de Dispositivo</h3>";
  message+= "<b>"+alias+" ("+name+")</b>";
  message+= "<ul>";
  {% for item in data_items %}
    {% for val in item %}
      if('{{val.parent}}' == name) {
        message+= "<hr>";
        message+= "<li><b> {{ val.sensor_var }} </b> {{ val.value }}{{ val.uom }}</li>";
        message+= "<li><b>lecturas</b> {{ val.reading }}</li>";
        message+= "<li><b>minimo</b> {{ val.minimum }}{{ val.uom }}</li>";
        message+= "<li><b>maximo</b> {{ val.maximum }}{{ val.uom }}</li>";
        message+= "<li><b>promedio</b> {{ '%.2f'|format(val.average) }}{{ val.uom }}</li>";
        message+= "<li><b>ultimo registro</b> {{ val.last_recorded }}</li>";
      }
    {% endfor %}
  {% endfor %}
  message+= "</ul>";
        
  frappe.msgprint(message);
};

function datainfo(name, alias) {
  let message="";
  message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Datos de Dispositivo</h3>";
  message+= "<b>"+alias+" ("+name+")</b>";
  message+= "<p></p>";
  message+= "<table class='table table-md table-responsive table-striped'>";
  message+= "<thead class='thead-dark'>";
  message+= "<tr>";
  message+= "<th>var</th>";
  message+= "<th>val</th>";
  message+= "<th>pts</th>";
  message+= "<th>min</th>";
  message+= "<th>max</th>";
  message+= "<th>media</th>";
  message+= "<th>ultimo</th>";
  message+= "</tr></thead>";
  message+= "<tbody>";
  {% for item in data_items %}
    {% for val in item %}
      if('{{val.parent}}' == name) {
        message+= "<tr>";
        message+= "<td><b>{{ val.sensor_var }}</b></td>"
        message+= "<td><b>{{ val.value }}{{ val.uom }}</td>";
        message+= "<td><b>{{ val.reading }}</b></td>";
        message+= "<td><b>{{ val.minimum }}{{ val.uom }}</b></td>";
        message+= "<td><b>{{ val.maximum }}{{ val.uom }}</b></td>";
        message+= "<td><b>{{ '%.2f'|format(val.average) }}{{ val.uom }}</b></td>";
        message+= "<td><b>{{ val.last_recorded }}</b></td>";
        message+= "</tr>";
      }
    {% endfor %}
  {% endfor %}
  message+= "</tbody></table>";
        
  frappe.msgprint(message);
};

$('.toggle-switch').change(function(){
  if(!event.srcElement.checked) {
    var btn = event.srcElement
    let message = "";
    message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Device Control</h3>";
    message+="<b>Switching Off </b>"+ event.srcElement.value + " (" + event.srcElement.id +")";
    message+="<br>Irreversible Action. Please Confirm."; 
    
    var straction = '';
              
    frappe.confirm(
      message,
      function(){
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          type: "GET",
          args: {"host": "rpb3b-nmci", "action": straction},
          error: function(r) {
            frappe.show_alert('Error. Check the execution');  
          },
          async: true,
        });
        frappe.show_alert('Switching Off ' + btn.value);
        window.setTimeout(function(){location.reload()},12000)
      },
      function(){
        frappe.show_alert('Switch off not sent to ' + event.srcElement.value);
        if (btn.checked == true) {
          btn.checked = false;
        } else {
          btn.checked = true;
        } 
      }
    );
  } else {
    var btn = event.srcElement
    let message = "";
    message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Device Control</h3>";
    message+="<b>Switching On </b>"+ event.srcElement.value + " (" + event.srcElement.id +")";
    message+="<br>Irreversible Action. Please Confirm."; 
    
    var straction = '';
              
    frappe.confirm(
      message,
      function(){
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          type: "GET",
          args: {"host": "rpb3b-nmci", "action": straction},
          error: function(r) {
            frappe.show_alert('Error. Check the execution');  
          },
          async: true,
        });
        frappe.show_alert('Switching On ' + btn.value);
        window.setTimeout(function(){location.reload()},12000)
      },
      function(){
        frappe.show_alert('Switch On command not sent to ' + event.srcElement.value);
        if (btn.checked == true) {
          btn.checked = false;
        } else {
          btn.checked = true;
        }
      }
    );
  }
});