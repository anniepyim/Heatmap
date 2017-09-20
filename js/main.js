var Heatmap = {};
var parserHeatmap = require('./parserHeatmap.js');
var mpld3 = require('./mpld3.v0.3.js');

Heatmap.init = function(json,jsonGroupCount,sessionid,parameter,svg,pyScript,onError){ 
    
    if (jQuery.isEmptyObject(json)) onError(new Error('Please add samples!'));
    if ((jsonGroupCount >= 1 && jsonGroupCount < 4) || (json.length >= 1 && json.length < 4)) onError(new Error('Please add at least 4 samples!')); 
    
    var init = "all";
    parserHeatmap.parse(drawHeatmap,onError,init,parameter,sessionid,svg,pyScript);
    
};

function drawHeatmap(url){
    
    mpld3.register_plugin("htmltooltip", HtmlTooltipPlugin);
    HtmlTooltipPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    HtmlTooltipPlugin.prototype.constructor = HtmlTooltipPlugin;
    HtmlTooltipPlugin.prototype.requiredProps = ["id"];
    HtmlTooltipPlugin.prototype.defaultProps = {labels:null,
                                                hoffset:0,
                                                voffset:10};
    function HtmlTooltipPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    }

    HtmlTooltipPlugin.prototype.draw = function(){
       var obj = mpld3.get_element(this.props.id);
       var labels = JSON.parse(this.props.labels);
       var tooltip = d3.select("body").append("div")
                    .attr("class", "mpld3-tooltip")
                    .style("position", "absolute")
                    .style("z-index", "10")
                    .style("opacity", 0);

       obj.elements()
           .on("mouseover", function(d, i){


                            tooltip.transition()
                                .duration(200)
                                .style("opacity", 0.9);
                            tooltip.html("Sample: " + labels[i].sample + "<br/>" + "Gene: " + labels[i].gene + "<br/>" + "Log2 FC: " + d3.format(".3f")(labels[i].value));



                })
           .on("mousemove", function(d, i){
                  tooltip
                    .style("top", d3.event.pageY + this.props.voffset + "px")
                    .style("left",d3.event.pageX + this.props.hoffset + "px");
                }.bind(this))
           .on("mouseout",  function(d, i){
                            tooltip.transition()
                                .duration(500)
                                .style("opacity", 0);
                })
            .on("mousedown",  function(d, i){
                
                var selected = $("#groups option:selected").val();
                if (selected == "") {
                    selected = 'selected-sample';
                }
               
                var newvalue = labels[i].sample;
           
                if ($("#"+selected+" option[value='"+newvalue+"']").length === 0){    
                    var option = document.createElement("option");
                    option.text = labels[i].sample;
                    option.value = labels[i].sample;
                    var select = document.getElementById(selected);
                    select.appendChild(option);
                }
               
            });
    };

    d3.json(url,function(data){
        mpld3.draw_figure("heatmap", data);
    });

}

//Export as App so it could be App.init could be called
module.exports = Heatmap;