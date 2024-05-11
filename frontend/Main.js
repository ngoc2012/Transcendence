import {Lobby} from './Lobby.js'
import {Signup} from './Signup.js'
import {Login} from './Login.js'
import {Profile} from './Profile.js'
import {twofa} from './twofa.js'
import {code_2fa} from './code_2fa.js'
import {qrcode_2fa} from './qrcode_2fa.js'
import {display_2fa} from './display_2fa.js'
import {tournament_history} from './tournament_history.js'
import {chatBox} from './chatBox.js'
import {Chat} from './Chat.js'
import { Tournament } from './Tournament.js'
import { localTournament } from './tournamentLocal.js'

export class Main
{
    login = '';
    twofa = '';
    name = '';
    email = '';
    id = -1;
    status = '';
    secret_2fa = '';
    history_stack = [];
    csrftoken = '';
    picture = '';
    chat = '';
    chat_socket = -1;

    constructor()
    {
        this.lobby = new Lobby(this);
        this.twofa = new twofa(this);
        this.signup = new Signup(this);
        this.log_in = new Login(this);
        this.code_2fa = new code_2fa(this);
        this.qrcode_2fa = new qrcode_2fa(this);
        this.display_2fa = new display_2fa(this);
        this.tournament_history = new tournament_history(this);
        this.profile = new Profile(this);
        this.chatBox = new chatBox(this)
        this.chat = new Chat(this, this.lobby);
        this.chat.init();
        this.tournament = new Tournament(this);
        this.lobby.tournament = this.tournament;
        this.localTournament = new localTournament(this, null, this.tournament);

        // this.dom_home = document.getElementById("home");
        this.dom_login = document.getElementById("login");
        // this.dom_proceed = document.getElementById("proceed");
        this.dom_signup = document.getElementById("signup");
        this.dom_status = document.getElementById("status");
        // this.dom_tournament = document.getElementById("tournament");
        this.dom_name = document.getElementById("name");
        this.dom_name.innerHTML = "Anonyme";
        // this.dom_email = document.getElementById("email");
        this.dom_container = document.getElementById("main_container");
        // this.dom_login42 = document.getElementById("login42");
        this.dom_signup.addEventListener("click", () => this.signup_click());
        this.dom_login.addEventListener("click", () => this.login_click());
    }

    load(page, callback) {
        $.ajax({
            url: page + '/',
            method: 'GET',
            success: (html) => {
                this.dom_container.innerHTML = html;
                if (callback && typeof callback === 'function') {
                    callback();
                }
            },
            error: (jqXHR, textStatus, errorThrown) => {
                if (jqXHR.status === 401) {
                    this.login_click();
                }
                else
                {
                    this.dom_container.innerHTML = textStatus;
                }
            }
        });
    }

	load_with_data(page, callback, data) {
        $.ajax({
            url: page + '/',
            method: 'GET',
            data : data,
            success: (html) => {
                this.dom_container.innerHTML = html;
                //pas oublier de changer ca
                if (callback && typeof callback === 'function') {
                    callback();
                }
                // callback();  // fait erreur "callback is not a function"
            },
            error: (jqXHR, textStatus, errorThrown) => {
                if (jqXHR.status === 401) {
                    this.login_click();
                }
            }
        });
    }

    login_click() {
        this.load('/pages/login', () => this.log_in.events());
    }

    set_status(s, valid) {
        if (valid === false){
            this.dom_status.innerHTML = s;
            this.dom_status.style.backgroundColor = '#dc3545';
            return;
        }
        this.dom_status.innerHTML = s;
        this.dom_status.style.backgroundColor = '#28a745';
        return;
    }

    signup_click() {
        this.load('/pages/signup', () => this.signup.events());
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    checkcsrf() {
        if (!this.csrftoken) {
            fetch('/get-csrf/')
            .then(response => response.json())
            .then(data => {
                this.csrftoken = data.csrfToken;
            });
        }
    }

    logout() {
        $.ajax({
            url: 'logout/',
            method: 'POST',
            headers: {
                'X-CSRFToken': this.csrftoken,
            },
            success: (info) => {
                if (typeof info === 'string')
                {
                    this.set_status(info, true);
                }
                else
                {
                    this.lobby.quit('logout')

                    this.email = '';
                    this.login = '';
                    this.name = '';
                    this.dom_name.innerHTML = 'Anonyme';
                    this.lobby.ws = '';
                    // this.twofat = '';
                    this.secret_2fa = '';

                    // this.history_stack.push('/');
                    // window.history.pushState({}, '', '/');
                    this.load('/lobby', () => this.lobby.events());

                    var dom_log_in = document.getElementById('login');
                    if (dom_log_in) {
                        dom_log_in.style.display = "block";
                        dom_log_in.addEventListener("click", () => this.login_click());
                    }

                    var dom_signup = document.getElementById('signup');
                    if (dom_signup) {
                        dom_signup.style.display = "block";
                        dom_signup.addEventListener("click", () => this.signup_click());
                    }

                    var dom_logout = document.getElementById('logoutButton');
                    if (dom_logout) {
                        dom_logout.style.display = "none";
                    }
                    var dom_picture = document.getElementById('picture');
                    if (dom_picture){
                        dom_picture.src="static/media/chat.jpg"
                    }
                }
            },
            error: (xhr, textStatus, errorThrown) => {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    this.set_status(xhr.responseJSON.error, false);
                } else {
                    this.set_status('An error occurred during the request.', false);
                }
            }
        });
    }

    find_profile(requester, login){
        var csrftoken = this.getCookie('csrftoken')
        $.ajax({
            url: '/profile/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data:{
                'user': login,
                'requester': requester
            },
            success: (info) => {
                this.load_with_data('/profile/' + login, () => this.profile.events(false, login), {'user':login, 'requester': requester});
                return true;
            }
        })
        return false;
    }


    make_chat(chat_area){
        if (this.login === '')
            chat_area.innerHTML = '';
        if (document.getElementById('chat-log'))
            return;
        let new_element = document.createElement("div");
        let new_chatbox = document.createElement("div");
        let new_textarea = document.createElement('div');
        let new_input = document.createElement('input');
        let new_button = document.createElement('button');
        new_button.id = 'chat-message-submit';
        new_button.type = 'button';
        new_button.className = "btn btn-primary mt-1";
        new_button.innerHTML = 'Send';

        new_button.style.margin = "0 auto";
        new_input.id = "chat-message-input";
        new_input.type = "text";
        new_input.size = "13";
        new_input.className = "form-chat  mt-1";
        new_textarea.id ='chat-log';
        new_textarea.style = 'text-align: left; padding: 5%';
        new_chatbox.id = "chatbox";
        new_chatbox.style = " margin-top: 0; padding-top: 0;"
        new_element.id = "chat";
        new_element.className = "container mt-3";

        new_input.addEventListener('keydown', (event) => {
            event.stopPropagation();
            this.chat.press_enter(event, new_button)
        });

        new_button.addEventListener("click", () => this.chat.send_message(new_input.value, new_input));
        new_chatbox.appendChild(new_textarea);
        new_chatbox.appendChild(new_input);

        new_element.appendChild(new_chatbox);
        new_chatbox.appendChild(new_button);
        chat_area.appendChild(new_element);
    }

    get_friend(login, friend){
        let returnvalue = true;
        $.ajax({
            url: '/profile/' + login + '/add_friend/',
            method: 'POST',
            headers:{
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            data:{
                'type': 'info',
                'user': login,
                'friend': friend
            },
            success: (info) =>{
                returnvalue = true
            },
            error: (info) =>{
                returnvalue = false
            }
        })
        return returnvalue
    }
}
