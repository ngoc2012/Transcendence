import { Alias } from './Alias.js'
import { Change_password } from './Change_password.js'

export class Profile{
    constructor(m){
        this.main = m;
    }

    init(){
        this.login = this.main.login;
        this.email = this.main.email;
        this.name = this.main.name;
        this.tournament_alias = this.login;
        this.history = '';
        this.context = JSON.parse(document.getElementById('user').textContent);
        this.events();
    }

    events(){
        this.dom_alias = document.getElementById("alias");
        this.dom_password = document.getElementById("password")
        this.dom_alias.addEventListener("click", () => this.change_alias());
        this.dom_password.addEventListener("click", () => this.change_password());
    }

    change_alias(){
        this.alias = new Alias(this.main, this);
        this.main.load('/profile/' + this.login + '/alias', () => this.alias.events());
    }

    change_password(){
        this.change_password = new Change_password(this.main);
        this.main.load('/profile/' + this.main.login + '/change_password', () => this.change_password.events());
    }
}