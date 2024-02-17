import {Chat} from './Chat.js'

export class Chat_signup{
	constructor(m){
		this.main = m;
	}

	events(){
		this.main.set_status('');
		this.main.dom_room = document.querySelector("#room");
		this.main.dom_submit = document.querySelector("#enter");
		this.main.dom_submit.addEventListener("click", () => this.enter());
		console.log(this.main.dom_room);
		console.log(this.main.dom_submit);
	}

	enter(){
		if (this.main.dom_room.value === ''){
			this.main.set_status('Please enter a room name');
			console.log("error room_name");
			return ;
		}
		this.chat = new Chat(this.main);
		console.log("rom_dom value = " + this.main.dom_room.value);
		$.ajax({
			url: '/transchat/signup/' + this.main.login + '/',
			method: 'POST',
			data: {
				"room": this.main.dom_room.value,
				"username": this.main.login,
			},
			success: (html) => {
				console.log('we enter');
				this.main.load('transchat/' + this.main.dom_room.value, () => this.chat.init());
			}
		})
	}
}