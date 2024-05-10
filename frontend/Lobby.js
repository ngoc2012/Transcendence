import {Pong} from './Pong.js'
import { Chat } from './Chat.js'
import { Profile } from './Profile.js'
import {Tournament} from './Tournament.js';
import {join_game} from './game.js';

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
        this.game = null;
        this.tournament = null;
        this.ws = null;
        this.socketTour1 = null;
        this.socketTour2 = null;
    }

    events(isPopState) {
        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }

        this.main.checkcsrf();

        if (this.main.login != '') {
            this.rooms_update();
        }
        else {
            var chat_area = document.getElementById('chat_area');
            chat_area.innerHTML = "<p>You must be logged<br>to chat</p>";
        }
        if (!isPopState)
            window.history.pushState({page: '/'}, '', '/');

        this.tournament = new Tournament(this.main);

        this.dom_rooms = document.getElementById("rooms");
        this.dom_join = document.querySelector("#join");
        this.dom_delete = document.querySelector("#delete");

        this.dom_join.addEventListener("click", () => {
            if (this.dom_rooms.selectedIndex === -1) {
                this.main.set_status('Please select a room to join', false);
                return;
            }
            join_game(this.main, this.dom_rooms.options[this.dom_rooms.selectedIndex].value, true);
        });

        var userbox = document.querySelector(".user-box");
        userbox.innerHTML = "<h>Please Log In to see online users</h>";
    }

    // 2FA Tournament
    eventsCallback(tourid) {
        this.tournament = new Tournament(this.main, tourid);
        this.main.load('/tournament/local/start', () => this.tournament.localBack(false));
    }

	start_chat(){
		if (this.main.login === ''){
			this.main.set_status('You must be logged in to chat.', false);
			return;
		}
        $.ajax({
			url: '/transchat/chat_lobby/',
			method: 'POST',
			data:{
				'username': this.main.login
			}
		});
		this.main.chat = new Chat(this.main, this.main.lobby);
	}

    profile(){

        if (this.main.login === ''){
            this.main.set_status('You must be logged in to see your profile', false);
            return ;
        }
        this.main.load_with_data('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login), {'requester': this.main.login, 'user': this.main.login});
    }

    homebar() {
        this.main.load('/lobby', () => this.events(false));
    }

    new_game(game) {
        // console.log('new game');
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up', false);
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
                    'name': 'PONG',
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
                        this.main.set_status(info, true);
                        this.rooms_update();
                    }
                    else
                    {
                        switch (info.game) {
                            case 'pong':
                                this.pong_game(info, false);
                                break;
                        }
                    }
                },
                error: () => this.main.set_status('Error: Can not create game', false)
            });
        } else
            this.main.load('/pages/login', () => this.main.log_in.events(false));
    }

    tournament_history_click() {
        if (this.main.login === ''){
			this.main.set_status('You must be logged to see the tournament history.', false);
			return;
		}
        this.main.load('/tournament_history', () => this.main.tournament_history.events(false));
    }

    delete_game() {

        if (this.main.login === '') {
            this.main.set_status('Please login or sign up', false);
            return;
        }

        if (this.dom_rooms.selectedIndex === -1) {
            this.main.set_status('Select a game', false);
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
                        this.main.set_status('Error: ' + message, false);
                    } else if (response.message) {
                        const message = response.message;
                        this.main.set_status(message, true);
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
                    this.main.set_status(errorMessage, false);
                }
            });
        } else
            this.main.load('/pages/login', () => this.main.log_in.events(false));
    }

    pong_game(info, isPopState, join = false) {
        this.quit('pong');
        this.game = new Pong(this.main, this, info);
        if (join)
            this.game.joined = true;
        this.main.load('/pong', () => this.game.init(isPopState));
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
        };

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const data = JSON.parse(e.data);
            if (data.type === 'friend_request_send'){
                this.main.profile.send_request(data);
            }
            else if (data.type === 'friend_request_receive'){
                if (data.receiver === this.main.login){
                    this.main.profile.receive_request(data)
                }
            }
            else if (data.type === 'users_list'){
                // Je ne sais pas si on doit faire quelque chose ici
            }
            else if (data.type === 'game_invite') {
                this.displayGameInvite(data.message);
            }
            else if (data.type === 'game_invite_ok') {
                this.startInvitePong(data.message);
            }
            else if (data.type === 'game_invite_ready') {
                this.joinInvitePong(data.message);
            }
            else if (data.type === 'game_invite_null') {
                this.main.set_status('Game invitation declined', false)
            }
            else if (data.type === 'rooms') {
                const rooms = data.room;
                const selectElement = document.getElementById('rooms');

                if (selectElement){
                    for (let i = selectElement.options.length - 1; i >= 0; i--) {
                        selectElement.remove(i);
                    }

                    if (rooms && rooms.length > 0) {
                        rooms.forEach((room) => {
                            var option = document.createElement("option");
                            option.value = room.id;
                            let string = room.id.substring(0, 5);
                            option.text = `${room.name} - ${string}... - ${room.owner}`;
                            selectElement.add(option);
                        });
                    } else {
                        var noRoomsOption = document.createElement("option");
                        noRoomsOption.text = "No rooms available";
                        selectElement.add(noRoomsOption);
                    }
                }
            }
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
        }

        if (this.main.chat_socket === -1){
            this.main.chat_socket = new WebSocket(
                'wss://'
                + window.location.host
                + '/ws/transchat/general_chat/'
            );
        }
        this.main.chat_socket.onopen = (e) => {
		    if (this.main.login != ''){
           	    this.main.chat_socket.send(JSON.stringify({
               	    'type': 'connection',
	                'user': this.main.login,
               	}));
		    }
        };

        if (this.main.chat_socket.readyState === 1) {
            this.main.chat_socket.send(JSON.stringify(
                {
                    type:"update",
                }
            ));
        }

       	this.main.chat_socket.onmessage = (e) => {
       	    var data = JSON.parse(e.data);
            var list_user = document.getElementById('user_list');
            var chat_log = document.querySelector('#chat-log');
            chat_log.scrollTop
            if (data.type === 'update_divs'){
                let divs = document.getElementsByClassName('user_chat');
                for (let i = 0; divs[i] != undefined; i++){
                    if (divs[i].innerHTML === data.old_user){
                        divs[i].innerHTML = data.new_user;
                        let new_element = divs[i].cloneNode(true);
                        new_element.addEventListener("click", () => this.main.find_profile(this.main.login, data.new_user));
                        divs[i].parentNode.replaceChild(new_element, divs[i]);
                    }
                }
                let whispers = document.getElementsByClassName('user_chat_whisper');
                for (let i = 0; whispers[i] != undefined; i++){
                    if (whispers[i].innerHTML === data.old_user){
                        whispers[i].innerHTML = data.new_user;
                        let new_element = whispers[i].cloneNode(true);
                        new_element.addEventListener("click", () => this.main.find_profile(this.main.login, data.new_user));
                        whispers[i].parentNode.replaceChild(new_element, whispers[i]);
                    }
                }
                // this.main.refresh_user_list(data.users, data.pictures);
            }
            else if (data.type === 'chat_message'){
                let new_element = document.createElement("a");
                new_element.addEventListener("click", () => this.main.find_profile(this.main.login, data.user));

                if (data.user === this.main.login) {
                    new_element.style = "cursor:pointer; color: rgb(255, 255, 255); background-color: rgba(0, 0, 0, 0.4); border-radius: 10px; padding-left: 10px; padding-right: 10px; margin-top: 5px;";
                } else {
                    new_element.style = "cursor:pointer; color: rgb(0, 0, 0); background-color: rgba(255, 255, 255, 0.8); border-radius: 10px; padding-left: 10px; padding-right: 10px; margin-top: 5px;";
                }
                new_element.innerHTML = data.user;
                new_element.className = 'user_chat';
                let new_message = document.createElement("p");
                new_message.innerHTML = data.message;
                new_message.style = "padding-left: 100px;"
		        document.querySelector('#chat-log').appendChild(new_element);
                new_element.insertAdjacentHTML('afterend', "<br><m>" + data.message + "</m><br>");
                return;
            }
            else if (data.type === 'whisper'){
                if (data.sender === this.main.login){
                    // show you whispered to user
                    let new_element = document.createElement("a");
                    new_element.innerHTML = "You whispered to ";
                    let new_recv = document.createElement("a");
                    new_recv.addEventListener("click", () => this.main.find_profile(this.main.login, data.receiver));
                    new_recv.innerHTML = data.receiver +":";
                    new_recv.style = "cursor:pointer; color: rgb(0, 128, 255); text-decoration: underline;";
                    new_recv.className = "user_chat_whisper";
                    let new_message = document.createElement("m");
                    new_message.innerHTML = data.message;
                    document.querySelector('#chat-log').appendChild(new_element);
                    new_element.insertAdjacentElement('afterend', new_recv);
                    new_recv.insertAdjacentHTML('afterend', "<br><m><strong>" + data.message + "</strong></m><br>");
                }
                else{
                    let new_element = document.createElement("a");
                    new_element.addEventListener("click", () => this.main.find_profile(this.main.login, data.receiver));
                    new_element.style = "cursor:pointer; color: rgb(0, 128, 255); text-decoration: underline;";
                    new_element.innerHTML = data.user + ":";
                    new_element.className = 'user_chat_whisper';
                    let new_message = document.createElement("m");
                    new_message.innerHTML = data.message;
		            document.querySelector('#chat-log').appendChild(new_element);
                    new_element.insertAdjacentHTML('afterend', "<br><m><strong>" + data.message + "</strong></m><br>");
                    return;
                }
            }
            else if (data.type != 'update' && data.type != 'connection' && data.type != 'game_invite_receive'){
                let new_element = document.createElement("a");
                new_element.addEventListener("click", () => this.main.find_profile(this.main.login, data.user));
                new_element.style = "cursor:pointer; color: rgb(0, 128, 255); text-decoration: underline;";
                new_element.innerHTML = data.user + ":";
                new_element.className = 'user_chat';
                let new_message = document.createElement("p");
                new_message.innerHTML = data.message;
		        document.querySelector('#chat-log').appendChild(new_element);
                new_element.insertAdjacentHTML('afterend', "<br><m>" + data.message + "</m><br>");
            }
            else if (data.type === "update") {
                // console.log('update received')
                this.displayUsers(data);
            }
            else if (data.type === 'game_invite_receive'){
                if (data.friend === this.main.login){
                    this.main.lobby.socket.send(JSON.stringify({
                        'type': 'game_invite',
                        'sender': data.sender,
                        'friend': data.friend
                    }));
                }
            }
       	};
        var chat_area = document.getElementById('chat_area');
        
        if (this.main.login != '')
            chat_area.innerHTML = '';
        this.main.make_chat(chat_area);
    }

    displayUsers(data) {
        if (data.type === "update" && this.socket.readyState === 1) {
            var users = data.users;
            var pictures = data.pictures;
            var container = $(".user-box");
            container.empty();

            users.forEach(function(user, index) {
                var userPic = pictures[index].avatar;
                var userContent = $(
                    '<div style="display: flex; align-items: center; margin-bottom: 10px;">' +
                    '<img src="' + 'static/' + userPic + '" alt="Profile Picture" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">' +
                    '<span id ="' + user.login + '_profile" style="flex-grow: 1; cursor:pointer; text-decoration:underline;">' + user.login + '</span>' +
                    '<button id="' + user.login + '_add-friend" class="btn btn-success btn-sm" type="button">Add Friend</button>' +
                    '<button class="btn btn-info btn-sm" type="button">Invite</button>' +
                    '</div>'
                );
                container.append(userContent);
                var button = document.getElementById(user.login + '_add-friend');
                if (this.main.login === user.login){
                    button.addEventListener('click', () => this.main.set_status("You wanna be friend with... Yourself ? Come on...", false));
                }
                else{
                    button.addEventListener('click', () =>
                        $.ajax({
                            url: '/profile/' + this.main.login + '/add_friend/',
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': this.main.getCookie('csrftoken')
                            },
                            data:{
                                'sender': this.main.login,
                                'friend': user.login,
                                'type': 'send',
                            },
                            success: (info) =>{
                                this.main.lobby.socket.send(JSON.stringify({
                                    'sender': this.main.login,
                                    'friend': user.login,
                                    'type': 'friend_request_send'
                                }));
                                this.main.set_status(info, true);
                            },
                            error: (info) =>{
                                this.main.set_status(info.responseText, false)
                            }
                        })
                    );
                }
                var profile = document.getElementById(user.login + '_profile');
                profile.addEventListener('click', () => this.main.find_profile(this.main.login, user.login));
            }, this);
        }
    }

    joinInvitePong(id) {
        join_game(this.main, id, false, true);
    }

    startInvitePong(data) {
        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/new',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'name': 'PONG',
                    'game': 'pong',
                    'login': this.main.login
                },
                success: (info) => {
                    // exclude this room !!!!
                    // if (this.socket !== -1)
                    //     this.socket.send(JSON.stringify({
                    //         type: 'update'
                    //     }));
                    if (typeof info === 'string')
                    {
                        this.main.set_status(info, true);
                        this.rooms_update();
                    }
                    else
                    {
                        this.socket.send(JSON.stringify(
                        {
                            type: "game_invite_ready",
                            sender: this.main.login,
                            invited: data,
                            id: info.id,
                        }));
                        switch (info.game) {
                            case 'pong':
                                this.pong_game(info, false, true);
                                break;
                        }
                    }
                },
                error: () => this.main.set_status('Error: Can not create game', false)
            });
        }
    }

    displayGameInvite(sender) {
        let inviteContainer = document.getElementById('inviteContainer');
        if (inviteContainer) {
            inviteContainer.innerHTML = '';
            inviteContainer.style.display = 'block';

            const inviteNotification = document.createElement('div');
            inviteNotification.classList.add('invite-notification');
            inviteNotification.innerHTML = `
                <p>${sender} sent you a game request !</p>
                <button id="acceptInviteBtn" class="btn btn-primary">Accept</button>
                <button id="declineInviteBtn" class="btn btn-primary">Decline</button>
            `;

            inviteContainer.appendChild(inviteNotification);

            document.getElementById('acceptInviteBtn').addEventListener('click', () => {
                this.gameRequestResponse('accepted', sender);
                inviteContainer.style.display = 'none';
            });
            document.getElementById('declineInviteBtn').addEventListener('click', () => {
                this.gameRequestResponse('declined', sender);
                inviteContainer.style.display = 'none';
            });
        }
    }

    gameRequestResponse(status, sender) {
        if (status === 'accepted' ) {
            this.socket.send(JSON.stringify(
            {
                type: "game_invite_accepted",
                invited: this.main.login,
                sender: sender,
            }));
        } else {
            this.socket.send(JSON.stringify(
            {
                type: "game_invite_declined",
                invited: this.main.login,
                sender: sender,
            }));
        }
    }

    displayUsers(data) {
        var users = data.users;
        var pictures = data.pictures;
        var container = document.getElementById('user-box');
        var counter = 0;

        if (container) {
            container.innerHTML = '';
            users.forEach((user, index) => {
                if (user.login === this.main.login) {
                    return;
                }
                const userPic = pictures[index].avatar;
                const userHtml = `
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <img src="static/${userPic}" alt="Profile Picture" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
                        <span id="${user.login}_profile" style="flex-grow: 1; cursor:pointer; text-decoration:underline;">${user.login}</span>
                        <button id="${user.login}_add-friend" class="btn btn-success btn-sm ml-2" type="button">Add Friend</button>
                        <button id="${user.login}_invite" class="btn btn-info btn-sm ml-2" type="button">Invite</button>
                    </div>
                `;


                container.innerHTML += userHtml;


                const addButton = document.getElementById(user.login + '_add-friend');
                const inviteButton = document.getElementById(user.login + '_invite');
                const profileLink = document.getElementById(user.login + '_profile');

                if (addButton) {
                    addButton.addEventListener('click', () => {
                        this.main.lobby.socket.send(JSON.stringify({
                            'sender': this.main.login,
                            'friend': user.login,
                            'type': 'friend_request_send'
                        }));
                    });
                }
                if (inviteButton) {
                    inviteButton.addEventListener('click', () => {
                        this.main.lobby.socket.send(JSON.stringify({
                            'sender': this.main.login,
                            'friend': user.login,
                            'type': 'game_invite'
                        }));
                    });
                }
                if (profileLink) {
                    profileLink.addEventListener('click', () => {
                        this.main.find_profile(this.main.login, user.login);
                    });
                }
                counter++;
            });


            if (counter === 0) {
                var userbox = document.querySelector(".user-box");
                userbox.innerHTML = "<h>No Users Online</h>";
            }
        }
    }


    tournament_click() {
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up', false);
            return;
        }

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/tournament/request/',
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    if (response.status === 'not_found') {
                        this.tournament = new Tournament(this.main);
                        this.main.load('/tournament', () => this.tournament.events(false));
                    } else {
                        this.tournament = new Tournament(this.main, response.id);
                        this.tournament.localBack();
                    }
                },
                error: () => {
                }
            });
        }
    }

    checkLogin() {
        if (this.main.login != '') {
            this.dom_l
        }
    }

    quit(action) {
        if (action === 'logout'){
            var chat_area = document.getElementById('chat_area');
            if (chat_area){
                chat_area.innerHTML = "<p>You must be logged<br>to chat</p>";
            }
            if (this.main.chat_socket !== -1){
                this.main.chat_socket.send(JSON.stringify({
                    'type': 'update'
                }));
                this.main.chat_socket.close();
                this.main.chat_socket = -1;
            }
        }
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
    }
}
