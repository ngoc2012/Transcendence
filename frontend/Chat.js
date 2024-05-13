export class Chat{
	constructor(m, l){
		this.main = m;
        this.lobby = l;
		this.chat_socket = this.main.chat_socket;
	}

	init(){
		this.chat_socket = this.main.chat_socket;
	}

	events(isPopState){
        if (!isPopState)
            window.history.pushState({page: '/transchat/general_chat'}, '', '/transchat/general_chat');
        this.dom_input = document.getElementById('chat-message-input');
		this.dom_chatlog = document.querySelector('#chat-log');
		this.dom_submit = document.querySelector('#chat-message-submit');
		this.dom_back = document.querySelector("#back");
		this.dom_input.addEventListener('keydown', (event) => this.press_enter(event));
		this.dom_submit.addEventListener("click", () => this.send_message())
		this.dom_back.addEventListener("click", () => this.close());
		this.dom_input.focus();
		const socket = this.socket;
		const login = this.main.login;
		const room = this.roomName;
	}

	send_message(msg, div){
		const room = this.roomName;
		const message = msg;
		$.ajax({
			url: '/chat/check_message',
			method: 'POST',
			headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
			data:{
				'message': message,
				'user': this.main.login
			},
			success: (info, xhr) => {
				if (xhr.status === 302)
					return;
				this.main.chat_socket.send(JSON.stringify({
					'message': message,
					'user': this.main.login,
					'room' : room,
					'type': 'chat_message'
				}));
			},
			error: (jqXHR) =>{
				if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
					this.main.load('/pages/login', () => this.main.log_in.events());
					return;
				}
				console.error('Invalid data sent');
			}
		});
        div.value = '';
	}

	press_enter(e, div){
		if (e.keyCode === 13) {  // enter, return
			div.click();
		}
	}

	close(){
		this.main.load('/lobby', () => this.main.lobby.events(false));
	}
}
