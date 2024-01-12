import {Main} from './Main.js'

var main = new Main();

document.addEventListener('DOMContentLoaded', () => {
    main.load('/lobby', () => main.lobby.events());
});
