var mainframe = require('./views/mainframe.js');
mainframe = new mainframe();

function parserHeatmap(){}   
function parse(drawHeatmap,onError,init,parameter,sessionid,svg,pyScript){
   
if(init == "all"){
    
        //RUN python script that calls R script to do PCA analysis
        jQuery.ajax({
            url: pyScript[0], 
            data: parameter,
            type: "POST",   
            success: function (data) {
                
                var el = document.getElementById(svg);
                while (el.hasChildNodes()) {el.removeChild(el.firstChild);}
                mainframe.setElement('#'+svg).renderHeatmap();
                
                var htmltext = "";
                $('#heatmapfolders').empty();
                $.each(data, function(i,process) {
                    htmltext = htmltext+'<option value=\"'+process+'\">'+process+'</option>';
                });

                $("#heatmapfolders").html(htmltext);
                $('#heatmapfolders').selectpicker('refresh');
                $('#heatmapfolders').find('[value="'+data[0]+'"]').prop('selected',true);
                $('#heatmapfolders').selectpicker('refresh');
                
                parse(drawHeatmap,onError,"folder",parameter,sessionid,svg,pyScript);
                
                //Update the PCA plot by calling the functions upon changing folders
                $('#heatmapfolders').on('change',function(){
                    parse(drawHeatmap,onError,"folder",parameter,sessionid,svg,pyScript);
                });
                
            },
            error: function(e){
                onError(e);
            }
        });
        
    }else{
        var process = $("#heatmapfolders option:selected").val();
        var parameter_HM = 'process=' + process + '&sessionid=' + sessionid
        
        var el = document.getElementById( "heatmap" );
        while (el.hasChildNodes()) {el.removeChild(el.firstChild);}
        var div = document.createElement('div');
        div.setAttribute("align", "center");
        div.innerHTML ='<img id="loading" src="./img/loading.gif">';
        el.appendChild(div);
        
        url = "./data/user_uploads/"+sessionid+"/heatmap/"+process+".json";
        
        jQuery.ajax({
            url:url,
            type:'HEAD',
            error: function()
            {
                jQuery.ajax({
                    url: pyScript[1], 
                    data: parameter_HM,
                    type: "POST",  
                    success: function (data) {

                        drawHeatmap(url);

                    },
                    error: function(e){
                        onError(e);
                    }});
            },
            success: function()
            {
                drawHeatmap(url);
            }
        });
        

        
    }


    
}

parserHeatmap.parse = parse;

module.exports = parserHeatmap;


