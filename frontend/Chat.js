export class Chat{
	constructor(m){
		this.main = m;
		this.socket = -1;
	}

	init(){
		this.main.checkcsrf();
		this.dom_input = document.querySelector('#chat-message-input');
		this.dom_chatlog = document.querySelector('#chat-log');
		this.dom_submit = document.querySelector('#chat-message-submit');
		this.roomName = JSON.parse(document.getElementById('room-name').textContent);
		this.dom_input.addEventListener('keydown', (event) => this.press_enter(event));
		this.dom_submit.addEventListener("click", () => this.send_message())
		this.dom_input.focus();

        this.socket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/transchat/'
            + this.roomName
            + '/'
			);
			this.events(this.socket);
		}
		
	events(e){
		var socket = this.socket;
		var login = this.main.login;
		var room = this.roomName;

		this.socket.onopen = function(e) {
			socket.send(JSON.stringify({
				'type': 'connection',
				'message': room,
				'user': login,
			}));
		};

       	this.socket.onmessage = function(e) {
       	    var data = JSON.parse(e.data);
			document.querySelector('#chat-log').value += (data.message + '\n');
       	};

        this.socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
       	};
	}

	send_message(){
		var message = this.dom_input.value;
		this.socket.send(JSON.stringify({
			'message': message,
			'user': this.main.login,
		}));
		this.dom_input.value = '';
	}

	press_enter(e){
		if (e.keyCode === 13) {  // enter, return
			this.dom_submit.click();
		}
	}
}
