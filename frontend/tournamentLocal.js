import {Pong} from './Pong.js';

export class localTournament {
    constructor(main, id = null, tournament) {
        this.main = main;
        this.lobby = main.lobby;
        this.id = id;
        this.tournament = tournament;
        this.player1 = '';
        this.player2 = '';
    }

    startEvents(isPopState) {
        // this.dom_quit_tournament = document.getElementById('quit-tournament');
        // this.dom_quit_tournament.addEventListener('click', () => this.tournament.quitTournament());
    }

    rematch(isPopState) {
        this.getMatch();
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
                    this.player1 = info.player1;
                    this.player2 = info.player2;
                    var tournamentInfosDiv = document.getElementById('tournament-infos');
                    var tournamentInfos2Div = document.getElementById('tournament-infos2');
                    var matchInfosDiv = document.getElementById('match-infos');
                    if (info.round === 'Terminated') {
                        tournamentInfosDiv.textContent = `Tournament ${info.name}`;
                        tournamentInfos2Div.textContent = ` `;
                        matchInfosDiv.textContent = `Congratulations ${info.tourwinner}!`;
                        this.displayResults(info.results)
                    }
                    else {
                        tournamentInfosDiv.textContent = `Tournament ${info.name}`;
                        matchInfosDiv.textContent = `Round ${info.round} - Match ${info.match}`;
                    }
                    if (!this.dom_quit_tournament)
                        this.startEvents();
                        this.joinMatch(info.room_id);
                },
                error: () => this.main.set_status('Error: Can not join game', false)
            });
        }
    }

    displayResults(results) {
        this.dom_quit_tournament = document.getElementById('quit-tournament');
        if (this.dom_quit_tournament)
            this.dom_quit_tournament.style.display = 'none';

        var match = document.getElementById('match');
        match.innerHTML = '';
        match.innerHTML = '<h4>Match History</h4>';

        var container = document.getElementById('tournament-matches');
        
        container.innerHTML = '';
        
        results.forEach((match, index) => {
            var top = document.getElementById('tournament-infos');
            let windowtop = window.scrollY, topPosition = top.scrollTop;
            const matchElement = document.createElement('div');
            matchElement.className = 'match-info';
            matchElement.innerHTML = `
                <h5>Match ${match.match_number}</h5>
                <p>Round ${match.round_number}</p>
                <p>Player 1: ${match.player1} (${match.p1_score})</p>
                <p>Player 2: ${match.player2} (${match.p2_score})</p>
                <p>Winner: ${match.winner}</p>`;

            container.appendChild(matchElement);
            top.scrollTop = topPosition

            if (index < results.length - 1) {
                const hr = document.createElement('hr');
                container.appendChild(hr);
            }
        });
    }

    joinMatch(roomId) {
        var csrftoken = this.main.getCookie('csrftoken');
        this.dom_container = document.getElementById('match');

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/join/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "game_id": roomId,
                },
                success: (info) => {
                    switch (info.game) {
                        case 'pong':
                            this.game = new Pong(this.main, this.main.lobby, info, this.tournament, this, true, this.id);
                            this.dom_container = document.getElementById('match');
                            this.load('/pong/local', () => {
                                this.game.init();
                            });
                            break;
                    }
                },
                error: () => this.main.set_status('Error: Can not join game', false)
            });
        }
    }

    load(page, callback) {
        $.ajax({
            url: page + '/',
            method: 'GET',
            success: (html) => {
                this.dom_container.innerHTML = html;
                if (callback && typeof callback === 'function') {
                    callback();
                }
            },
            error: (jqXHR, textStatus, errorThrown) => {
                if (jqXHR.status === 401) {
                    this.login_click();
                }
            },
        });
    }

    sendResult(score1, score2, room) {
        var csrftoken = this.main.getCookie('csrftoken');
        $.ajax({
            url: '/game/tournament/local/result/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: {
                'room': room,
                'score1': score1,
                'score2': score2
            },
            success: (info) => {
                // this.tournament.localBack();
            },
            error: (jqXHR, textStatus, errorThrown) => {
                if (jqXHR.status === 401) {
                    this.login_click();
                }
            }
        })
    }
}
