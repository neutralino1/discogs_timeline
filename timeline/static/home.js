var Home = {
    init:function(){
	var input = $('input');
	input.bind('focus', function(){
	    $(this).removeClass('faded');
	    $(this).addClass('set');
	});
	input.bind('blur', function(){
	    var value = $(this).val();
	    if (value == 'your@email.com' || value == '' || value == 'password')
	    {
		$(this).addClass('faded');
		$(this).removeClass('set');
	    }
	});
	$('input.email').bind('focus', function(){
	    if ($(this).val() == 'your@email.com')
		$(this).val('');
	});
	$('input.email').bind('blur', function(){
	    if ($(this).val() == '')
		$(this).val('your@email.com');
	});
	$('input.password').bind('focus', function(){
	    if ($(this).val() == 'password')
		$(this).val('');
	});
	$('input.password').bind('blur', function(){
	    if ($(this).val() == '')
		$(this).val('password');
	});
	
    }
};

$(document).ready(function(){
    Home.init();
});

