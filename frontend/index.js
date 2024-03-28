import {Main} from './Main.js'

export var main = new Main();

//recupere la data obtenue du callback de l'auth 42 
if (my42login !== null && my42login !== "" && my42email !== "" && my42JWT != "")
{
    main.login = my42login;
    main.email = my42email;
    sessionStorage.setItem('JWTToken', my42JWT);
    my42JWT = ""
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
    
    checkSession();

    function checkSession() {
        const jwtToken = sessionStorage.getItem('JWTToken');
        if (jwtToken) {
            console.log(jwtToken)
            validateSessionToken(jwtToken).then(data => {
                if (data && data.validSession) {
                    main.email = data.email;
                    main.login = data.login;
                    main.name = data.name;
                    main.dom_name.innerHTML = data.name;
                    
                    if (data.enable2fa == 'true') {
                        main.load('/twofa', () => main.twofa.events());
                    } else {
                        main.history_stack.push('/');
                        window.history.pushState({}, '', '/');
                        main.load('/lobby', () => main.lobby.events());
                    }
                } else {
                    console.log('Session is not valid');
                }
            });
        } else {
            console.log('No JWT token found');
        }
    }

    async function validateSessionToken(jwtToken) {
        try {
            let response = await fetch('/validate-session/', {
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + jwtToken,
                },
            });
            if (response.ok) {
                let data = await response.json();
                if (data.validSession) {
                    return data;
                } else {
                    console.error('Session validation failed: Invalid session');
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
        // console.log('reload path')
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