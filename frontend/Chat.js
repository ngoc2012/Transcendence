export class Chat{
	constructor(m, l){
		this.main = m;
        this.lobby = l;
		this.chat_socket = this.main.chat_socket;
	}

	init(){
		this.main.checkcsrf();

        this.main.chat_socket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/transchat/general_chat/'
		);
		this.chat_socket = this.main.chat_socket;
		console.log('connecting chat')
		this.socket_events(this);
	}

	events(isPopState){
        if (!isPopState)
            window.history.pushState({page: '/profile/transchat/general_chat/'}, '', '/transchat/general_chat/');
        this.dom_input = document.querySelector('#chat-message-input');
		this.dom_chatlog = document.querySelector('#chat-log');
		this.dom_submit = document.querySelector('#chat-message-submit');
		this.roomName = JSON.parse(document.getElementById('room-name').textContent);
		this.dom_input.addEventListener('keydown', (event) => this.press_enter(event));
		this.dom_submit.addEventListener("click", () => this.send_message())
		this.dom_input.focus();
		const socket = this.socket;
		const login = this.main.login;
		const room = this.roomName;


	}

	socket_events(c){
		c.main.chat_socket.onopen = function(e) {
			if (c.main.login != ''){
				console.log("sending connecting message");
            	c.main.chat_socket.send(JSON.stringify({
                	'type': 'connection',
	                'user': c.main.login,
            	}));
			}
        };

       	c.main.chat_socket.onmessage = function(e) {
       	    var data = JSON.parse(e.data);
            var list_user = document.getElementById('user_list');
            if (data.type === 'update'){
                c.main.refresh_user_list(data.users);
                return;
            }
            else
			    document.querySelector('#chat-log').value += (data.message + '\n');
       	};
        c.main.chat_socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
       	};
	}
	send_message(){
		const room = this.roomName;
		const message = this.dom_input.value;
		this.main.chat_socket.send(JSON.stringify({
			'message': message,
			'user': this.main.login,
            'room' : room,
            'type': 'chat_message'
		}));
		this.dom_input.value = '';
	}

	press_enter(e){
		if (e.keyCode === 13) {  // enter, return
			this.dom_submit.click();
		}
	}
}
