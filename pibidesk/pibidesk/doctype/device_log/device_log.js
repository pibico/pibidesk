// Copyright (c) 2022, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Device Log', {
	refresh: function(frm) {
    create_chart(frm);
    //sleep(1500).then(function() {
      // Do something
      //create_pic(frm);
    //});
    frm.add_custom_button("Chart To Picture", function() {
      // code to be executed after button is click
      create_pic(frm);
    });
	}
});
function create_chart(frm) {
  frappe.call({
    method: "pibidesk.pibidesk.custom.get_chart",
    args: {
      'doc': frm.doc.name
    },
    async: false,
  	callback: function(r) {
      var obj = r.message;
      var keys = Object.keys(obj);
      var res = {};
      for (let i = 0; i < keys.length; i++) {
        var key = keys[i];
        var prop = obj[key];
        res[i] = prop;
  	  }
      var series = keys.length/4;
    
      // Main Data
      // order is var,uom,lbl,read 0,1,2,3
      const main_data = {
        labels: res[2],
        datasets: [
          { 
            name: res[0],
            type: 'line',
            values: res[3]
          },
          {
            name: res[4],
            type: 'line',
            values: res[7]
          },
          {
            name: res[8],
            type: 'line',
            values: res[11]
          }
        ],
        tooltipOptions: {
          formatTooltipX: d => (d + '').toUpperCase(),
          formatTooltipY: d => d + ' pts',
        }
      };
      const main_chart = new frappe.Chart(
        "#main_chart", {
          // or a DOM element,
          // new Chart() in case of ES6 module with above usage
          title: res[0] + " [" + res[1] + "] " + res[4] + " [" + res[5] + "] " + res[8] + " [" + res[9] + "]",
          data: main_data,
          type: 'axis-mixed', // or 'bar', 'line', 'scatter', 'pie', 'percentage'
          height: 300,
          colors: ['#ff2233', '#224433', '#4682b4'],
          axisOptions: {
            xAxisMode: 'tick', // default: 'span'
            xIsSeries: true // default: false
          },
          lineOptions: {
            spline: 0,
            hideDots: 1
          }
      });
    // end callback
    }
  });  
}
function create_pic(frm){
  SVGToImage({
    // 1. Provide the SVG DOM element
    svg: document.querySelector("#main_chart svg"),
    // 2. Provide the format of the output image
    mimetype: "image/png",
    // 3. Provide the dimensions of the image if you want a specific size.
    //  - if they remain in auto, the width and height attribute of the svg will be used
    //  - You can provide a single dimension and the other one will be automatically calculated
    // width: "auto",
    // height: "auto",
    width: "auto",
    // 4. Specify the quality of the image
    quality: 1,
    // 5. Define the format of the output (base64 or blob)
    outputFormat: "base64"
  }).then(function(outputData){
    // If using base64 (outputs a DataURL)
    //  data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfQAAAH0...
    // Or with Blob (Blob)
    //  Blob {size: 14353, type: "image/png"}
    //console.log(outputData);
    frm.set_value('pic', outputData);
    refresh_field('pic');
  }).catch(function(err){
    // Log any error
    console.log(err);
  }); 
};
function sleep(ms) {
  return(new Promise(function(resolve, reject) {
    setTimeout(function() { resolve(); }, ms);
  }));
};
/**
 * Simple function that converts a plain SVG string or SVG DOM Node into an image with custom dimensions.
 * 
 * @param {Object} settings The configuration object to override the default settings.
 * @see https://ourcodeworld.com/articles/read/1456/how-to-convert-a-plain-svg-string-or-svg-node-to-an-image-png-or-jpeg-in-the-browser-with-javascript
 * @returns {Promise}
 */
function SVGToImage(settings){
  let _settings = {
    svg: null,
    // Usually all SVG have transparency, so PNG is the way to go by default
    mimetype: "image/png",
    quality: 0.92,
    width: "auto",
    height: "auto",
    outputFormat: "base64"
  };

  // Override default settings
  for (let key in settings) { _settings[key] = settings[key]; }

  return new Promise(function(resolve, reject){
    let svgNode;

    // Create SVG Node if a plain string has been provided
    if(typeof(_settings.svg) == "string"){
      // Create a non-visible node to render the SVG string
      let SVGContainer = document.createElement("div");
      SVGContainer.style.display = "none";
      SVGContainer.innerHTML = _settings.svg;
      svgNode = SVGContainer.firstElementChild;
    }else{
      svgNode = _settings.svg;
    }

    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d'); 

    let svgXml = new XMLSerializer().serializeToString(svgNode);
    let svgBase64 = "data:image/svg+xml;base64," + btoa(svgXml);

    const image = new Image();

    image.onload = function(){
      let finalWidth, finalHeight;

      // Calculate width if set to auto and the height is specified (to preserve aspect ratio)
      if(_settings.width === "auto" && _settings.height !== "auto"){
        finalWidth = (this.width / this.height) * _settings.height;
        // Use image original width
      }else if(_settings.width === "auto"){
        finalWidth = this.naturalWidth;
        // Use custom width
      }else{
        finalWidth = _settings.width;
      }

      // Calculate height if set to auto and the width is specified (to preserve aspect ratio)
      if(_settings.height === "auto" && _settings.width !== "auto"){
        finalHeight = (this.height / this.width) * _settings.width;
        // Use image original height
      }else if(_settings.height === "auto"){
        finalHeight = this.naturalHeight;
        // Use custom height
      }else{
        finalHeight = _settings.height;
      }

      // Define the canvas intrinsic size
      canvas.width = finalWidth;
      canvas.height = finalHeight;

      // Render image in the canvas
      context.drawImage(this, 0, 0, finalWidth, finalHeight);

      if(_settings.outputFormat == "blob"){
        // Fullfil and Return the Blob image
        canvas.toBlob(function(blob){
        resolve(blob);
        }, _settings.mimetype, _settings.quality);
      }else{
        // Fullfil and Return the Base64 image
        resolve(canvas.toDataURL(_settings.mimetype, _settings.quality));
      }
    };

    // Load the SVG in Base64 to the image
    image.src = svgBase64;
  });
}