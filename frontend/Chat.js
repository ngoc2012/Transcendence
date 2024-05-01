export class Chat{
	constructor(m, l){
		this.main = m;
        this.lobby = l;
		this.socket = -1;
	}

	init(){
		this.main.checkcsrf();

        this.socket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/transchat/general_chat/'
			);
        console.log('connecting chat')
	}

	events(e){
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

       	this.socket.onmessage = function(e) {
       	    var data = JSON.parse(e.data);
            var list_user = document.getElementById('user_list');
            console.log(data);
            if (data.type === "refresh" && list_user){
                $( "#user_list" ).load(window.location.href + " #user_list")
                return;
            }
            else if (data.type === 'update'){
                this.main.refresh_user_list(data.users);
                return;
            }
            else
			    document.querySelector('#chat-log').value += (data.message + '\n');
       	};
        this.socket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
       	};
	}

	send_message(){
		const room = this.roomName;
		const message = this.dom_input.value;
		this.socket.send(JSON.stringify({
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
