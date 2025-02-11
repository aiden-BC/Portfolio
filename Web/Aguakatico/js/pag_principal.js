//BUSCADOR-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
function buscar(){
    const recetas = [
        {nombre:"macarrones", valor:0},
        {nombre:"sushi", valor:1},
        {nombre:"red velvet", valor:2},
    ]
    let input_buscador=document.getElementById("search");
    let busqueda=input_buscador.value.toLowerCase(); //lo que ponemos en la barra de busqueda
    let lista=document.getElementsByClassName("receta"); //lista de recetas a mostrar u ocultar

    for (receta of recetas){
        let nombre = receta.nombre;
        if (nombre.indexOf(busqueda) !== -1){ //dice si lo que introcudimos coincide con algo de las opciones de recetas
            lista[receta.valor].style.display = "";
        }else{
            lista[receta.valor].style.display = "none"; //oculta
        }
    }
}

//FILTRO-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
function filtrar_facil(){
     let elementosf = document.getElementsByClassName("facil");
     let elementosm = document.getElementsByClassName("media");
     let elementosd = document.getElementsByClassName("dificil");
     for(i = 0; i < elementosf.length; i++) {
        let padre = elementosf[i].parentElement;
        padre.style.display = "";
     }
     for(i = 0; i < elementosm.length; i++) {
        let padre = elementosm[i].parentElement;
        padre.style.display = "none";
     }
     for(i = 0; i < elementosd.length; i++) {
        let padre = elementosd[i].parentElement;
        padre.style.display = "none";
    }
}

function filtrar_media(){
    let elementosf = document.getElementsByClassName("facil");
    let elementosm = document.getElementsByClassName("media");
    let elementosd = document.getElementsByClassName("dificil");
    for(i = 0; i < elementosf.length; i++) {
       let padre = elementosf[i].parentElement;
       padre.style.display = "none";
    }
    for(i = 0; i < elementosm.length; i++) {
       let padre = elementosm[i].parentElement;
       padre.style.display = "";
    }
    for(i = 0; i < elementosd.length; i++) {
       let padre = elementosd[i].parentElement;
       padre.style.display = "none";
   }
}

function filtrar_dificil(){
    let elementosf = document.getElementsByClassName("facil");
    let elementosm = document.getElementsByClassName("media");
    let elementosd = document.getElementsByClassName("dificil");
    for(i = 0; i < elementosf.length; i++) {
       let padre = elementosf[i].parentElement;
       padre.style.display = "none";
    }
    for(i = 0; i < elementosm.length; i++) {
       let padre = elementosm[i].parentElement;
       padre.style.display = "none";
    }
    for(i = 0; i < elementosd.length; i++) {
       let padre = elementosd[i].parentElement;
       padre.style.display = "";
   }
}

function quitar_filtro(){
   let elementosf = document.getElementsByClassName("facil");
   let elementosm = document.getElementsByClassName("media");
   let elementosd = document.getElementsByClassName("dificil");
   for(i = 0; i < elementosf.length; i++) {
      let padre = elementosf[i].parentElement;
      padre.style.display = "";
   }
   for(i = 0; i < elementosm.length; i++) {
      let padre = elementosm[i].parentElement;
      padre.style.display = "";
   }
   for(i = 0; i < elementosd.length; i++) {
      let padre = elementosd[i].parentElement;
      padre.style.display = "";
  }
}

//RECETAS POPULARES---------------------------------------------------------------------------------------------------------------------------------------------------------------------
function mostrar_recetas(){
   var padre=document.getElementById("recetas_populares_padre");
   if (padre.style.display==='none'){
      padre.style.display='block';

   }
   else{
      padre.style.display='none';
   }
}

//ABRIR RECETAS-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
function abrir_macarrones(){
   window.open("receta1.html","_self");
}

function abrir_sushi(){
   window.open("receta2.html","_self");
}

function abrir_redvelvet(){
   window.open("receta3.html","_self");
}

//IMAGENES FOOTER-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
function twitter(){
   window.open('https://twitter.com/');
}
function tiktok(){
   window.open('https://www.tiktok.com/');
}
function insta(){
   window.open('https://www.instagram.com/');
}
function facebook(){
   window.open('https://es-es.facebook.com/');
}