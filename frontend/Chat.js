export class Chat{
	constructor(m, l){
		this.main = m;
        this.lobby = l;
		this.chat_socket = this.main.chat_socket;
	}

	init(){
		this.main.checkcsrf();

		this.chat_socket = this.main.chat_socket;
	}

	events(isPopState){
        if (!isPopState)
            window.history.pushState({page: '/transchat/general_chat/'}, '', '/transchat/general_chat/');
        this.dom_input = document.querySelector('#chat-message-input');
		this.dom_chatlog = document.querySelector('#chat-log');
		this.dom_submit = document.querySelector('#chat-message-submit');
		this.dom_input.addEventListener('keydown', (event) => this.press_enter(event));
		this.dom_submit.addEventListener("click", () => this.send_message())
		this.dom_input.focus();
		const socket = this.socket;
		const login = this.main.login;
		const room = this.roomName;


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
