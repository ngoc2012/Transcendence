$(document).on('submit', '#message', function(e){
	console.log("on entre ou aps ?")
	e.preventDefault();
	$.ajax({
		type: 'POST',
		data: {
			message: $('#msg').val(),
			csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
		},
		success: (data) => {
			$( ".message" ).load(window.location.href + " .message" );
		}
	});
	$( ".parent" ).load(window.location.href + " .parent" );
})

$(document).ready(function(){
	setInterval(function(){
		$( ".message" ).load(window.location.href + " .message" );
	}, 500)
})