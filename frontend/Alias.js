export class Alias{
    constructor(m){
        this.main = m;
    }

    events(){
        this.dom_textfield = document.querySelector('#alias');
        this.dom_confirm = document.querySelector("#confirm");
        console.log(this.dom_confirm);
        this.dom_cancel = document.querySelector('#cancel');
        this.dom_confirm.addEventListener("click", () => this.confirm());
        this.dom_cancel.addEventListener("click", () => this.cancel());
    }

    confirm(){
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
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
    }

    cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
    }
}