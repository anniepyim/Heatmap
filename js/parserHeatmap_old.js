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
            dataType: "html",    
            success: function () {
                
                var el = document.getElementById(svg);
                while (el.hasChildNodes()) {el.removeChild(el.firstChild);}
                mainframe.setElement('#'+svg).renderHeatmap();
                $( "#loading_heatmap_process" ).css('display','');
                
                //call the function to drawHeatmap
                url = "./data/user_uploads/"+sessionid+"/heatmap/Apoptosis.json";
                drawHeatmap(url);
                
																//Retrieve files result from the python+R script runs and 
																var targeturl = './data/user_uploads/'+sessionid+'/heatmap/';
																var folderurl = '.'+targeturl;
																var htmltext = "",
																value = "",
																text = "";

																jQuery.ajax({
																				type: "POST",
																				url: "./php/getdirectory.php",
																				dataType: "json",
																				data: { folderurl : folderurl },
																		success: function(data){
                                        
																						$('#heatmapfolders').empty();
																						$.each(data, function(i,filename) {
																								value = targeturl+filename;
																								text = filename.split(".")[0];
																								htmltext = htmltext+'<option value=\"'+value+'\">'+text+'</option>';
																				});

																				$("#heatmapfolders").html(htmltext);
																				$('#heatmapfolders').selectpicker('refresh');
																				$('#heatmapfolders').find('[value="./data/user_uploads/'+sessionid+'/heatmap/Apoptosis.json"]').prop('selected',true);
																				$('#heatmapfolders').selectpicker('refresh');
																		},
																				error: function(e){
																								console.log(e);
																				}
																});
                
                jQuery.ajax({
                    url: pyScript[1], 
                    data: parameter,
                    type: "POST",
                    dataType: "html",    
                    success: function (result) {
                    
                        //Retrieve files result from the python+R script runs and 
                        var targeturl = './data/user_uploads/'+sessionid+'/heatmap/';
                        var folderurl = '.'+targeturl;
                        var htmltext = "",
                        value = "",
                        text = "";

                        jQuery.ajax({
                            type: "POST",
                            url: "./php/getdirectory.php",
                            dataType: "json",
                            data: { folderurl : folderurl },
                          success: function(data){
                              $('#heatmapfolders').empty();
                              $.each(data, function(i,filename) {
                                value = targeturl+filename;
                                text = filename.split(".")[0];
                                htmltext = htmltext+'<option value=\"'+value+'\">'+text+'</option>';

                            });

                            $("#heatmapfolders").html(htmltext);
                            $('#heatmapfolders').selectpicker('refresh');
                            $('#heatmapfolders').find('[value="./data/user_uploads/'+sessionid+'/heatmap/Apoptosis.json"]').prop('selected',true);
                            $('#heatmapfolders').selectpicker('refresh');
                            
                            $( "#loading_heatmap_process" ).css('display','none');
                              
                          },
                            error: function(e){
                                console.log(e);
                            }
                        });
                    },
                    error: function(e){
                        onError(e);
                    }});

                //Update the PCA plot by calling the functions upon changing folders
                $('#heatmapfolders').on('change',function(){
                    parse(drawHeatmap,onError,"folder");
                });
                
            },
            error: function(e){
                onError(e);
            }
        });
        
    }else{
        var url = $("#heatmapfolders option:selected").val();
        drawHeatmap(url); 
        $( "#loading_heatmap_process" ).css('display','none');
    }


    
}

parserHeatmap.parse = parse;

module.exports = parserHeatmap;


