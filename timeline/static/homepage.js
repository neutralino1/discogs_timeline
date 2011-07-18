var NotificationArea = {
    init:function(){
        this.searchLive = $('div#search-live');
        this.liveMessage = $('span#live-message');
        this.progress = $('div#progress');
	this.progressBar = $('div#progress-bar');
    },
    show:function(){
        this.searchLive.fadeIn(1000);
    },
    hide:function(){
        this.searchLive.fadeOut(5000);
    },
    startSearch:function(){
        this.updateProgress(0, 100);
        this.setMessage('Querying Discogs ...');
    },
    updateProgress:function(n, total){
 	this.progress.css('width', 100.*n/total + '%');
    },
    finishSearch:function(){
        this.setMessage('Search is over');
        this.updateProgress(100, 100);
        this.hide();
    },
    setMessage:function(message){
       this.liveMessage.text(message);
    }
};

var Search = {
    init:function(){
	this.resultsBox = $('div#search-results');
	this.resultsList = $('ul#results-list');
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
	this.searchForm = $('form#search-form');
	this.searchForm.submit(function(event){
            NotificationArea.show();
	    this.resultsList.find('li').remove();
	    this.resultsBox.addClass('hidden');
            NotificationArea.startSearch();
	    var q = this.searchForm.serialize();
	    this.retrieved = 0;
	    this.search(q, 1);
	    event.preventDefault();
	}.bind(this));
    },
    search:function(query, page){
	if(this.request) this.request.abort();
	this.request = $.get("/search", query+'&p='+page, function(data) {
	    this.resultsBox.removeClass('hidden');
	    this.resultsList.append(data.content);
	    this.bindAddButtons();
	    if (data.page < data.total){
		this.retrieved += data.nres;
                NotificationArea.updateProgress(data.page, data.total);
		this.search(query, data.page + 1);
	    }
	    else{
                NotificationArea.finishSearch();
	    }
	}.bind(this), 'json');
    },
    bindAddButtons:function(){
	$('form.add-release-form').each(function(){
	    $(this).unbind();
	    $(this).submit(function(event){
		$.post($(this).attr('action'), $(this).serialize(), function(data){
		    MyCollection.fill(data);
		});
		event.preventDefault();
	    }.bind(this));
	});
    }
};

var MyCollection = {
    init:function(){
        this.setupHover();
        this.bindDeleteButtons();
	this.container = $('div#collection-container');
    },
    setupHover:function(){
	$('div.collection-item').bind('mouseenter mouseleave', function(){
	    $(this).find('form.delete input').toggleClass('hidden');
	});
    },
    bindDeleteButtons:function(){
	$('form.delete').submit(function(event){
	    var id = $(this).find('input#delete-id').val();
	    var item = $('li#release-'+id);
	    item.fadeOut(1000);
	    $.ajax({
		type:'DELETE',
		url:'/users/delete_release/?id='+id
	    });
	    event.preventDefault();
	});
    },
    fill:function(data){
	this.container.html(data);
	this.init();
    }
};

var HomePage = {
    init:function(){
	MyCollection.init();
        NotificationArea.init();
        Search.init();
    },
};

$(document).ready(function(){
    HomePage.init();
});

