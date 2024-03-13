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
        // this.alias = new Alias(this.main, this);
        this.main.history_stack.push('/profile/' + this.login + '/alias/');
        window.history.pushState({}, '', '/profile/' + this.login + '/alias/');
        this.main.load('/profile/' + this.login + '/alias', () => this.alias_events());
    }
    
    alias_events(){
        this.dom_textfield = document.querySelector('#alias');
        this.dom_confirm = document.querySelector("#confirm");
        console.log(this.dom_confirm);
        this.dom_cancel = document.querySelector('#cancel');
        this.dom_confirm.addEventListener("click", () => this.alias_confirm());
        this.dom_cancel.addEventListener("click", () => this.alias_cancel());
    }

    alias_confirm(){
        if (this.dom_textfield.value === ''){
            this.main.set_status('You must enter a value.');
            return;
        }
        else{
            $.ajax({
                url: '/profile/' + this.main.login + '/alias/',
                method: 'POST',
                data:{
                    'alias': this.dom_textfield.value
                }
            })
        }
        this.main.history_stack.push('/profile/' + this.main.login);
        window.history.pushState({}, '', '/profile/' + this.main.login);
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
    }

    alias_cancel(){
        this.main.history_stack.push('/profile/' + this.main.login);
        window.history.pushState({}, '', '/profile/' + this.main.login);
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
    }

    change_password(){
        // this.change_password = new Change_password(this.main);
        this.main.history_stack.push('/profile/' + this.login + '/change_password/');
        window.history.pushState({}, '', '/profile/' + this.login + '/change_password/');
        this.main.load('/profile/' + this.login + '/change_password', () => this.cp_events());
    }


    cp_events(){
        this.dom_oldvalue = document.querySelector("#oldpwd")
        this.dom_newvalue = document.querySelector("#newpwd");
        this.dom_newvaluerepeat = document.querySelector("#pwdrepeat");
        this.dom_confirm = document.querySelector("#confirm");
        this.dom_cancel = document.querySelector("#cancel");
        this.dom_confirm.addEventListener("click", () => this.cp_change_password());
        this.dom_cancel.addEventListener("click", () => this.cp_cancel());
    }

    cp_change_password(){
        if (this.dom_oldvalue.value === '' || this.dom_newvalue.value === '' || this.dom_newvaluerepeat.value === ''){
            this.main.set_status('You must fill all field');
            return;
        }
        else if (this.dom_newvaluerepeat.value != this.dom_newvalue.value){
            this.main.set_status("Passwords do not match");
            return;
        }
        $.ajax({
            url: '/profile/' + this.main.login + '/change_password/',
            method: 'POST',
            data:{
                'oldpwd': this.dom_oldvalue.value,
                'newpwd': this.dom_newvalue.value,
            },
            success: ()=>{
                this.main.set_status('Password changed succesfully');
                this.main.history_stack.push('/profile/' + this.main.login);
                window.history.pushState({}, '', '/profile/' + this.main.login);
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
            },
            error: (info) =>{
                this.main.set_status(info.responseText);
                this.dom_newvalue.value = '';
                this.dom_newvaluerepeat.value = '';
                this.dom_oldvalue.value = '';
            }
        });
    }

    cp_cancel(){
        this.main.history_stack.push('/profile/' + this.main.login);
        window.history.pushState({}, '', '/profile/' + this.main.login);
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
    }
}