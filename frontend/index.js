import {Main} from './Main.js'

var main = new Main();

if (my42login !== null && my42login !== "" && my42email !== "")
{
    main.login = my42login;
    main.email = my42email;

    main.name = my42name;
    main.dom_name.innerHTML = main.name;
}

document.addEventListener('DOMContentLoaded', () => {
    main.load('/lobby', () => main.lobby.events());
});
