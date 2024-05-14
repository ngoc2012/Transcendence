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
        main.load('/lobby', () => main.lobby.events(isPopState));
    } else if (path === '/') {
        main.load('/lobby', () => main.lobby.events(isPopState));
    } else if (path.startsWith('/pong/')) {
        if (main.login !== '')
            join_game(main, path.substring(6), true);
        else {
            main.load('/pages/login', () => main.log_in.events(false));
            // main.set_status("You need to Log in or Sign up to access this page", false);
        }
    } else if (path.startsWith('/profile/')){
        if (main.login !== '')
            main.load_with_data('/profile/' + path.substring(9), () => main.profile.events(isPopState, path.substring(9)), {'user':path.substring(9), 'requester': main.login});
        else {
            main.load('/pages/login', () => main.log_in.events(false));
            // main.set_status("You need to Log in or Sign up to access this page", false);
        }
    } else if (path === '/tournament') {
        if (main.login !== '')
            main.load('/tournament', () => main.lobby.tournament.events(isPopState));
        else {
            main.load('/pages/login', () => main.log_in.events(false));
            // main.set_status("You need to Log in or Sign up to access this page", false);
        }
    } else if (path === '/tournament/local') {
        if (main.login !== '')
            main.load('/tournament/local', () => main.lobby.tournament.eventsLocal(isPopState));
        else {
            main.load('/pages/login', () => main.log_in.events(false));
            // main.set_status("You need to Log in or Sign up to access this page", false);
        }
    } else if (path === '/tournament/local/start') {
        if (main.login !== '')
            main.load('/tournament/local/start', () => main.lobby.tournament.localTournament.startEvents(isPopState));
        else {
            main.load('/pages/login', () => main.log_in.events(false));
            // main.set_status("You need to Log in or Sign up to access this page", false);
        }
    } else if (path === '/tournament_history') {
        if (main.login !== '')
            main.load('/tournament_history', () => main.tournament_history.events(isPopState));
        else {
            main.load('/pages/login', () => main.log_in.events(false));
            // main.set_status("You need to Log in or Sign up to access this page", false);
        }

    } else {
        main.load('/lobby', () => main.lobby.events(isPopState));
    }
}

if (error_user)
    main.set_status("Login already taken", false);
//recupere la data obtenue du callback de l'auth 42
if (my42login !== null && my42login !== "" && my42email !== "" && my42ws != "")
{
    main.login = my42login;
    main.email = my42email;
    main.enable2fa = my42enable2fa
    main.lobby.ws = my42ws
    main.name = my42name;
    main.dom_name.innerHTML = main.name;
    main.login42 = true;
    main.picture = my42avatar;
    var dom_log_in = document.getElementById('login');
    if (dom_log_in) {
        dom_log_in.style.display = "none";
    }

    var dom_picture = document.getElementById('picture');
    if (dom_picture){
        dom_picture.src = main.picture.replace('/app/frontend/', '/static/');
    }

    var dom_signup = document.getElementById('signup');
    if (dom_signup) {
        dom_signup.style.display = "none";
        var dom_logout = document.getElementById('logoutButton');
        if (dom_logout) {
            // dom_logout.classList.remove("hidden");
            
            dom_logout.style.display = 'inline-block'
            // dom_logout.addEventListener('click', () => main.logout());
            // dom_logout.addEventListener('click', () => this.main.logout());
        }
        else
        {
            dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
            var dom_logout = document.getElementById('logoutButton');
            dom_logout.addEventListener('click', () => main.logout());
        }
    }

}

window.addEventListener('popstate', (event) => {
    if (event.state && event.state.page)
        reload(event.state.page, true);
});


document.addEventListener('DOMContentLoaded', () => {
    if (!main.csrftoken) {
        fetch('/get-csrf/')
        .then(response => response.json())
        .then(data => {
            main.csrftoken = data.csrftoken;
        });
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

    var dom_profile = document.getElementById('profile');
    dom_profile.addEventListener("click", () => main.lobby.profile(false));

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
                        var dom_logout = document.getElementById('logoutButton');
                        if (dom_logout) {
                            // dom_logout.classList.remove("hidden");
                            console.log("coucou index 218")
                            dom_logout.style.display = 'inline-block'
                            // dom_logout.addEventListener('click', () => this.main.logout());
                        }
                        else
                        {
                            dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
                            var dom_logout = document.getElementById('logoutButton');
                            dom_logout.addEventListener('click', () => main.logout());
                        }
                    }

                    // var dom_logout = document.getElementById('logoutButton');
                    // if (dom_logout) {
                    //     dom_logout.addEventListener('click', () => main.logout());
                    // }
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
                // console.error('Session validation request failed:', response.statusText);
                return null;
            }
        } catch (error) {
            // console.error('Error during session validation:', error);
            return null;
        }
    }

    reload(window.location.pathname);
});


