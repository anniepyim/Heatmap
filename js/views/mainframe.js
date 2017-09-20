var templates = require('./templates');

module.exports = Backbone.View.extend({
        
    Heatmap: templates.Heatmap,
    
    renderHeatmap: function(id){
        this.$el.append(this.Heatmap());
        return this;
    }
    
});
