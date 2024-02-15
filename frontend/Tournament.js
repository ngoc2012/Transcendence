import {Lobby} from './Lobby.js'

export class Tournament {

    constructor(m) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = -1;
        this.players = 0;
        this.minimumPlayers = 3;
        this.inviteSocket = -1;
    }

    events() {
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    events_lobby() {
        this.dom_player_list = document.getElementById('players-list');
        if (this.dom_player_list)
            this.fetchUsers();
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
                this.setInviteSocket();
                this.main.load('/tournament/lobby', () => this.events_lobby());
            },
            error: () => {
                this.main.set_status('Error: Could not create tournament');
            }
        });
    }

    setInviteSocket() {
        const tid = this.id;
        this.inviteSocket = new WebSocket(
            `wss://${window.location.host}/ws/tournament/invite/${tid}/`
        );

        this.inviteSocket.onopen = (e) => {
            console.log("Invite socket connection established for tournament ID:", this.tournamentId);
        }

        this.inviteSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            // display invite notification here
        }

        this.inviteSocket.onerror = (e) => {
            console.error("Invite socket encountered an error: ", e.message);
        }

        this.inviteSocket.onclose = (e) => {
            console.log("Invite socket closed");
        };    
    } 

    fetchUsers() {
        $.ajax({
            url: '/tournament/list/users/',
            method: 'GET',
            success: (data) => {
                const playersList = document.getElementById('players-list');
                playersList.innerHTML = ''; // Clear existing list items
                data.forEach((user) => {
                    const li = document.createElement('li');
                    li.textContent = `${user.login}`;
                    
                    const inviteButton = document.createElement('button');
                    inviteButton.textContent = 'Send Invite';
                    inviteButton.onclick = function() {
                        sendInvite(user.id, this.id);
                    };
                    
                    li.appendChild(inviteButton);
                    playersList.appendChild(li);
                });
            },
            error: () => {
                console.error('Error fetching players');
            }
        });
    }

    sendInvite(userId, tournamentId) {
        if (this.lobby.inviteSocket !== -1 && this.lobby.inviteSocket.readyState === WebSocket.OPEN) {
            const inviteData = {
                action: 'send_invite',
                inviteeId : userId,
                tourId : tournamentId
            };
            this.lobby.inviteSocket.send(JSON.stringify(inviteData));
            console.log(`Game invite sent to ${inviteeId}`);
        } else {
            console.log("Invite socket is not open. Cannot send invite.");
        }
    }

    //     var data = JSON.stringify({
    //         'action' : 'send_invite',
    //         'userId' : userId
    //     });
    //     socket.send(data);
    //     console.log(`Invite sent to ${login}`);
    // }
}