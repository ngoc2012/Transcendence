import {Lobby} from './Lobby.js'

export class Tournament {

    constructor(m) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = -1;
        this.players = 0;
        this.minimumPlayers = 3;
    }

    events() {
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    events_lobby() {
        this.dom_player_list = document.getElementById('players-list');
        if (this.dom_player_list)
            this.main.lobby.socket.send(JSON.stringify({type: 'request_users_list'}));
    }
    
    tournamentSubmit(event) {
        event.preventDefault();

        const formData = {
            name: document.getElementById('tname').value,
            game: document.getElementById('game').value,
            login: this.main.login,
        };

        $.ajax({
            url: '/tournament/new/',
            method: 'POST',
            data: formData,
            success: (response) => {
                this.id = response.id;
                this.main.set_status('Tournament created successfully');
                console.log(response);
                this.main.load('/tournament/lobby', () => this.events_lobby());
            },
            error: () => {
                this.main.set_status('Error: Could not create tournament');
            }
        });
    }

    userList(users) {
        const playersList = document.getElementById('players-list');
        playersList.innerHTML = ''; // Clear existing list items
        users.forEach((user) => {
            const li = document.createElement('li');
            li.textContent = `${user.login}`; // Display the user's login
            
            const inviteButton = document.createElement('button');
            inviteButton.textContent = 'Send Invite';
            inviteButton.onclick = function() {
                // sendInvite(user.id, this.id);
            };
            
            li.appendChild(inviteButton);
            playersList.appendChild(li);
        });
    }

    // sendInvite(userId, tournamentId) {
    //     if (this.lobby.inviteSocket !== -1 && this.lobby.inviteSocket.readyState === WebSocket.OPEN) {
    //         const inviteData = {
    //             action: 'send_invite',
    //             inviteeId : userId,
    //             tourId : tournamentId
    //         };
    //         this.lobby.inviteSocket.send(JSON.stringify(inviteData));
    //         console.log(`Game invite sent to ${userId}`);
    //     } else {
    //         console.log("Invite socket is not open. Cannot send invite.");
    //     }
    // }
}