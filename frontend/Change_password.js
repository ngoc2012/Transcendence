export class Change_password{
    constructor(m){
        this.main = m;
    }

    events(){
        this.dom_oldvalue = document.querySelector("#oldpwd")
        this.dom_newvalue = document.querySelector("#newpwd");
        this.dom_newvaluerepeat = document.querySelector("#pwdrepeat");
        this.dom_confirm = document.querySelector("#confirm");
        this.dom_cancel = document.querySelector("#cancel");
        this.dom_confirm.addEventListener("click", () => this.change_password());
        this.dom_cancel.addEventListener("click", () => this.cancel());
    }

    change_password(){
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
                this.main.set_status('Password changed succesfully')
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

    cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events());
    }
}