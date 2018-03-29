function downloadImage(){
    var a = document.createElement('a');
    // toDataURL defaults to png, so we need to request a jpeg, then convert for file download.
    a.href = c.toDataURL("image/png");
    a.download = 'somefilename.png';
    //a.click();

    // create a mouse event
    var event = new MouseEvent('click');

    // dispatching it will open a save as dialog in FF
    a.dispatchEvent(event);
}

var c = document.getElementById("canvasDownload");

$("#downloadsvg").click(function(){
    //check if affix top or not 
    sidebarWidth = document.getElementById("sidebar").offsetWidth
    sidebarHeight = document.getElementById("sidebar").offsetHeight

    processSelectorHeight = document.getElementById("processSelector").offsetHeight

    svgsWidth = document.getElementById("heatmap").offsetWidth
    svgsHeight = document.getElementById("heatmap").offsetHeight

    //check the width and height of the canvas element

    canvasWidth = sidebarWidth + svgsWidth +20
    canvasHeight = sidebarHeight > processSelectorHeight+svgsHeight+20 ? sidebarHeight+10 : processSelectorHeight+svgsHeight

    //set the width and height accordingly
    c.width = canvasWidth
    c.height = canvasHeight

    var ctx = c.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, c.width, c.height);

    html2canvas(document.querySelector("#sidebar"),{scale:1}).then(sidebarImage => {                    
        ctx.drawImage(sidebarImage,0,0);
    });

    html2canvas(document.querySelector("#processSelector"),{scale:1}).then(processSelector => {
        
        ctx.drawImage(processSelector,sidebarWidth+20,0);

        //draw the svgs
        svgAsPngUri(document.getElementById("clhmsvg"), {scale: 1, backgroundColor: "white", canvg: window.canvg}, function(uri) {
            base_image1 = new Image();
            base_image1.src = uri;
            base_image1.onload = function(){
                ctx.drawImage(base_image1, sidebarWidth+20, processSelectorHeight+10);
                downloadImage();
            }
        });
    });
})