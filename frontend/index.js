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
if (my42login !== null && my42login !== "" && my42email !== "")
{
    main.login = my42login;
    main.email = my42email;

    main.name = my42name;
    main.dom_name.innerHTML = main.name;
}

document.addEventListener('DOMContentLoaded', () => {
    main.load('/lobby', () => main.lobby.events());
});
