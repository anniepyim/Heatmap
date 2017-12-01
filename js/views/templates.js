var glob = ('undefined' === typeof window) ? global : window,

Handlebars = glob.Handlebars || require('handlebars');

this["Templates"] = this["Templates"] || {};

this["Templates"]["Heatmap"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"col-md-12\" style=\"margin-top:10px;\" align=\"center\">\n    Show Heatmap by Processes <select class=\"selectpicker\" id=\"heatmapfolders\" data-style=\"btn-default\" title=\"Pick process\" data-width=\"175px\">\n    </select><img id=\"loading_heatmap_process\" src=\"./img/loading_folder.gif\" height=\"35\" width=\"35\" style=\"display:none\">\n</div>\n<div id=\"heatmap\" class=\"col-md-12\"></div>";
},"useData":true});

this["Templates"]["Heatmap_tooltip"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"col-md-12 title\">"
    + alias4(((helper = (helper = helpers.sample || (depth0 != null ? depth0.sample : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"sample","hash":{},"data":data}) : helper)))
    + "</div>\n<div class=\"col-md-12 title\">"
    + alias4(((helper = (helper = helpers.gene || (depth0 != null ? depth0.gene : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"gene","hash":{},"data":data}) : helper)))
    + "</div>\n\n<div class=\"col-md-12 process\">"
    + alias4(((helper = (helper = helpers.process || (depth0 != null ? depth0.process : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"process","hash":{},"data":data}) : helper)))
    + "</div>\n\n<div class=\"col-md-12 function\">"
    + alias4(((helper = (helper = helpers.nth || (depth0 != null ? depth0.nth : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"nth","hash":{},"data":data}) : helper)))
    + "</div>\n\n<div class=\"col-md-6 miniTitle\">\n    Log2 FC\n</div>\n                \n<div class=\"col-md-6 info\">"
    + alias4(((helper = (helper = helpers.value || (depth0 != null ? depth0.value : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data}) : helper)))
    + "</div>\n";
},"useData":true});

if (typeof exports === 'object' && exports) {module.exports = this["Templates"];}