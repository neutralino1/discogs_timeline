var HomePage = {
    init:function(){
	this.queryInput = $('input#search-query');
	this.emptyValue = this.queryInput.val();
	this.queryInput.bind('focus', function(){
	    if (this.queryInput.val() == this.emptyValue){
		this.queryInput.removeClass('faded');
		this.queryInput.addClass('set');
		this.queryInput.val('');
	    }
	}.bind(this));
	this.queryInput.bind('blur', function(){
	    var value = this.queryInput.val();
	    if (value == '' || value == this.emptyValue)
	    {
		this.queryInput.val(this.emptyValue);
		this.queryInput.addClass('faded');
		this.queryInput.removeClass('set');
	    }
	}.bind(this));
	$('div.collection-item').bind('mouseenter mouseleave', function(){
	    $(this).find('form.delete input').toggleClass('hidden');
	});
    }
};

$(document).ready(function(){
    HomePage.init();
});

