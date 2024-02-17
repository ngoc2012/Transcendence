// $(document).on('submit', '#message', function(e){
// 	console.log("on entre ou aps ?")
// 	e.preventDefault();
// 	$.ajax({
// 		type: 'POST',
// 		data: {
// 			message: $('#msg').val(),
// 			csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
// 		},
// 		success: (data) => {
// 			$( ".message" ).load(window.location.href + " .message" );
// 		}
// 	});
// 	$( ".parent" ).load(window.location.href + " .parent" );
// })

// $(document).ready(function(){
// 	setInterval(function(){
// 		$( ".message" ).load(window.location.href + " .message" );
// 	}, 5000)
// })

export class Chat{
	constructor(m){
		this.main = m;
		console.log("creating chat");
	}

	events(){

	}

	init(){
		console.log("entering chat");
		console.log("url = " + 'wss://'
		+ window.location.host
		+ '/transchat/'
		+ this.main.dom_room.value
		+ '/');
		this.socket = new WebSocket(
			'wss://'
			+ window.location.host
			+ '/transchat/'
			+ this.main.dom_room
			+ '/'
		);
		if (this.socket != null){
			console.log("websocket");
		}
	}
}
