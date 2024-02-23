import {Main} from './Main.js'

var main = new Main();
//<script src="//cdn.rawgit.com/davidshimjs/qrcodejs/gh-pages/qrcode.min.js"></script>

/*
function makeCode() {
  var elText = document.getElementById("text");

  if (!elText.value) {
    alert("Input a text");
    elText.focus();
    return;
  }

  qrcode.makeCode(elText.value);
}

makeCode();

$("#text").
on("blur", function () {
  makeCode();
}).
on("keydown", function (e) {
  if (e.keyCode == 13) {
    makeCode();
  }
});
//# sourceURL=pen.js
*/

//recupere la data obtenue du callback de l'auth 42 
if (my42login !== null && my42login !== "" && my42email !== "" && my42JWT != "")
{
    main.login = my42login;
    main.email = my42email;
    sessionStorage.setItem('JWTToken', my42JWT);
    my42JWT = ""
    main.name = my42name;
    main.dom_name.innerHTML = main.name;
    history.replaceState({}, '', 'https://127.0.0.1:8080');

}

document.addEventListener('DOMContentLoaded', () => {
    main.load('/lobby', () => main.lobby.events());
});
