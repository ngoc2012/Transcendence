export class Chat{
	constructor (m, r){
		this.main = m;
		this.name = "test";
		this.room = r;
		this.connected = false;
		this.socket = -1;
	}

	init(s){
		this.dom_chat_room = document.getElementById("chat_room");
		// this.dom_chat_room.innerHTML = this.room.name;
		this.socket = s
		this.connect();
	}
	
	connect(){
		this.socket.addEventListener("error", (event) => {
			console.log("Websocket error :", event);
		})
	}
}
