var Heatmap = {};
var parserHeatmap = require('./parserHeatmap.js');
var mpld3 = require('./mpld3.v0.3.js');
var tipTemplate = require('./views/templates').Heatmap_tooltip;

var clickEvent = {target: null, holdClick: false};

Heatmap.init = function(json,jsonGroupCount,sessionid,parameter,svg,pyScript,onError){ 
    
    if (jQuery.isEmptyObject(json)) onError(new Error('Please add samples!'));
    if ((jsonGroupCount >= 1 && jsonGroupCount < 4) || (json.length >= 1 && json.length < 4)) onError(new Error('Please add at least 4 samples!')); 
    
    var init = "all";
    parserHeatmap.parse(drawHeatmap,onError,init,parameter,sessionid,svg,pyScript);
    
};

function drawHeatmap(url){
    
    d3.select(".mpld3-tooltip").remove();
    
    mpld3.register_plugin("htmltooltip", HtmlTooltipPlugin);
    HtmlTooltipPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    HtmlTooltipPlugin.prototype.constructor = HtmlTooltipPlugin;
    //HtmlTooltipPlugin.prototype.requiredProps = ["id"];
    HtmlTooltipPlugin.prototype.defaultProps = {labels:null,
                                                hoffset:0,
                                                voffset:10};
    function HtmlTooltipPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    }

    HtmlTooltipPlugin.prototype.draw = function(){
       var obj = mpld3.get_element(this.props.id,this.fig);
       var labels = JSON.parse(this.props.labels);
       var tooltip = d3.select("body").append("div")
                    .attr("class", "mpld3-tooltip")
                    .style("position", "absolute")
                    .style("z-index", "10")
                    .style("opacity", 0);

        onMouseOverNode = function(d,i) {
          
            node = labels[i];

            node.log2 = Math.round(node.log2 * 1000)/1000;
            node.pvalue = Math.round(node.pvalue * 1000)/1000;
            if (node.mutation != null && !(node.mutation instanceof Array)) node.mutation = node.mutation.split(";");

            if(clickEvent.holdClick) return;

            //Clear tooltip
            $('#rowtip1').empty();

            //Init tooltip if hover over gene
            if(!_.isUndefined(node.geneID))
              $('#rowtip1').append(tipTemplate(node));

        };

        onMouseOut = function(){

            if(clickEvent.holdClick) return;

            //Clear tooltip
            $('#rowtip1').empty();

        };

        onMouseDown = function(d,i){
            node = labels[i];

            if(clickEvent.holdClick) return;

            //Clear tooltip
            $('#rowtip1').empty();

            //Init tooltip if hover over gene
            if(!_.isUndefined(node.geneID))
              $('#rowtip1').append(tipTemplate(node));

            d3.selectAll("path.mpld3-path").on("mouseout",null);
            d3.selectAll("path.mpld3-path").on("mouseover",null);

            var selected = $("#groups option:selected").val();
            if (selected == "") {
                selected = 'selected-sample';
            }
           
            var newvalue = labels[i].sampleID;

       
            if ($("#"+selected+" option[value='"+newvalue+"']").length === 0 && labels[i].isgroup == "n"){    
                var option = document.createElement("option");
                option.text = labels[i].sampleID;
                option.value = labels[i].sampleID;
                var select = document.getElementById(selected);
                select.appendChild(option);
                }
        };

        $(window).click(function(event){
            if (event.target.getAttribute('class') != "mpld3-figure"){
                if(clickEvent.holdClick) return;
                
                //Clear tooltip
                $('#rowtip1').empty();

                obj.elements().on('mouseout', onMouseOut);
                obj.elements().on('mouseover', onMouseOverNode);
            }    
        });

       obj.elements()
           /*.on("mouseover", function(d, i){
                onMouseOverNode(labels[i]);
                })*/
          .on("mouseover", onMouseOverNode)
           /*.on("mousemove", function(d, i){
                  tooltip
                    .style("top", d3.event.pageY + this.props.voffset + "px")
                    .style("left",d3.event.pageX + this.props.hoffset + "px");
                }.bind(this))*/
          .on("mouseout",  onMouseOut)
          .on("mousedown", onMouseDown);
    };

    d3.json(url,function(data){
        var el = document.getElementById( 'heatmap' );
        while (el.hasChildNodes()) {el.removeChild(el.firstChild);}

        var svg = data[0]["svg"];
        var canvasHeight = data[0]["canvasHeight"];

        mpld3.draw_figure("heatmap", svg);

        d3.selectAll("text")
        .style("font-family","Montserrat, Arial")
        .style("font-size","12px");
        
        document.getElementById('clhmsvg').setAttribute("height", canvasHeight+"px");
        document.getElementById('clhmsvg-toolbar').setAttribute("y", canvasHeight-38);

        maxStrLength = 0;
        document.querySelectorAll('.mpld3-xaxis .tick text').forEach(function(i){
            maxStrLength = i.innerHTML.length > 0 ? i.innerHTML.length : maxStrLength;
            //i.style.transform = "rotate(-90deg) translateX(-"+transX+"em) translateY(-1em)"
        });

        transX = maxStrLength * 0.34;
        $('.mpld3-xaxis .tick text').css('transform','rotate(-90deg) translateX(-'+transX+'em) translateY(-1em)');

    });

}

//Export as App so it could be App.init could be called
module.exports = Heatmap;