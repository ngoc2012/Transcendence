export class Profile{
    constructor(m){
        this.main = m;
    }

    events(isPopState, l){
        this.main.checkcsrf();
        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }

        if (!isPopState)
            window.history.pushState({page: '/profile/' + l}, '', '/profile/' + l);

        this.dom_alias = document.getElementById("alias");
        this.dom_friend = document.getElementById("add_friend");
        this.dom_add_friend = document.getElementById('add_user_as_friend');
        this.dom_password = document.getElementById("password");
        this.dom_email = document.getElementById("email");
        this.dom_login = document.getElementById("log_in");
        this.dom_name = document.getElementById("new_name");
        this.dom_cancel = document.getElementById("back");
        this.dom_pp = document.getElementById("new_pp");
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
        if (this.dom_pp)
            this.dom_pp.addEventListener("click", () => this.togglepp());
        if (this.dom_add_friend){
            this.dom_add_friend.addEventListener("click", () => this.main.lobby.socket.send(JSON.stringify({'type': 'friend_request_send', 'sender': this.main.login, 'friend': l})));
            this.dom_add_friend.addEventListener("click", () => this.dom_add_friend.parentNode.removeChild(this.dom_add_friend));
        }
        if (this.main.getCookie('login42') && this.main.login === l) {
            this.dom_password.style.display = 'none';
            this.dom_email.style.display = 'none';
            this.dom_login.style.display = 'none';
            this.dom_name.style.display = 'none';
        }
        this.create_submit_pp();
    }

    create_submit_pp() {
        var uploadpp = document.getElementById("upload_pp");
        let new_form = document.createElement("form");
        let input = document.createElement('input')
        let button = document.createElement('input');
        button.type = "submit";
        button.id = 'submit_button';
        button.className = "btn btn-primary";
        button.value = "Submit";
        input.type = 'file';
        input.name = 'id_file';
        input.required = true;
        input.id = "id_file";
        new_form.enctype = "multipart/form-data"
        new_form.appendChild(input);
        new_form.appendChild(document.createElement("br"));
        new_form.appendChild(button);
        if (uploadpp)
            uploadpp.appendChild(new_form);
        if (new_form)
            new_form.addEventListener('submit', (event) => this.submit_pp(event));
    }

    togglepp() {
        var uploadpp = document.getElementById("upload_pp");
        if (uploadpp) {
            uploadpp.style.display = uploadpp.style.display === 'block' ? 'none' : 'block';
        }
    }

    submit_pp(event){
        event.preventDefault();
        var i = $('#id_file');
        var form = new FormData();
        var input = i[0].files[0];
        form.append('id_file', input);
        if (input.type.search('image') === -1){
            this.main.set_status("Invalid image format", false);
            return;
        }
        fetch('/profile/' + this.main.login + '/change_avatar/', {
            method: 'POST',
            body: form
        }).then(response => response.json())
          .then(response => {
              const newUrl = response.url.replace('/app/frontend', '/static');
              document.getElementById('picture').src = newUrl;
              document.getElementById('profile_picture').src = newUrl;
              this.main.set_status("Profile picture changed.", true);
          })
          .then(this.main.load('/profile/' + this.main.login, () => this.main.profile.events(true, this.main.login)));
    }

    change_alias(){
        this.main.load('/profile/' + this.main.login + '/alias', () => this.alias_events(false));
    }

    alias_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.main.login + '/alias'}, '', '/profile/' + this.main.login + '/alias');
        }
        this.dom_textfield = document.querySelector('#alias');
        this.dom_aliasconfirm = document.querySelector("#confirm");
        this.dom_aliascancel = document.querySelector('#cancel');
        this.dom_aliasconfirm.addEventListener("click", () => this.alias_confirm());
        this.dom_aliascancel.addEventListener("click", () => this.alias_cancel(false));
    }

    alias_confirm(){
        $.ajax({
            url: '/profile/' + this.main.login + '/alias/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                'alias': this.dom_textfield.value
            },
            success: (info) =>{
                this.main.set_status(info, true);
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
            },
            error: (info) =>{
                this.main.set_status(info.responseText, false);
            }
        });
    }

    alias_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
    }

    change_password(){
        this.main.load('/profile/' + this.main.login + '/change_password', () => this.cp_events(false));
    }


    cp_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.main.login + '/change_password'}, '', '/profile/' + this.main.login + '/change_password');
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
            this.main.set_status('You must fill all field', false);
            return;
        }
        else if (this.dom_newvaluerepeat.value != this.dom_newvalue.value){
            this.main.set_status("Passwords do not match", false);
            return;
        }
        $.ajax({
            url: '/profile/' + this.main.login + '/change_password/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                'oldpwd': this.dom_oldvalue.value,
                'newpwd': this.dom_newvalue.value,
            },
            success: (info) => {
                this.main.set_status(info, true);
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
            },
            error: (info) => {
                this.main.set_status(info.responseText, false);
                this.dom_newvalue.value = '';
                this.dom_newvaluerepeat.value = '';
                this.dom_oldvalue.value = '';
            }
        });
    }

    cp_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
    }

    change_email(){
        this.main.load('/profile/' + this.main.login + '/change_email', () => this.ce_events(false));
    }

    ce_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.main.login + '/change_email'}, '', '/profile/' + this.main.login + '/change_email');
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
            this.main.set_status('All fields are required.', false);
            return;
        }
        if (this.dom_cenewemail.value != this.dom_ceconfirmemail.value){
            this.main.set_status('Emails do not match.', false);
            return;
        }
        $.ajax({
            url: '/profile/' + this.main.login + '/change_email/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data: {
                "login": this.main.login,
                "password": this.dom_cepassword.value,
                "email": this.dom_cenewemail.value,
            },
            success: (info)=>{
                this.main.set_status(info, true);
                this.email = this.dom_cenewemail;
                this.main.email = this.email;
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
            },
            error: (info) =>{
                this.main.set_status(info.responseText, false);
            }
        })
    }

    ce_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
    }

    change_login(){
        this.main.load('/profile/' + this.main.login + '/change_login', () => this.cl_events(false));
    }

    cl_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.main.login + '/change_login'}, '', '/profile/' + this.main.login + '/change_login');
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
            this.main.set_status("All fiels are required", false);
            return;
        }
        else if (this.dom_clpassword.value != this.dom_clpasswordrepeat.value){
            this.main.set_status('Passwords do not match', false);
            return;
        }

        $.ajax({
            url: '/profile/' + this.main.login + '/change_login/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                "login": this.main.login,
                "new_login": this.dom_cllogin.value,
                "password": this.dom_clpassword.value
            },
            success: (info)=>{
                this.main.set_status(info, true);
                this.main.chat_socket.send(JSON.stringify({
                    'type': 'connection_update',
                    'old_user': this.main.login,
                    'new_user': this.dom_cllogin.value
                }));
                this.main.login = this.dom_cllogin.value;
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
            },
            error: (info) =>{
                this.main.set_status(info.responseText, false);
            }
        })
    }

    cl_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
    }

    change_name(){
        this.main.load('/profile/' + this.main.login + '/change_name', () => this.cn_events(false));
    }

    cn_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.main.login + '/change_name'}, '', '/profile/' + this.main.login + '/change_name');
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
            this.main.set_status('All fields are required', false);
            return;
        }
        if (this.dom_cn_password.value != this.dom_cn_pwd_repeat.value){
            this.main.set_status("Passwords do not match", false);
            return;
        }
        $.ajax({
            url: '/profile/' + this.main.login + '/change_name/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                'login': this.main.login,
                "name": this.dom_cn_name.value,
                "password": this.dom_cn_password.value
            },
            success: (info)=>{
                this.main.set_status(info, true);
                this.main.name = this.dom_cn_name.value;
                let name = document.getElementById('name');
                if (name){
                    name.innerHTML = this.main.name;
                }
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
            },
            error: (info)=>{
                this.main.set_status(info.responseText, false);
            }
        })
    }

    cn_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
    }

    add_friend(){
        this.main.load('/profile/' + this.main.login + '/add_friend', () => this.friend_events(false));
    }

    friend_events(isPopState){
        if (!isPopState){
            window.history.pushState({page: '/profile/' + this.main.login + '/add_friend'}, '', '/profile/' + this.main.login + '/add_friend');
        }
        this.dom_friend_name = document.querySelector("#friend");
        this.dom_af_confirm = document.querySelector("#confirm");
        this.dom_af_cancel = document.querySelector("#cancel");
        if (this.dom_af_confirm)
            this.dom_af_confirm.addEventListener("click", () => this.af_confirm());
        if (this.dom_af_cancel)
            this.dom_af_cancel.addEventListener("click", () => this.af_cancel());
    }

    af_confirm(){
        if (this.dom_friend_name.value === ''){
            this.main.set_status('All fields are required', false);
            return;
        }
        if (this.dom_friend_name.value === this.main.login){
            this.main.set_status("You can't add yourself as friend", false);
            return ;
        }
        $.ajax({
            url: '/profile/' + this.main.login + '/add_friend/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
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
                this.main.set_status(info, true);
                this.main.load('/profile/' + this.main.login, () => this.friend_events(false));
            },
            error: (info)=>{
                this.main.set_status(info.responseText, false);
            }
        });
    }

    send_request(data){
        $.ajax({
            url: '/profile/' + data.sender + '/add_friend/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                'sender': data.sender,
                'friend': data.friend,
                'type': 'send'
            },
            success: (info)=>{
                this.main.set_status(info, true);
                this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
            },
            error: (info) =>{
                this.main.set_status(info.responseText, false);
            }
        })
    }

    receive_request(data){
        let inviteContainer = document.getElementById('inviteContainer');
        if (inviteContainer) {
            inviteContainer.innerHTML = '';
            inviteContainer.style.display = 'block';

            const inviteNotification = document.createElement('div');
            inviteNotification.classList.add('invite-notification');
            inviteNotification.innerHTML = `
                <p>${data.sender} sent you a friend request !</p>
                <button id="acceptInviteBtn" class="btn btn-primary">Accept</button>
                <button id="declineInviteBtn" class="btn btn-primary">Decline</button>
            `;

            inviteContainer.appendChild(inviteNotification);

            document.getElementById('acceptInviteBtn').addEventListener('click', () => {
                this.accept_request(data);
                inviteContainer.removeChild(inviteNotification);
                inviteContainer.style.display = 'none';
            });
            document.getElementById('declineInviteBtn').addEventListener('click', () => {
                this.decline_request(data);
                inviteContainer.removeChild(inviteNotification);
                inviteContainer.style.display = 'none';
            });
        }
    }

    accept_request(data){
        // console.log('on accepte pour ' + this.main.login);
        $.ajax({
            url: '/profile/' + data.sender + '/add_friend/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                'type': 'receive',
                'sender': data.sender,
                'response': 'accept',
                'friend': this.main.login
            },
            success: (info)=>{
                this.main.set_status(info, true);
            },
            error: (info)=>{
                this.main.set_status(info.responseText, false);
            }
        })
    }

    decline_request(data){
        $.ajax({
            url: '/profile/' + data.sender +'/add_friend/',
            method: 'POST',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data:{
                'type': 'receive',
                'sender': data.sender,
                'response': 'decline'
            },
            success: (info)=>{
                this.main.set_status(info, true);
            },
            error: (info) => {
                this.main.set_status(info.responseText, false);
            }
        })
    }

    af_cancel(){
        this.main.load('/profile/' + this.main.login, () => this.main.profile.events(false, this.main.login));
    }
}
