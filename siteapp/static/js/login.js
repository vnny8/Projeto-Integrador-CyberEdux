//Login
const formularioLogin = document.querySelector(".LoginSubmit");
const InomeLogin = document.querySelector(".nomeLogin");
const IsenhaLogin = document.querySelector(".senhaLogin");
var result = document.getElementById("resultado");

function Logar(){
    return fetch("http://localhost:8080/usuarios/login/" + InomeLogin.value + "/" + IsenhaLogin.value,
    {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "GET"
    })
    .then(response => response.json())
    .then(usuarios => {
        if (usuarios === 1){
            result.className="alert alert-success";
            result.textContent="Logado com sucesso!";// 1 se deu certo, 0 se não deu certo
        } else{
            result.className="alert alert-danger";
            result.textContent="Falha no login";
        }
    })
    .catch(function (resultado) {
            result.className="alert alert-danger";
            result.textContent="Falha no login";
    });
}

formularioLogin.addEventListener('submit', function (event){
    event.preventDefault();
    Logar();
});