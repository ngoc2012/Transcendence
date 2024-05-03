import { Chat } from './Chat.js'

export class Chat_signup{
	constructor(m){
		this.main = m;
	}

	events(){
		this.main.checkcsrf();
		this.dom_roomname = document.querySelector("#room-name-input");
		this.dom_submit = document.querySelector("#room-name-submit");
		this.dom_submit.addEventListener("click", () => this.start_chat());
		this.dom_roomname.addEventListener("keydown", (event) => this.enter_chat(event));
		this.dom_roomname.focus();
	}

	enter_chat(e){
		if (e.keyCode === 13){
			this.dom_submit.click();
		}
	}

	start_chat(){
		this.roomname = this.dom_roomname.value;
		if (this.roomname === ''){
			return ;
		}
		this.main.chat = new Chat(this.main);
        // this.main.history_stack.push('/transchat/' + this.roomname);
        // window.history.pushState({}, '', '/transchat/' + this.roomname);
		this.main.load('transchat/' + this.roomname, () => this.main.chat.init());
	}
}
