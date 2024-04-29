import {Pong} from './Pong.js'
import { Chat } from './Chat.js'
import { Profile } from './Profile.js'
import {Tournament} from './Tournament.js';

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
        this.game = null;
        this.tournament = null;
        this.ws = null;
    }

    events() {
        this.main.checkcsrf();
        this.main.set_chat();
        this.dom_rooms = document.getElementById("rooms");
        this.dom_tournament = document.getElementById("tournament");
        this.dom_tournament_history = document.getElementById("tournament_history");
        this.dom_join = document.querySelector("#join");
        this.dom_pong = document.querySelector("#pong");
        this.dom_chat = document.querySelector("#chat");
        this.dom_delete = document.querySelector("#delete");
        this.dom_profile = document.querySelector('#profile');
        this.dom_pong.addEventListener("click", () => this.new_game("pong"));
        this.dom_delete.addEventListener("click", () => this.delete_game());
        this.dom_join.addEventListener("click", () => this.join());
		this.dom_chat.addEventListener("click", () => this.start_chat());
        this.dom_profile.addEventListener("click", () => this.profile());
        this.dom_tournament.addEventListener("click", () => this.tournament_click());
        this.dom_tournament_history.addEventListener("click", () => this.tournament_history_click());
        if (this.main.login != '') {
            this.rooms_update();
        }
    }

    eventsCallback(tourid) {
        console.log(tourid)
        this.tournament = new Tournament(this.main, tourid);
        this.main.history_stack.push('/tournament');
        window.history.pushState({}, '', '/tournament');
        this.main.load('/tournament', () => this.tournament.eventsCallback(tourid));
    }

	start_chat(){
		this.main.set_status('')
		if (this.main.login === ''){
			this.main.set_status('You must be logged in to chat.');
			return;
		}
        $.ajax({
			url: '/transchat/chat_lobby/',
			method: 'POST',
			data:{
				'username': this.main.login
			}
		});
        this.main.history_stack.push('/transchat/general_chat/');
        window.history.pushState({}, '', '/transchat/general_chat/');
        this.main.load('transchat/general_chat', () => this.main.chat.events());
	}

    profile(){
        
        if (this.main.login === ''){
            this.main.set_status('You must be logged in to see your profile');
            return ;
        }
        this.main.history_stack.push('/profile/' + this.main.login);
        window.history.pushState({}, '', '/profile/' + this.main.login);
        this.main.load('/profile/' + this.main.login, () => this.main.profile.init());
    }

    join() {
        if (this.main.login === '') {
            this.main.set_status('Please login or sign up');
            return;
        }
        if (this.dom_rooms.selectedIndex === -1) {
            this.main.set_status('Please select a room to join');
            return;
        }
        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/join',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },        
                data: {
                    'login': this.main.login,
                    "game_id": this.dom_rooms.options[this.dom_rooms.selectedIndex].value
                },
                success: (info) => {
                    if (typeof info === 'string') {
                        this.main.set_status(info);
                        this.rooms_update();
                    } else {
                        switch (info.game) {
                            case 'pong':
                                this.pong_game(info);
                                break;
                        }
                    }
                },
                error: () => this.main.set_status('Error: Can not join game')
            });
        } else {
            this.history_stack.push('/login');
            window.history.pushState({page: '/login'}, '', '/login');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    new_game(game) {
        
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up');
            return;
        }
        
        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/new',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'name': 'Star wars',
                    'game': game,
                    'login': this.main.login
                },
                success: (info) => {
                    if (this.socket !== -1)
                        this.socket.send(JSON.stringify({
                            type: 'update'
                        }));
                    if (typeof info === 'string')
                    {
                        this.main.set_status(info);
                        this.rooms_update();
                    }
                    else
                    {
                        switch (info.game) {
                            case 'pong':
                                this.pong_game(info);
                                break;
                        }
                    }
                },
                error: () => this.main.set_status('Error: Can not create game')
            });
        } else {
            this.history_stack.push('/login');
            window.history.pushState({page: '/login'}, '', '/login');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    tournament_history_click() {
        if (this.main.login === ''){
			this.main.set_status('You must be logged to see the tournament history.');
			return;
		}
        this.main.load('/tournament_history', () => this.main.tournament_history.events());
    }
 
    delete_game() {
        
        if (this.main.login === '') {
            this.main.set_status('Please login or sign up');
            return;
        }
        if (this.dom_rooms.selectedIndex === -1) {
            this.main.set_status('Select a game');
            return;
        }

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/delete',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'game_id': this.dom_rooms.options[this.dom_rooms.selectedIndex].value,
                    'login': this.main.login,
                },
                success: (response) => {
                    if (response.token) {
                        sessionStorage.setItem('JWTToken', response.token);
                    }
                    if (response.error) {
                        const message = response.message;
                        this.main.set_status('Error: ' + message);
                    } else if (response.message) {
                        const message = response.message;
                        this.main.set_status(message);
                        if (this.socket !== -1) {
                            this.socket.send(JSON.stringify({
                            type: 'update'
                        }));
                        }
                    }
                    if (this.socket !== -1) {
                        this.socket.send(JSON.stringify({
                            type: 'update'
                        }));
                    }
                },
                error: (xhr, textStatus, errorThrown) => {
                    let errorMessage = "Error: Can not delete game";
                    if (xhr.responseJSON && xhr.responseJSON.error) {
                        errorMessage = xhr.responseJSON.error;
                    }
                    this.main.set_status(errorMessage);
                }
            });
        } else {
            this.history_stack.push('/login');
            window.history.pushState({page: '/login'}, '', '/login');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    pong_game(info) {
        this.quit();
        this.game = new Pong(this.main, this, info);
        this.main.load('/pong', () => this.game.init());
    }

    rooms_update() {
        if (this.socket === -1) {
            this.socket = new WebSocket(
                'wss://'
                + window.location.host
                + '/ws/game/rooms/'
            );
        }

        this.socket.onopen = () => {
            this.socket.send(JSON.stringify({
                type: "authenticate",
                token: this.ws,
            }));
            this.socket.send(JSON.stringify({
                type: 'tournament_registered',
            }));
        };
        $.ajax({
            url: '/game/update',
            method: 'GET',
            success: (rooms) => {
                var options_rooms = this.dom_rooms && this.dom_rooms.options;
                this.dom_rooms.innerHTML = "";
                if (options_rooms && rooms && rooms.length > 0) {
                    rooms.forEach((room) => {
                        var option = document.createElement("option");
                        option.value = room.id;
                        option.text = room.name + " - " + room.id;
                        this.dom_rooms.add(option);
                    });
                }
            },
            error: () => this.main.set_status('Error: Can not update rooms')
        });

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const data = JSON.parse(e.data);
            if (data.type === 'tournament_local_found') {
                this.displayTournamentLocalBack(data.id);
            }
            else if (data.type === 'friend_request_send'){
                this.main.profile.send_request(data);
            }
            else if (data.type === 'friend_request_receive'){
                if (data.receiver === this.main.login){
                    this.main.profile.receive_request(data)
                }
            }
            else {
                const rooms = JSON.parse(e.data);
                var options_rooms = this.dom_rooms && this.dom_rooms.options;
                this.dom_rooms.innerHTML = "";
                if (options_rooms && rooms && rooms.length > 0) {
                    rooms.forEach((room) => {
                        var option = document.createElement("option");
                        option.value = room.id;
                        option.text = room.name + " - " + room.id;
                        this.dom_rooms.add(option);
                    });
                }
            };
        }

        if (this.socket.readyState === 1){
            this.socket.send(JSON.stringify({
                'type': 'status',
                'login': this.main.login
            }));
            this.socket.send(JSON.stringify({
                type: "authenticate",
                token: this.ws,
            }));
            this.socket.send(JSON.stringify({
                type: 'tournament_registered',
            }));
        }
        // this.socket.onclose = (e) => {

        // };
    }

    tournament_click() {
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up');
            return;
        }
        this.tournament = new Tournament(this.main);
        this.main.history_stack.push('/tournament');
        window.history.pushState({page: '/tournament'}, '', '/tournament');
        this.main.load('/tournament', () => this.tournament.events());
    }

    displayTournamentLocalBack(tourID) {
        const existingButton = document.getElementById('tournament');
    
        if (existingButton) {
            const clonedButton = existingButton.cloneNode(true);
            clonedButton.textContent = 'Tournament';
    
            clonedButton.addEventListener('click', () => {
                this.tournament = new Tournament(this.main, tourID);
                this.tournament.localBack();
            });
            existingButton.replaceWith(clonedButton);
        }
    }    

    checkLogin() {
        if (this.main.login != '') {
            this.dom_l
        }
    }

    quit() {
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
    }
}
