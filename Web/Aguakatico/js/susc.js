//alert
function alerta(){
    let nombre = document.getElementById("nombre");
    let correo = document.getElementById("correo");
    let contr = document.getElementById("pass");

    if (nombre.value != '' && correo.value!='' && contr.value!=''){
        alert(`¡Bienvenid@, ${nombre.value}!\nSu suscripción ha sido realizada con éxito.`)
    }
    
}