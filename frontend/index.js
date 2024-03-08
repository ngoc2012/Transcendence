import {Main} from './Main.js'

var main = new Main();

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
    function    reload() {
        const   path = window.location.pathname;
        // console.log(path);
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
