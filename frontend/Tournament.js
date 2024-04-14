import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';
import { localTournament } from './tournamentLocal.js';

export class Tournament {

    constructor(m, id = null) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = id;
        this.game = null;
        this.ready = -1;
        this.final = 0;
        this.localTournament = null;
    }

    events() {
        this.main.checkcsrf();
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        if (this.dom_tournamentForm)
            this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    eventsLobby() {
        this.main.checkcsrf();
        this.dom_player_list = document.getElementById('players-list');
        if (this.dom_player_list) {
            this.main.lobby.socket.send(JSON.stringify({type: 'request_users_list'}));
            const inviteButton = document.querySelector(`button[data-login='${login}']`);
            this.main.lobby.socket.send(JSON.stringify({type: 'request_users_in_tour', id: `${this.id}`}));
        }
        this.dom_start_tournament = document.getElementById('start-tournament');
        this.dom_start_tournament.disabled = true;
        this.dom_quit_tournament = document.getElementById('quit-tournament');
        this.dom_quit_tournament.addEventListener('click', (e) => this.quitTournament())
    }

    eventsLocal() {
        document.getElementById('playerCount').addEventListener('change', (event) => {
            const numberOfPlayers = event.target.value;
            const form = document.getElementById('playerForm');
            form.innerHTML = '';

            const input = document.createElement('input');
            input.type = 'text';
            input.name = 'player' + 1;
            input.placeholder = `${this.main.login}`;
            input.readOnly = true;
            input.classList.add('ignore');
            form.appendChild(input);
            form.appendChild(document.createElement('br'));            
    
            for (let i = 2; i <= numberOfPlayers; i++) {
                const input = document.createElement('input');
                input.type = 'text';
                input.name = 'player' + i;
                input.placeholder = 'Player ' + i + ' Nickname';
                form.appendChild(input);
                form.appendChild(document.createElement('br'));
            }
            
            if (numberOfPlayers > 0) {
                const submitButton = document.createElement('button');
                submitButton.type = 'submit';
                submitButton.textContent = 'Submit';
                form.appendChild(submitButton);
            }
        });

        document.getElementById('playerForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const inputs = form.querySelectorAll('input[type="text"]:not(.ignore)');
            let allFilled = true;
            let playerNicknames = [];
        
            inputs.forEach(input => {
                if (input.value === '') {
                    allFilled = false;
                } else {
                    playerNicknames.push(input.value);
                }
            });
        
            if (!allFilled) {
                event.preventDefault();
                alert('Please fill out all player nicknames.');
            } else {
                var csrftoken = this.main.getCookie('csrftoken');
                var formData;
                formData = JSON.stringify({ players: playerNicknames, id: this.id});

                if (csrftoken) {
                    $.ajax({
                        url: '/game/tournament/local/verify/',
                        method: 'POST',
                        data: formData,
                        headers: {
                            'X-CSRFToken': csrftoken,
                        },
                        success: (response) => {
                            this.main.set_status = '';
                            this.localTournament = new localTournament(this.main, playerNicknames, this.id, this);
                            this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
                        },
                        error: (xhr) => {
                            this.main.set_status(xhr.responseJSON.error);
                    }
                    });
                }
            }
        });
    }

    eventsStart() {
        this.main.checkcsrf();
        this.dom_matches = document.getElementById('tournament-matches');
        if (this.dom_matches) {
            const data = {
                type: 'tournament_list',
                id: this.id
            };
            this.main.lobby.socket.send(JSON.stringify(data));
        }
        this.dom_lobby_tournament = document.getElementById('Lobby');
        this.dom_lobby_tournament.addEventListener('click', (e) => this.backToLobby())
        this.dom_quit_tournament = document.getElementById('quit-tournament');
        this.dom_quit_tournament.addEventListener('click', (e) => this.quitTournament())
    }
    
    tournamentSubmit(event) {
        event.preventDefault();

        let formData = {
            
            name: document.getElementById('tname').value,
            game: 'pong',
            login: this.main.login,
            local: 'true'
        };

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/tournament/new/',
                method: 'POST',
                data: formData,
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    this.id = response.id;
                    if (response.local === true) {
                        this.main.load('/tournament/local', () => this.eventsLocal());
                    } else {
                        this.main.load('/tournament/lobby', () => this.eventsLobby());
                        this.main.lobby.socket.send(JSON.stringify({type: 'add_to_group', id: this.id}));
                    }
                },
                error: (xhr, textStatus, errorThrown) => {
                    if (xhr.status === 400) {
                    var errorResponse = JSON.parse(xhr.responseText);
                    this.main.set_status('Error: ' + errorResponse.error);
                } else {
                    this.main.set_status('Error: Could not create tournament');
                    }
            }
            });
        } else {
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
        
    }
    
    alreadyIn(users) {
        const acceptedList = document.getElementById('accepted-list');
        users.forEach(user => {
            if (user.login === this.main.login) {
                return;
            }
            const li = document.createElement('li');
            li.setAttribute('data-login', user.login);
            li.textContent = `${user.login}`;
    
            const acceptedButton = document.createElement('button');
            acceptedButton.setAttribute('data-login', user.login);
            acceptedButton.textContent = 'Accepted';
            acceptedButton.disabled = true;
            li.appendChild(acceptedButton);
            acceptedList.appendChild(li);
        });
    }

    createUserListItem(user) {
        const li = document.createElement('li');
        li.textContent = user.login;
        
        const inviteButton = document.createElement('button');
        inviteButton.setAttribute('data-login', user.login);
        inviteButton.textContent = 'Send Invite';
        inviteButton.onclick = () => this.sendInvite(user.login, this.id);
        li.appendChild(inviteButton);
        return li;
    }

    userList(users) {
        const playersList = document.getElementById('players-list');
        const acceptedList = document.getElementById('accepted-list');
        if (acceptedList) {
            const acceptedLogins = new Set([...acceptedList.querySelectorAll('[data-login]')].map(li => li.getAttribute('data-login')));
            if (acceptedLogins) {
                playersList.innerHTML = '';
                
                users.forEach(user => {
                    if (user.login === this.main.login || acceptedLogins.has(user.login)) {
                        return;
                    }
                    const li = this.createUserListItem(user);
                    playersList.appendChild(li);
                });
            }
        }
    }

    tournamentInviteAccepted(login) {
        const inviteButton = document.querySelector(`button[data-login='${login}']`);
        if (inviteButton) {
            inviteButton.textContent = 'Accepted';
            inviteButton.disabled = true;
            
            const li = inviteButton.closest('li');
            const acceptedList = document.getElementById('accepted-list');
            acceptedList.appendChild(li);
        }
    }

    sendInvite(userId, tournamentId) {
        const inviteData = {
            type: 'tournament_invite',
            inviteeId : userId,
            tourId : tournamentId
        };
        this.main.lobby.socket.send(JSON.stringify(inviteData));
    }

    tournamentReady() {
        if (this.ready === -1) {
            this.dom_start_tournament.addEventListener('click', (e) => {this.queryTournamentRound(e); this.startEventInvite();});
            this.dom_start_tournament.disabled = false;
            this.ready = 1;
        }
    }

    queryTournamentRound() {
        const tournamentUrl = `/tournament/${this.id}`;
        this.main.load(tournamentUrl, () => this.eventsStart());
        const data = {
            type: 'tournament_rounds',
            id: this.id
        };
        this.main.lobby.socket.send(JSON.stringify(data));
    }

    queryRoundList() {
        const tournamentUrl = `/tournament/${this.id}`;
        this.main.load(tournamentUrl, () => this.eventsStart());
    }

    endMatch(data) {
        const resultData = {
            type: 'match_result',
            winner: data.win,
            score: data.score,
            winning_score: data.winning_score,
            roomid: data.roomid
        };
        this.main.lobby.socket.send(JSON.stringify(resultData));
        this.queryRoundList();
    }

    startEventInvite() {
        const inviteData = {
            type: 'tournament_event_invite',
            tour_id : this.id
        };
        this.main.lobby.socket.send(JSON.stringify(inviteData));
    }

    tournamentInfos(name, round) {
        const tournamentInfosContainer = document.getElementById('tournament-infos');
        if (tournamentInfosContainer) {
            let content = '';
            if (round === -2) {
                content = `<h3>Tournament - ${name} - Results</h3>`;
            }
            else if (round === -1) {
                this.final = 1;
                content = `<h3>Tournament - ${name} - Round: Final</h3>`;
            }
            else {
                content = `<h3>Tournament - ${name} - Round: ${round}</h3>`;
            }
    
            tournamentInfosContainer.innerHTML = content;
        }
    }

    displayTournamentMatches(matches) {
        const matchesContainer = document.getElementById('tournament-matches');
        if (matchesContainer) {
            matchesContainer.innerHTML = '';
    
            // group matches by round number
            const matchesByRound = matches.reduce((acc, match) => {
                if (!acc[match.round]) {
                    acc[match.round] = [];
                }
                acc[match.round].push(match);
                return acc;
            }, {});
    
            // sort rounds in reverse to display newer rounds first
            Object.keys(matchesByRound).sort((a, b) => b - a).forEach(round => {
                // Create round element
                const roundElement = document.createElement('div');
                roundElement.setAttribute('data-round-number', round);
                roundElement.innerHTML = `<strong>Round: ${round}</strong>`;
                matchesContainer.appendChild(roundElement);
    
                matchesByRound[round].forEach(match => {
                    // Create match element
                    const matchElement = document.createElement('div');
                    matchElement.className = 'match';
                    matchElement.setAttribute('data-match-id', match.room_id);
                    matchElement.innerHTML = `
                        <p>Match: #${match.match_nbr}</p>
                        <p>Player 1: ${match.player1_name} vs. Player 2: ${match.player2_name}</p>
                        <p>Status: ${match.status}</p>
                    `;
                    // append match element directly after its round's header
                    matchesContainer.appendChild(matchElement);
                });
            });
    
            this.main.lobby.socket.send(JSON.stringify({
                type: 'tournament-player-action',
                id: this.id
            }));
        }
    }    

    displayPlayerAction(matchId) {
        const matchElement = document.querySelector(`[data-match-id="${matchId}"]`);
        if (matchElement) {
            const existingButton = matchElement.querySelector('button');
            if (!existingButton) {
                const button = document.createElement('button');
                button.textContent = 'Join';
                matchElement.appendChild(button);
                button.onclick = () => {
                    this.main.lobby.socket.send(JSON.stringify({
                        type: 'tournament-join',
                        tour_id: this.id,
                        match_id: matchId 
                    }));
                };
            }
        }
    }    

    updateMatchStatus(data) {
        const roomId = data.room_id;
        const newStatus = data.status;

        const matchElement = document.querySelector(`[data-match-id="${roomId}"]`);

        if (matchElement) {
            const statusParagraph = matchElement.querySelectorAll('p')[2];
            statusParagraph.innerHTML = `Status: ${newStatus}`;
        }
    }

    winnerDisplay(data) {
        const winnerName = data.winner;
        const container = document.getElementById('winnerNameDisplay');

        if (container) {
            container.innerHTML = '';

            const winnerMsg = document.createElement('div');
            winnerMsg.classList.add('winnerMessage');
            winnerMsg.textContent = `Tournament Terminated | Winner: ${winnerName}`;

            const congratsMsg = document.createElement('div');
            congratsMsg.classList.add('congratulationsMessage');
            congratsMsg.textContent = 'Congratulations!';

            container.appendChild(winnerMsg);
            container.appendChild(congratsMsg);
        }
    }

    joinMatch(data) {
        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/join',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "game_id": data.matchId
                },
                success: (info) => {
                    if (typeof info === 'string')
                        return;
                    else
                    {
                        switch (info.game) {
                            case 'pong':
                                this.game = new Pong(this.main, this.main.lobby, info, this, false);
                                this.main.load('/pong', () => {
                                    this.game.init();
                                });
                                break;
                        }
                    }
                },
                error: () => this.main.set_status('Error: Can not join game')
            });
        } else {
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    quitTournament() {
        const confirmQuit = confirm("Warning: Quitting the tournament will end tournament for every player. Are you sure?");
        
        if (confirmQuit) {
                this.main.lobby.socket.send(JSON.stringify({
                    type: 'tournament-quit',
                    tour_id: this.id,
                }));
                this.id = -1;
                this.game = null;
                this.ready = -1;
                this.final = 0;
                this.lobby.tournament = null;
                this.main.load('/lobby', () => this.main.lobby.events());
            } 
    }

    backToLobby() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    localBack() {
        this.localTournament = new localTournament(this.main, null, this.id, this);
        this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
    }

    inSetup() {
        const parentElement = document.getElementById('tournament-matches');
        if (parentElement) {
            const message = document.createElement('div');
            message.innerHTML = 'Tournament is still in preparation';
            parentElement.appendChild(message);
        }
    }
}