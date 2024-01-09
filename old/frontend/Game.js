export class Game
{
    update_time_interval = 2000;

    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.dom_invite = document.querySelector("#invite");
        this.dom_accept_invitation = document.getElementById("accept_invitation");
        this.dom_cancel_invitation = document.getElementById("cancel_invitation");
        this.dom_online_players_list = document.getElementById("online_players_list");
        this.dom_invitations = document.getElementById("invitations");
        this.dom_invite.addEventListener("click", () => {
            var players = this.get_players_selected();
            //console.log(players);
            if (players.length === 2)
                this.invite(players);
        });

        this.dom_accept_invitation.addEventListener("click", () => {
            if (this.main.status !== "")
                return ;
            if (this.dom_invitations.selectedIndex !== -1) {
                this.accept_invitation(this.dom_invitations.options[this.dom_invitations.selectedIndex].value);
            }
        });

        this.dom_cancel_invitation.addEventListener("click", () => {
            if (this.dom_invitations.selectedIndex !== -1) {
                this.cancel_invitation(this.dom_invitations.options[this.dom_invitations.selectedIndex].value);
            }
        });
        this.update();
    }

    get_players_selected() {
        var options = this.dom_online_players_list && this.dom_online_players_list.options;
        var players_selected = [this.main.user];

        for (var i=0; i < options.length; i++) {
            if (options[i].selected) {
                players_selected.push(options[i].value);
            }
        }
        return (players_selected);
    }

    update_online_players_list(game) {
    //console.log("Update online");
    $.ajax({
        url: '/online_players_list/',
        method: 'POST',
        data: { "user": this.main.user },
        success: (response) => {
            var options = this.dom_online_players_list && this.dom_online_players_list.options;
            if (options && response.online_players_list.length !== options.length + 1) {
                this.dom_online_players_list.innerHTML = "";
                if (response.online_players_list.length > 0) {
                    response.online_players_list.forEach((element) => {
                        if (element !== this.main.user) {
                            var option = document.createElement("option");
                            option.value = element;
                            option.text = element;
                            this.dom_online_players_list.add(option);
                        }
                    });
                }
            }
            var options_invitations = this.dom_invitations && this.dom_invitations.options;
            this.dom_invitations.innerHTML = "";
            if (options_invitations && response.invitations
                && response.invitations.length > 0) {
                response.invitations.forEach((invitation) => {
                    var option = document.createElement("option");
                    option.value = invitation.id;
                    option.text = "" + invitation.id;
                    invitation.players.forEach((p) => {
                        option.text += " - " + p;
                    });
                    this.dom_invitations.add(option);
                });
            }
        },
        error: function(error) {
            //console.error('Error: online players list POST fail', error.message);
        }
    });
}

    update() {
        //console.log("update :" + this.main.user);
        //console.log("status :" + this.main.status);
        if (this.main.status === "playing")
            return ;
        if (this.main.status === "waiting")
            this.check_game_status();
        else
            this.update_online_players_list();
        setTimeout(() => {this.update();}, this.update_time_interval);
    }

    invite(players) {
        //console.log(players);
        $.ajax({
            url: '/invite/',
            method: 'POST',
            data: {
                "host": this.main.user,
                "game": "pong",
                "players": players
            },
            success: (response) => {
                this.main.name = "pong";
                this.main.id = response.id;
                this.main.status = "waiting";
                this.main.game_info = response;
                this.main.dom_status.textContent = "New game " + this.main.name + " " + this.main.id + " created. Wait for players...";
                //this.dom_online_players_list.innerHTML = "";
                //this.dom_invitations.innerHTML = "";
            },
            error: function(error) {
                console.error('Error: invite POST fail', error.message);
            }
        });
    }

    accept_invitation(game_id) {
        $.ajax({
            url: '/accept_invitation/',
            method: 'POST',
            data: {
                "user": this.main.user,
                "game_id": game_id
            },
            success: (response) => {
                this.main.dom_status.textContent = "Game " + this.main.name + " " + this.main.id + " invitation is accepted by " + this.main.user;
                this.main.name = response.game;
                this.main.id = game_id;         
                this.main.status = "waiting";
                this.main.game_info = response;
            },
            error: function(error) {
                console.error('Error: accept invitation POST fail', error.message);
            }
        });
    }

    cancel_invitation(game_id) {
        $.ajax({
            url: '/cancel_invitation/',
            method: 'POST',
            data: {
                "user": this.main.user,
                "game_id": game_id
            },
            success: (response) => {
                this.main.dom_status.textContent = "Game " + this.main.name + " " + game_id + " invitation is canceled by " + this.main.user;
                if (this.main.id === game_id)
                {
                    this.main.name = "";
                    this.main.id = -1;         
                    this.main.status = "";
                }
            },
            error: function(error) {
                console.error('Error: cancel invitation POST fail', error.message);
            }
        });
    }

    check_game_status() {
        $.ajax({
            url: '/check_game_status/',
            method: 'POST',
            data: {
                "user": this.main.user,
                "game_id": this.main.id
            },
            success: (response) => {
                if (response === "canceled") {
                    this.main.dom_status.textContent = "Game " + this.main.name +" " + this.main.id + " is canceled";
                    this.main.name = "";
                    this.main.id = -1;         
                    this.main.status = "";
                }
                else if (response.status === "playing") {
                    this.main.status = "playing";
                    this.main.load('/pong', () => this.main.pong.init());
                    //this.main.dom_status.textContent = "Game " + this.main.name +" " + this.main.id + " is ready";
                }
            },
            error: function(error) {
                //console.error('Error: check game GET fail', error.message);
            }
        });
    }
}


/*
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
*/
