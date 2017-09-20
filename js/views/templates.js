var glob = ('undefined' === typeof window) ? global : window,

Handlebars = glob.Handlebars || require('handlebars');

this["Templates"] = this["Templates"] || {};

this["Templates"]["Heatmap"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"col-md-12\" style=\"margin-top:10px;\" align=\"center\">\n    Show Heatmap by Processes <select class=\"selectpicker\" id=\"heatmapfolders\" data-style=\"btn-default\" title=\"Pick process\" data-width=\"175px\">\n    </select><img id=\"loading_heatmap_process\" src=\"./img/loading_folder.gif\" height=\"35\" width=\"35\" style=\"display:none\">\n</div>\n<div id=\"heatmap\" class=\"col-md-12\"></div>";
},"useData":true});

if (typeof exports === 'object' && exports) {module.exports = this["Templates"];}