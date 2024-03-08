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
    const   path = window.location.pathname;
    if (path === '/login') {
        window.history.pushState({}, '', '/login');
        main.load('/pages/login', () => main.log_in.events());
    } else if (path === '/signup') {
        window.history.pushState({}, '', '/signup');
        main.load('/pages/signup', () => main.signup.events());
    } else {
        window.history.pushState({}, '', '/');
        main.load('/pages/lobby', () => main.lobby.events());
    }
});
