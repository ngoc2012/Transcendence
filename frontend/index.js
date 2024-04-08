import {Main} from './Main.js'

export var main = new Main();

//recupere la data obtenue du callback de l'auth 42 
if (my42login !== null && my42login !== "" && my42email !== "" && my42ws != "")
{
    main.login = my42login;
    main.email = my42email;
    main.enable2fa = my42enable2fa
    main.lobby.ws = my42ws
    main.name = my42name;
    main.dom_name.innerHTML = main.name;
    history.replaceState({}, '', 'https://127.0.0.1:8080');
}

document.addEventListener('DOMContentLoaded', () => {
    
    if (!main.csrftoken) {
        fetch('/get-csrf/')
        .then(response => response.json())
        .then(data => {
            main.csrftoken = data.csrfToken;
        });
    }
    
    if (!main.login)
        checkSession();

    function checkSession() {
        validateSessionToken().then(data => {
            if (data && data.validSession) {
                main.email = data.email;
                main.login = data.login;
                main.name = data.name;
                main.dom_name.innerHTML = data.name;
                main.lobby.ws = data.ws;
                if (data.enable2fa == 'true') {
                    main.load('/twofa', () => main.twofa.events());
                } else {
                    main.history_stack.push('/');
                    window.history.pushState({}, '', '/');
                    main.load('/lobby', () => main.lobby.events());

                    var dom_log_in = document.getElementById('login');
                    if (dom_log_in) {
                        dom_log_in.style.display = "none";
                    }

                    var dom_signup = document.getElementById('signup');
                    if (dom_signup) {
                        dom_signup.style.display = "none";
                        dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton">Logout</button>');
                    }

                    var dom_logout = document.getElementById('logoutButton');
                    if (dom_logout) {
                        dom_logout.addEventListener('click', () => main.logout());
                    }
                }
            } else {
                main.email = '';
                main.login = '';
                main.name = '';
                main.dom_name.innerHTML = 'Anonyme';
                main.lobby.ws = '';
                // main.history_stack.push('/');
                // window.history.pushState({}, '', '/');
                // main.load('/lobby', () => main.lobby.events());
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

    function    reload() {
        const   path = window.location.pathname;
        if (main.lobby.game && main.lobby.game !== undefined)
        {
            main.lobby.game.quit();
            main.lobby.game = undefined;
        }
        if (path === '/login') {
            main.load('/pages/login', () => main.log_in.events());
        } else if (path === '/signup') {
            main.load('/pages/signup', () => main.signup.events());
        } else {
            main.load('/lobby', () => main.lobby.events());
        }
    }
    
    window.onpopstate = function (event) { reload();};
    main.history_stack.push(window.location.pathname);
    window.history.pushState({}, '', window.location.pathname);
    reload();
});