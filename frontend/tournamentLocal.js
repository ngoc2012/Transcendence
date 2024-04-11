import {Pong} from './Pong.js';

export class localTournament {
    constructor(main, playersNicknames, id = null, tournament) {
        this.main = main;
        this.lobby = main.lobby;
        this.id = id;
        this.playersNicknames = playersNicknames;
        this.tournament = tournament;
    }

    startEvents() {
        this.dom_quit_tournament = document.getElementById('quit-tournament');
        this.dom_quit_tournament.addEventListener('click', () => this.tournament.quitTournament());
        this.dom_lobby_tournament = document.getElementById('Lobby');
        this.dom_lobby_tournament.addEventListener('click', () => this.tournament.backToLobby());
    }

    getMatch() {
        var csrftoken = this.main.getCookie('csrftoken');
        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/get/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "id": this.id
                },
                success: (info) => {
                    var tournamentInfosDiv = document.getElementById('tournament-infos');
                    tournamentInfosDiv.textContent = `Tournament - ${info.name} - Round ${info.round} - Match ${info.match}`;
                    var matchInfosDiv = document.getElementById('match-infos');
                    matchInfosDiv.textContent = `${info.player1} vs ${info.player2}`;
                    if (!this.dom_quit_tournament)
                        this.startEvents()
                    this.joinMatch(info.room_id)
                },
                error: () => this.main.set_status('Error: Can not join game')
            });
        } else {
            console.log('Login required');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    joinMatch(roomId) {
        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/join/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "game_id": roomId
                },
                success: (info) => {
                    switch (info.game) {
                        case 'pong':
                            console.log('pooong')
                            this.game = new Pong(this.main, this.main.lobby, info, this);
                            this.main.load('/pong', () => {
                                this.game.init();
                            });
                            break;
                    }
                },
                error: () => this.main.set_status('Error: Can not join game')
            });
        } else {
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }
}