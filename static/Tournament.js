import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';
import { localTournament } from './tournamentLocal.js';

export class Tournament {

    constructor(m, id = null) {
        this.main = m;
        this.lobby = m.lobby;
        this.name = ''
        this.id = id;
        this.game = null;
        this.localTournament = null;
        this.userAdded = []
    }

    events(isPopState) {
        if (!isPopState)
            window.history.pushState({page: '/tournament'}, '', '/tournament');

        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }

        this.dom_tournamentForm = document.getElementById('tournamentForm');
        if (this.dom_tournamentForm)
            this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    localBack() {
        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }
        this.localTournament = new localTournament(this.main, this.id, this);
        this.main.load('/tournament/local/start', () => this.localTournament.rematch(false));
    }

    nextMatch() {
        this.main.load('/tournament/local/start', () => this.localTournament.getMatch(false));
    }

    eventsTwoFA(login) {
        const csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/2FAback',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'login': login
                },
                success: (response) => {
                    this.id = response.id;
                    const participants = response.participants;
                    participants.forEach(participant => {this.userAdded.push(participant.login)})
                    this.main.load('/tournament/local', () => this.eventsLocal());
                },
                error: (xhr, jqXHR) => {
                    if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                        this.main.clearClient();
                        this.main.load('/pages/login', () => this.main.log_in.events());
                        return;
                    }
                    this.main.set_status(xhr.responseJSON.error, false);
                }
            });
        }
    }

    eventsLocal(isPopState) {
        if (!isPopState)
            window.history.pushState({page: '/tournament/local'}, '', '/tournament/local');

        var userLogin = false;

        var startBtn = document.getElementById('startTour');
        startBtn.disabled = true;
        this.checkAdded()

        const addPlayerBtn = document.getElementById('addPlayer');
        const playerForm = document.getElementById('playerForm');
        addPlayerBtn.addEventListener('click', () => {
            playerForm.style.display = (playerForm.style.display === 'none' || playerForm.style.display === '' ? 'block' : 'none');
        });

        const passwordField = document.getElementById('passwordField');
        const loginCheckbox = document.getElementById('loginCheckbox');
        loginCheckbox.addEventListener('change', () => {
            passwordField.style.display = loginCheckbox.checked ? 'block' : 'none';
            userLogin = userLogin === false ? true : false;
        });

        const submitBtn = document.getElementById('submitBtn');
        submitBtn.addEventListener('click', (event) => {
            event.preventDefault();
            const password = document.getElementById('passwordTour').value;
            const login = document.getElementById('loginTour').value;

            const isLoginTaken = this.userAdded.some(user => user.login === login) || login === this.main.login;

            if (isLoginTaken) {
                this.main.set_status(`The login ${login} is already in use.`, false);
                return;
            }

            if ((userLogin && password !== "" && login !== "") || (!userLogin && login !== "")) {
                this.addUser(login, password, userLogin);
            } else {
                this.main.set_status('Please fill all required fields', false);
            }
        });
    }

    addUser(login, password, userLogin) {
        const csrftoken = this.main.getCookie('csrftoken');

        const formData = {
            'login': login,
            'password': password,
            'userLogin': userLogin.toString(),
            'tournament_id': this.id
        }

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/adduser/',
                method: 'POST',
                data: JSON.stringify(formData),
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    if (response.success == 'twofa') {
                        this.main.load('/twofa', () => this.main.twofa.eventsTour(this.id, response.login, response.name, response.email));
                    } else {
                        if (response.error) {
                            this.main.set_status(response.error, false)
                        } else {
                            this.userAdded.push(response.login);
                            this.main.load('/tournament/local', () => this.eventsLocal(false));
                        }
                    }
                },
                error: (xhr, jqXHR) => {
                    if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                        this.main.clearClient();
                        this.main.load('/pages/login', () => this.main.log_in.events());
                        return;
                    }
                    this.main.set_status(xhr.responseJSON.error, false);
                }
            });
        }
    }

    checkAdded() {
        const playerStack = document.getElementById('player-stack');
        if (playerStack && this.userAdded.length > 0) {
            playerStack.innerHTML = '<h4 class="text-center mt-5">Participants</h4>';

            this.userAdded.forEach(user => {
                let playerEntry = document.createElement('div');
                playerEntry.textContent = user;
                playerEntry.style.fontFamily = "Poppins, sans-serif";
                playerEntry.style.fontWeight = 400;
                playerEntry.style.fontStyle = "normal";
                playerEntry.style.color = "white";
                playerEntry.classList.add('text-center');
                playerStack.appendChild(playerEntry);
            });


            var startBtn = document.getElementById('startTour');
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.addEventListener('click', () => {
                    this.startTournament();
                });
            }
        }
    }

    startTournament() {
        const csrftoken = this.main.getCookie('csrftoken');

        const formData = {
            id: this.id
        };

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/verify/',
                method: 'POST',
                data: JSON.stringify(formData),
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    this.localTournament = new localTournament(this.main, response.id, this);
                    this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
                },
                error: (xhr, jqXHR) => {
                    if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                        this.main.clearClient();
                        this.main.load('/pages/login', () => this.main.log_in.events());
                        return;
                    }
                    this.main.set_status(xhr.responseJSON.error, false);
                    this.userAdded = [];
                    this.main.load('/tournament/local', () => this.eventsLocal());
                    // this.quitTournament();
                }
            });
        }
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
                    this.name = response.name;
                    this.id = response.id;
                    this.main.load('/tournament/local', () => this.eventsLocal(false));
                },
                error: (xhr, jqXHR) => {
                    if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                        this.main.clearClient();
                        this.main.load('/pages/login', () => this.main.log_in.events());
                        return;
                    }
                    if (xhr.status === 400) {
                        var errorResponse = JSON.parse(xhr.responseText);
                        this.main.set_status('Error: ' + errorResponse.error, false);
                    } else {
                        this.main.set_status('Error: Could not create tournament', false);
                    }
                }
            });
        }
    }

    quitTournament() {
        $.ajax({
            url: '/game/tournament/local/delete',
            method: 'POST',
            headers: {
                'X-CSRFToken': this.main.getCookie('csrftoken')
            },
            data:{
                'id':this.id,
            },
            success: (info) =>{
                this.lobby.game.close_room()
                this.main.set_status(info.status, true)
            },
            error: (info, jqXHR) =>{
                if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                    this.main.clearClient();
					this.main.load('/pages/login', () => this.main.log_in.events());
					return;
				}
                this.lobby.game.close_room()
                this.main.set_status(info.error, false)
            }
        });

        this.main.load('/lobby', () => this.main.lobby.events(false));
    }

    backToLobby() {
        if (this.localTournament && this.localTournament.game) {
            this.localTournament.game.stop();
            this.localTournament.game.preventWinBox = true;
        }
        this.main.load('/lobby', () => this.main.lobby.events(false));
    }
}
