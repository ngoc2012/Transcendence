import { Chat } from './Chat.js'

export class Chat_signup{
	constructor(m){
		this.main = m;
	}

	events(){
		this.dom_roomname = document.querySelector("#room-name-input");
		this.dom_submit = document.querySelector("#room-name-submit");
		this.dom_submit.addEventListener("click", () => this.start_chat());
		this.dom_roomname.focus();

		this.dom_roomname.onkeyup = function(e) {
            if (e.keyCode === 13) {
                document.querySelector('#room-name-submit').click();
            }
        };
	}

	start_chat(){
		this.roomname = this.dom_roomname.value;
		if (this.roomname === ''){
			return ;
		}
		this.main.chat = new Chat(this.main);
		$.ajax({
			url: 'transchat/' + this.roomname +'/',
			method: 'POST',
			success: (html) => {
				this.main.load('transchat/' + this.roomname, () => this.main.chat.init());
			}
		})
	}
}
