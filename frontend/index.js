import {Main} from './Main.js'
import { join_game } from './game.js';

export var main = new Main();

var reload_page = true;

function    reload(path, isPopState = false) {
    if (main.lobby.game && main.lobby.game !== null)
    {
        main.lobby.game.close_room();
        main.lobby.game = null;
    }
    if (path === '/login') {
        main.load('/pages/login', () => main.log_in.events(isPopState));
    } else if (path === '/signup') {
        main.load('/pages/signup', () => main.signup.events(isPopState));
    } else if (path === '/lobby') {
        console.log(isPopState);
        main.load('/lobby', () => main.lobby.events(isPopState));
    } else if (path === '/') {
        main.load('/lobby', () => main.lobby.events(isPopState));
    } else if (path.startsWith('/pong/')) {
        join_game(main, path.substring(6));
    } else if (path === '/transchat/general_chat'){
        main.load('transchat/general_chat', () => main.chat.events(isPopState));
    } else if (path.startsWith('/profile/')){
        main.load('/profile/' + path.substring(9), () => main.profile.init(isPopState));
    } else if (path === '/tournament') {
        main.load('/tournament', () => main.lobby.tournament.events(isPopState));
    } else if (path === '/tournament/local') {
        main.load('/tournament/local', () => main.lobby.tournament.eventsLocal(isPopState));
    } else if (path === '/tournament/local/start') {
        main.load('/tournament/local/start', () => main.lobby.tournament.localTournament.startEvents(isPopState));
    } else if (path === '/tournament_history') {
        main.load('/tournament_history', () => main.tournament_history.events(isPopState));
    }
    else {
        main.load('/lobby', () => main.lobby.events(isPopState));
    }
}

//recupere la data obtenue du callback de l'auth 42
if (my42login !== null && my42login !== "" && my42email !== "" && my42ws != "")
{
    main.login = my42login;
    main.email = my42email;
    main.enable2fa = my42enable2fa
    main.lobby.ws = my42ws
    main.name = my42name;
    main.dom_name.innerHTML = main.name;
    var dom_log_in = document.getElementById('login');
    if (dom_log_in) {
        dom_log_in.style.display = "none";
        dom_log_in.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
    }

    var dom_signup = document.getElementById('signup');
    if (dom_signup) {
        dom_signup.style.display = "none";
    }

    var dom_logout = document.getElementById('logoutButton');
    if (dom_logout) {
        dom_logout.addEventListener('click', () => this.reload());
    }
}



var dom_tournament = document.getElementById("tournament");
dom_tournament.addEventListener("click", () => main.lobby.tournament_click());
var dom_tournament2 = document.getElementById("tournament2");
dom_tournament2.addEventListener("click", () => main.lobby.tournament_click());

var dom_tournament_history = document.getElementById("tournament_history");
dom_tournament_history.addEventListener("click", () => main.lobby.tournament_history_click());
var dom_tournament_history2 = document.getElementById("tournament_history2");
dom_tournament_history2.addEventListener("click", () => main.lobby.tournament_history_click());

var dom_pong = document.getElementById("pong");
var dom_pong2 = document.getElementById("pong2");
dom_pong.addEventListener("click", () => main.lobby.new_game("pong"));
dom_pong2.addEventListener("click", () => main.lobby.new_game("pong"));

var dom_homebar = document.getElementById("homebar");
var dom_homebar2 = document.getElementById("homebar2");
dom_homebar.addEventListener("click", () => main.lobby.homebar());
dom_homebar2.addEventListener("click", () => main.lobby.homebar());

var dom_chat = document.getElementById("chat");
var dom_chat2 = document.getElementById("chat2");
dom_chat.addEventListener("click", () => main.lobby.start_chat());
dom_chat2.addEventListener("click", () => main.lobby.start_chat());

var dom_profile = document.getElementById('profile');
dom_profile.addEventListener("click", () => main.lobby.profile(false));


window.addEventListener('popstate', (event) => {
    reload(event.state.page, true);
});


document.addEventListener('DOMContentLoaded', () => {
    if (!main.csrftoken) {
        fetch('/get-csrf/')
        .then(response => response.json())
        .then(data => {
            main.csrftoken = data.csrfToken;
        });
    }

    const bg = document.getElementById('dynamic-bg');
    let color1 = [166, 192, 254];
    let color2 = [246, 128, 132];
    let targetColor1 = [...color1];
    let targetColor2 = [...color2];

    function interpolateColors(current, target) {
        return current.map((c, i) => {
            if (c < target[i]) {
                return Math.min(c + 1, target[i]);
            } else {
                return Math.max(c - 1, target[i]);
            }
        });
    }

    function updateTargetColors() {
        targetColor1 = targetColor1.map(c => Math.max(0, Math.min(255, c + Math.floor(Math.random() * 50 - 25))));
        targetColor2 = targetColor2.map(c => Math.max(0, Math.min(255, c + Math.floor(Math.random() * 50 - 25))));
    }

    function changeBackground() {
        color1 = interpolateColors(color1, targetColor1);
        color2 = interpolateColors(color2, targetColor2);

        const newColor1 = `rgb(${color1[0]}, ${color1[1]}, ${color1[2]})`;
        const newColor2 = `rgb(${color2[0]}, ${color2[1]}, ${color2[2]})`;

        bg.style.background = `linear-gradient(120deg, ${newColor1}, ${newColor2})`;

        if (color1.every((c, i) => c === targetColor1[i]) && color2.every((c, i) => c === targetColor2[i])) {
            updateTargetColors();
        }
    }

    setInterval(changeBackground, 100);
    updateTargetColors();

    if (!main.login)
        checkSession();

    function checkSession() {
        validateSessionToken().then(data => {
            if (data && data.validSession) {
                reload_page = false;
                main.email = data.email;
                main.login = data.login;
                main.name = data.name;
                main.dom_name.innerHTML = data.name;
                main.lobby.ws = data.ws;
                main.picture = data.avatar;
                if (data.enable2fa == 'true') {
                    main.load('/twofa', () => main.twofa.events());
                } else {
                    if (fromAddUser) {
                        main.load('/lobby', () => main.lobby.eventsCallback(tourid));
                    } else {
                        main.load('/lobby', () => main.lobby.events());
                    }

                    var dom_log_in = document.getElementById('login');
                    if (dom_log_in) {
                        dom_log_in.style.display = "none";
                    }

                    var dom_signup = document.getElementById('signup');
                    if (dom_signup) {
                        dom_signup.style.display = "none";
                        dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
                    }

                    var dom_logout = document.getElementById('logoutButton');
                    if (dom_logout) {
                        dom_logout.addEventListener('click', () => main.logout());
                    }
                    var dom_picture = document.getElementById('picture')
                    if (dom_picture){
                        dom_picture.src=data.avatar.replace('/app/frontend/', 'static/');
                    }
                }
            } else {
                main.email = '';
                main.login = '';
                main.name = '';
                main.dom_name.innerHTML = 'Anonyme';
                main.lobby.ws = '';
            }
        });
    }

    async function validateSessionToken() {
        try {
            let response = await fetch('/validate-session/', {
                method: 'GET',
            });
            if (response.ok) {
                let data = await response.json();
                if (data.validSession) {
                    return data;
                } else {
                    return null;
                }
            } else {
                console.error('Session validation request failed:', response.statusText);
                return null;
            }
        } catch (error) {
            console.error('Error during session validation:', error);
            return null;
        }
    }

    reload(window.location.pathname);
});


