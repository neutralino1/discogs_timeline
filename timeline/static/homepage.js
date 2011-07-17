var HomePage = {
    init:function(){
	this.resultsBox = $('div#search-results');
	this.resultsList = $('ul#results-list');
	this.queryInput = $('input#search-query');
	this.emptyValue = this.queryInput.val();
	this.searchLive = $('div#search-live');
	this.liveMessage = $('span#live-message');
	this.progress = $('div#progress');
	this.progressBar = $('div#progress-bar');
	this.setupSearch();
	this.setupCollection();
	$('div.collection-item').bind('mouseenter mouseleave', function(){
	    $(this).find('form.delete input').toggleClass('hidden');
	});
    },
    setupSearch:function(){
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
	$('form#search-form').submit(function(event){
	    this.searchLive.fadeIn(1000);
	    this.resultsList.find('li').remove();
	    this.resultsBox.addClass('hidden');
	    this.progress.css('width','0%');
	    this.liveMessage.text('Querying Discogs ...');
	    var q = this.queryInput.val();
	    this.retrieved = 0;
	    this.search(q, 1);
	    event.preventDefault();
	}.bind(this));
    },
    search:function(query, page){
	$.get("/search", {q:query, p:page}, function(data) {
	    this.resultsBox.removeClass('hidden');
	    this.resultsList.append(data.content);
	    this.bindAddButtons();
	    if (data.page < data.total){
		this.retrieved += data.nres;
		this.progress.css('width',data.page/data.total*100 + '%');
		this.search(query, data.page + 1);
	    }
	    else{
		this.liveMessage.text('Search is over');
		this.progress.css('width','100%');
		this.searchLive.fadeOut(10000);
	    }
	}.bind(this), 'json');
    },
    setupCollection:function(){
	$('form.delete').submit(function(event){
	    var id = $(this).find('input#delete-id').val();
	    var item = $('li#release-'+id);
	    item.fadeOut(1000);
	    $.ajax({
		type:'DELETE',
		url:'/users/delete_release/?id='+id,
		success:function(data){
//		    item.fadeOut(1000, function(){
//			$('div#collection-container').html(data);
//		    });
		}
	    });
	    event.preventDefault();
	});
    },
    bindAddButtons:function(){
	$('form.add-release-form').submit(function(event){
	    console.log(this);
	    console.log($(this).find('input[name]').val());
	    console.log(2);
	    event.preventDefault();
	});
    }
};

$(document).ready(function(){
    HomePage.init();
});

