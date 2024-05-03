export class Profile{
    constructor(m){
        this.main = m;
    }

    init(isPopState){
        this.login = this.main.login;
        this.email = this.main.email;
        this.name = this.main.name;
        this.events(isPopState);
    }

    events(isPopState){
        this.main.checkcsrf();
        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }

        if (!isPopState)
            window.history.pushState({page: '/profile/' + this.login}, '', '/profile/' + this.login);
        
        this.dom_alias = document.getElementById("alias");
        this.dom_friend = document.getElementById("add_friend");
        this.dom_password = document.getElementById("password");
        this.dom_email = document.getElementById("email");
        this.dom_login = document.getElementById("log_in");
        this.dom_name = document.getElementById("new_name");
        this.dom_cancel = document.getElementById("back");
        if (this.dom_alias)
            this.dom_alias.addEventListener("click", () => this.change_alias());
        if (this.dom_friend)
            this.dom_friend.addEventListener("click", () => this.add_friend());
        if (this.dom_password)
            this.dom_password.addEventListener("click", () => this.change_password());
        if (this.dom_email)
            this.dom_email.addEventListener("click", () => this.change_email());
        if (this.dom_login)
            this.dom_login.addEventListener("click", ()=> this.change_login());
        if (this.dom_name)
            this.dom_name.addEventListener("click", () => this.change_name());
        this.dom_cancel.addEventListener("click", () => this.backtolobby());

    }

    backtolobby(){
        this.main.load('/lobby', () => this.main.lobby.events(false));
    }

    change_alias(){
        this.main.load('/profile/' + this.login + '/alias', () => this.alias_events(false));
    }
    
    alias_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.login + '/alias'}, '', '/profile/' + this.login + '/alias');
        }
        this.dom_textfield = document.querySelector('#alias');
        this.dom_aliasconfirm = document.querySelector("#confirm");
        this.dom_aliascancel = document.querySelector('#cancel');
        this.dom_aliasconfirm.addEventListener("click", () => this.alias_confirm());
        this.dom_aliascancel.addEventListener("click", () => this.alias_cancel(false));
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
                },
                success: (info) =>{
                    this.main.set_status(info);
                    this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false));
                },
                error: (info) =>{
                    this.main.set_status(info.responseText);
                }
            });
        }
    }

    alias_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false));
    }

    change_password(){
        this.main.load('/profile/' + this.login + '/change_password', () => this.cp_events(false));
    }


    cp_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.login + '/change_password'}, '', '/profile/' + this.login + '/change_password');
        }
        this.dom_oldvalue = document.querySelector("#oldpwd")
        this.dom_newvalue = document.querySelector("#newpwd");
        this.dom_newvaluerepeat = document.querySelector("#pwdrepeat");
        this.dom_cpconfirm = document.querySelector("#confirm");
        this.dom_cpcancel = document.querySelector("#cancel");
        this.dom_cpconfirm.addEventListener("click", () => this.cp_change_password());
        this.dom_cpcancel.addEventListener("click", () => this.cp_cancel());
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
                this.main.set_status(info);
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false));
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
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false));
    }

    change_email(){
        this.main.load('/profile/' + this.main.login + '/change_email', () => this.ce_events(false));
    }

    ce_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.login + '/change_email'}, '', '/profile/' + this.login + '/change_email');
        }
        this.dom_cenewemail = document.querySelector('#new_email');
        this.dom_cepassword =document.querySelector('#password');
        this.dom_ceconfirmemail = document.querySelector('#email_confirm');
        this.dom_ceconfirm = document.querySelector('#confirm');
        this.dom_cecancel = document.querySelector('#cancel');
        this.dom_ceconfirm.addEventListener("click", () => this.ce_change_email());
        this.dom_cecancel.addEventListener("click", ()=>this.ce_cancel());
    }

    ce_change_email(){
        if (this.dom_cenewemail.value === '' || this.dom_ceconfirmemail.value === '' || this.dom_cepassword.value === ''){
            this.main.set_status('All fields are required.');
            return;
        }
        if (this.dom_cenewemail.value != this.dom_ceconfirmemail.value){
            this.main.set_status('Emails do not match.');
            return;
        }
        $.ajax({
            url: '/profile/' + this.login + '/change_email/',
            method: 'POST',
            data: {
                "login": this.login,
                "password": this.dom_cepassword.value,
                "email": this.dom_cenewemail.value,
            },
            success: (info)=>{
                this.main.set_status(info);
                this.email = this.dom_cenewemail;
                this.main.email = this.email;
                this.main.history_stack.push('/profile/' + this.login + '/');
                window.history.pushState({}, '', '/profile/' + this.login + '/');
                this.main.load('/profile/' + this.login, () => this.main.profile.events());
            },
            error: (info) =>{
                this.main.set_status(info.responseText);
            }
        })
    }

    ce_cancel(){
        this.main.load('/profile/' + this.login, () => this.main.profile.events(false));
    }

    change_login(){
        this.main.load('/profile/' + this.login + '/change_login', () => this.cl_events(false));
    }

    cl_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.login + '/change_login'}, '', '/profile/' + this.login + '/change_login');
        }
        this.dom_cllogin = document.querySelector("#log_in");
        this.dom_clpassword = document.querySelector("#password");
        this.dom_clpasswordrepeat = document.querySelector("#password_repeat");
        this.dom_clconfirm = document.querySelector("#confirm");
        this.dom_clcancel = document.querySelector("#cancel");
        this.dom_clconfirm.addEventListener("click", () => this.cl_confirm());
        this.dom_clcancel.addEventListener("click", () => this.cl_cancel());
    }

    cl_confirm(){
        if (this.dom_cllogin.value === '' || this.dom_clpassword.value === '' || this.dom_clpasswordrepeat.value === ''){
            this.main.set_status("All fiels are required");
            return;
        }
        else if (this.dom_clpassword.value != this.dom_clpasswordrepeat.value){
            this.main.set_status('Passwords do not match');
            return;
        }
        
        $.ajax({
            url: '/profile/' + this.login + '/change_login/',
            method: 'POST',
            data:{
                "login": this.login,
                "new_login": this.dom_cllogin.value,
                "password": this.dom_clpassword.value
            },
            success: (info)=>{
                console.log(info);
                this.login = this.dom_cllogin.value;
                this.main.login = this.login;
                this.main.set_status(info);
                this.main.load('/profile/' + this.login, () => this.main.profile.events(false));
            },
            error: (info) =>{
                this.main.set_status(info.responseText);
            }
        })
    }

    cl_cancel(){
        this.main.load('/profile/' + this.login, () => this.main.profile.events(false));
    }

    change_name(){
        this.main.load('/profile/' + this.login + '/change_name', () => this.cn_events(false));
    }

    cn_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.login + '/change_name'}, '', '/profile/' + this.login + '/change_name');
        }
        this.dom_cn_name = document.querySelector("#newname");
        this.dom_cn_password = document.querySelector("#password");
        this.dom_cn_pwd_repeat = document.querySelector("#password_repeat");
        this.dom_cnconfirm = document.querySelector("#confirm");
        this.dom_cncancel = document.querySelector("#cancel");
        this.dom_cnconfirm.addEventListener("click", () => this.cn_confirm());
        this.dom_cncancel.addEventListener("click", () => this.cn_cancel());
    }

    cn_confirm(){
        if (this.dom_cn_name.value === '' || this.dom_cn_password.value === '' || this.dom_cn_pwd_repeat.value === '' ){
            this.main.set_status('All fields are required');
            return;
        }
        if (this.dom_cn_password.value != this.dom_cn_pwd_repeat.value){
            this.main.set_status("Passwords do not match");
            return;
        }
        $.ajax({
            url: '/profile/' + this.login + '/change_name/',
            method: 'POST',
            data:{
                'login': this.login,
                "name": this.dom_cn_name.value,
                "password": this.dom_cn_password.value
            },
            success: (info)=>{
                this.main.set_status(info);
                this.main.name = this.dom_cn_name;
                this.main.load('/profile/' + this.login, () => this.main.profile.events(false));
            },
            error: (info)=>{
                this.main.set_status(info.responseText);
            }
        })
    }

    cn_cancel(){
        this.main.load('/profile/' + this.login, () => this.main.profile.events(false));
    }

    add_friend(){
        this.main.load('/profile/' + this.login + '/add_friend', () => this.friend_events(false));
    }

    friend_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.login + '/add_friend'}, '', '/profile/' + this.login + '/add_friend');
        }
        this.dom_friend_name = document.querySelector("#friend");
        this.dom_af_confirm = document.querySelector("#confirm");
        this.dom_af_cancel = document.querySelector("#cancel");
        this.dom_af_confirm.addEventListener("click", () => this.af_confirm());
        this.dom_af_cancel.addEventListener("click", () => this.af_cancel());
    }

    af_confirm(){
        if (this.dom_friend_name.value === ''){
            this.main.set_status('All fields are required');
            return;
        }
        $.ajax({
            url: '/profile/' + this.main.login + '/add_friend/',
            method: 'POST',
            data:{
                'sender': this.main.login,
                'friend': this.dom_friend_name.value,
                'type': 'send'
            },
            success: (info)=>{
                this.main.lobby.socket.send(JSON.stringify({
                    'sender': this.main.login,
                    'friend': this.dom_friend_name.value,
                    'type': 'friend_request_send'
                }));
                this.main.set_status(info);
                this.main.load('/profile/' + this.login, () => this.friend_events(false));
            },
            error: (info)=>{
                this.main.set_status(info.responseText);
            }
        });
    }

    send_request(data){
        $.ajax({
            url: '/profile/' + data.sender + '/add_friend/',
            method: 'POST',
            data:{
                'sender': data.sender,
                'friend': data.friend,
                'type': 'send'
            },
            success: (info)=>{
                this.main.set_status(info);
                this.main.load('/profile/' + this.login, () => this.main.profile.events(false));            
            },
            error: (info) =>{
                this.main.set_status(info.responseText);
            }
        })
    }

    receive_request(data){
        let inviteContainer = document.getElementById('inviteContainer');
        if (!inviteContainer) {
            inviteContainer = document.createElement('div');
            inviteContainer.id = 'inviteContainer';
            document.body.appendChild(inviteContainer);
        }

        const inviteNotification = document.createElement('div');
        inviteNotification.classList.add('invite-notification');
        inviteNotification.innerHTML = `
            <p>${data.sender} sent you a friend request !</p>
            <button id="acceptInviteBtn">Accept</button>
            <button id="declineInviteBtn">Decline</button>
        `;

        inviteContainer.appendChild(inviteNotification);

        document.getElementById('acceptInviteBtn').addEventListener('click', () => {
            this.accept_request(data);
            inviteContainer.removeChild(inviteNotification);
        });
        document.getElementById('declineInviteBtn').addEventListener('click', () => {
            this.decline_request(data);
            inviteContainer.removeChild(inviteNotification);
        });
    }

    accept_request(data){
        console.log('on accepte pour ' + this.login);
        $.ajax({
            url: '/profile/' + data.sender + '/add_friend/',
            method: 'POST',
            data:{
                'type': 'receive',
                'sender': data.sender,
                'response': 'accept',
                'friend': this.main.login
            },
            success: (info)=>{
                this.main.set_status(info);
            },
            error: (info)=>{
                this.main.set_status(info.responseText);
            }
        })
    }

    decline_request(data){
        $.ajax({
            url: '/profile/' + data.sender +'/add_friend/',
            method: 'POST',
            data:{
                'type': 'receive',
                'sender': data.sender,
                'response': 'decline'
            },
            success: (info)=>{
                this.main.set_status(info);
            },
            error: (info) => {
                this.main.set_status(info.responseText);
            }
        })
    }

    af_cancel(){
        this.main.load('/profile/' + this.login, () => this.main.profile.events(false));
    }
}