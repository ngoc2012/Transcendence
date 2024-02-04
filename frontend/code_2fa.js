
export class code_2fa
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.set_status('');

        this.dom_code = document.querySelector("#code0");
        this.dom_confirm = document.querySelector("#confirm");
        this.dom_cancel = document.querySelector("#cancel0");
        document.getElementById("email_address").innerText = this.main.email;
        this.dom_confirm.addEventListener("click", () => this.confirm());
        this.dom_cancel.addEventListener("click", () => this.cancel());


    }


    confirm() {
        console.log('CONFIRM ACCESSED input code = ', this.dom_code.value);
        if (this.dom_code.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }
        $.ajax({
            url: '/verify/',
            method: 'POST',
            data: {
                "input_code": this.dom_code.value,
            },
            success: (info) => {
                if (typeof info === 'string')
                {
                    this.main.set_status(info);
                }
                else
                {
                    if (info.result == '1')
                        this.main.load('/lobby', () => this.main.lobby.events());
                    else
                        this.main.set_status('Wrong code, please try again');
                }
            },
            error: (data) => this.main.set_status(data.error)
        });
    }


    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
