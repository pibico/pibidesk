function switch_on(name, alias) {
  let message = "";
  message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Control de Dispositivo</h3>";
  message+="<b>Activando Dispositivo </b>"+alias+" ("+name+")";
  message+="<br>Accion Irreversible. Confirma por favor.";
        
  var straction = '';              
  if (name == 'relay-01-rpb3b-pilot-container'){
    straction="rele_on"
  }
  
  frappe.confirm(
    message,
    function(){
      frappe.call({
        method: "pibidesk.pibidesk.custom.mqtt_command",
        type: "GET",
        args: {"host": "rpb3b-pilot-container", "action": straction},
        error: function(r) {
          frappe.show_alert('Error. Comprueba la ejecucion');  
        },
        async: true,
      });
      frappe.show_alert('Encendiendo ' + name);
      window.setTimeout(function(){location.reload()},6000);
    },
    function(){
      frappe.show_alert('Orden de encendido de ' + alias + ' NO enviada!');
    }
  );
};
function switch_off(name, alias) {
  let message = "";
  message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Control de Dispositivo</h3>";
  message+="<b>Desactivando Dispositivo </b>"+alias+" ("+name+")";
  message+="<br>Accion Irreversible. Confirma por favor."; 
  
  var straction = '';
  if (name == 'relay-01-rpb3b-pilot-container'){
    straction="rele_off"
  }
              
  frappe.confirm(
    message,
    function(){
      frappe.call({
        method: "pibidesk.pibidesk.custom.mqtt_command",
        type: "GET",
        args: {"host": "rpb3b-pilot-container", "action": straction},
        error: function(r) {
          frappe.show_alert('Error. Comprueba la ejecucion');  
        },
        async: true,
      });
      frappe.show_alert('Apagando ' + name);
      window.setTimeout(function(){location.reload()},6000)
    },
    function(){
      frappe.show_alert('Orden de apagado de ' + alias + ' NO enviada!');
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
    message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Control de Dispositivo</h3>";
    message+="<b>Desactivando Dispositivo </b>"+ event.srcElement.value + " (" + event.srcElement.id +")";
    message+="<br>Accion Irreversible. Confirma por favor."; 
    
    var straction = '';
    if (btn.id == 'relay-01-rpb3b-pilot-container'){
      straction="rele_off"
    }
              
    frappe.confirm(
      message,
      function(){
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          type: "GET",
          args: {"host": "rpb3b-001-pilot-container", "action": straction},
          error: function(r) {
            frappe.show_alert('Error. Comprueba la ejecucion');  
          },
          async: true,
        });
        frappe.show_alert('Apagando ' + btn.value);
        window.setTimeout(function(){location.reload()},12000)
      },
      function(){
        frappe.show_alert('Orden de apagado de ' + event.srcElement.value + ' NO enviada!');
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
    message+= "<h3><img src='/assets/pibidesk/images/favicon.svg' /> Control de Dispositivo</h3>";
    message+="<b>Activando Dispositivo </b>"+ event.srcElement.value + " (" + event.srcElement.id +")";
    message+="<br>Accion Irreversible. Confirma por favor."; 
    
    var straction = '';
    if (btn.id == 'relay-01-rpb3b-pilot-container'){
      straction="extractor_on"
    }
              
    frappe.confirm(
      message,
      function(){
        frappe.call({
          method: "pibidesk.pibidesk.custom.mqtt_command",
          type: "GET",
          args: {"host": "rpb3b-pilot-container", "action": straction},
          error: function(r) {
            frappe.show_alert('Error. Comprueba la ejecucion');  
          },
          async: true,
        });
        frappe.show_alert('Encendiendo ' + btn.value);
        window.setTimeout(function(){location.reload()},12000)
      },
      function(){
        frappe.show_alert('Orden de encendido de ' + event.srcElement.value + ' NO enviada!');
        if (btn.checked == true) {
          btn.checked = false;
        } else {
          btn.checked = true;
        }
      }
    );
  }
});