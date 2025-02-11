
//ARRAY DE IMAGENES-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//arrays de datos
imgs = ["libro1","libro2","libro3","libro4","libro5","libro6","libro7","ut1", "ut2", "ut3", "ut4", "ut5", "ut6", "ut7","ing1", "ing2", "ing3", "ing4", "ing5", "ing6", "ing7"]
ids = ["Diario de recetas", "Recetas veganas", "Recetas mediterráneas", "Recetas para ninyos", "Libro de repostería", "Cocina para diabéticos", "Recetas saludables",
        "Juego de sartenes", "Juego de cubiertos", "Utensilios negros", "Utensilios blancos", "Juego de cuchillos", "Moldes para bombones", "Moldes de tartaletas",
        "Colorante alimetario", "Harina de almendras", "Arroz basmati", "Quinoa", "Chocolate a la taza", "Ramen noodles", "Frutos secos"]
precios = ["10.3", "15.15", "11.99", "3.98", "8.26", "14.8", "6.17", "64.99", "27.78", "32.99", "27.95", "61.99", "5.74", "13.98", "2.98", "18.9", "8.88", "19.9", "16.76", "18.5", "1.99"]

var arr = creaArray(imgs);

//crea el array de imágenes
function creaArray(imgs){
    let arr = [];
    for (img of imgs){
        let ruta_img = "imgs/tienda/"+img+".png";
        arr.push(ruta_img);
    }
    return arr;
}

//crea las imágenes con su texto correspondiente
window.onload = function(){ //ponemos window.onload para que no ejecute la función hasta que no se genere el DOM

    for (let i=0; i<arr.length;i++){
        
        //crea la imagen
        let im = document.createElement("img");
        
        im.setAttribute("src", arr[i]);
        im.setAttribute("id", ids[i]);
        im.setAttribute("data-precio", precios[i]);
        im.setAttribute("width", "115");
        im.setAttribute("height", "170");
        im.setAttribute("ondragstart", "dragStart(event)");
        im.setAttribute("onmouseenter", "aumentar(event)");
        im.setAttribute("onmouseout", "disminuir(event)");

        //crea el texto
        let nom = document.createElement("p");
        let prec = document.createElement("p");

        //sustituye ny por ñ en el html
        if ((ids[i]).search("ny") != -1){
            nom.innerHTML = (ids[i]).replace("ny", "ñ");
        }
        else{
            nom.innerHTML = ids[i];
        }

        nom.style.fontWeight = "bold"; //pone el nombre en negrita
        prec.innerHTML = precios[i]+"€"; //añade € al precio

        //crea un div con la imagen y el texto
        let div = document.createElement("div");
        div.setAttribute("class", "producto");
        div.appendChild(im);
        div.appendChild(nom);
        div.appendChild(prec);

        //añade la imagen donde toca si existe la sección a la que pertenece
        if (imgs[i][0] == "l" && document.body.contains(document.getElementById("libros"))){
            document.getElementById("libros").appendChild(div);
        }
        else if (imgs[i][0] == "u" && document.body.contains(document.getElementById("utensilios"))){
            document.getElementById("utensilios").appendChild(div);
        }
        else if (imgs[i][0] == "i" && document.body.contains(document.getElementById("ingredientes"))){
            document.getElementById("ingredientes").appendChild(div);
        }
        
    }
}

//CARRITO-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

var carro = []; //array del carrito

function dragStart(event) {
    event.dataTransfer.setData("Text", event.target.id); //coge la id del objeto que arrastra
}

function allowDrop(event) {
    event.preventDefault(); 
    //evita el comportamiento habitual del evento -- en un div, el comportamiento habitual es NO soltar (not to drop)
    //para poder realizar el drop, ponemos event.preventDefault();
}

function drop(event) {
    event.preventDefault();

    //variables globales
    nombre = event.dataTransfer.getData("Text"); //id del producto
    total = document.getElementById("total"); //coge la variable del precio total
    total_num = parseFloat(total.innerHTML); //precio total de la compra (tipo float)

    //variables de la función
    var prod = document.getElementById(nombre); //consigue el elemento para poder acceder a sus otras propiedades
    var prec = prod.getAttribute("data-precio"); //accede al precio del producto
    

    if (carro.length == 0){
        //elimina el texto de "arrastre los productos aquí"
        let padre = document.querySelector("#carro");
        let texto = document.querySelector("#carro p");
        padre.removeChild(texto);
    }

    if (carro.findIndex((objeto => objeto.id==nombre)) != -1){ //si el elemento ya está en el carro
        //selecciona el objeto
        let i = carro.findIndex((objeto => objeto.id==nombre));
        let obj = carro[i];
        
        //actualiza la cantidad
        obj.cantidad+=1;
        let cant = document.getElementById(nombre+"c");
        cant.innerHTML = "x" + obj.cantidad;

        //actualiza el subtotal
        obj.subtotal = obj.precio*obj.cantidad;
        let s = document.getElementById(nombre+"s");
        s.innerHTML = "........" + (obj.subtotal).toFixed(2) + "€";
        
    }
    else{
        let c=1; //establece la cantidad en 1

        //añade el producto al array carro
        let objeto = {id:nombre, cantidad:c, precio:prec, subtotal:prec*c};
        carro.push(objeto);

        //clase que le vamos a dar a los elementos que tienen que ver con el producto
        let clase = (objeto.id).replace(/ /g, ""); //quitamos espacios para evitar problemas con el querySelector más tarde

        //crea la variable producto HTML para luego añadirla al carro
        let producto = document.createElement("li");
        
        //sustituye ny por ñ en el html
        if ((objeto.id).search("ny") != -1){
            producto.innerHTML = (objeto.id).replace("ny", "ñ");
        }
        else{
            producto.innerHTML = objeto.id;
        }

        //crea imagen x
        let im = document.createElement("img");
        im.setAttribute("src", "imgs/tienda/x.png");
        im.setAttribute("class", clase);
        im.setAttribute("height", 15);
        im.setAttribute("width", 15);
        im.style.paddingLeft = "10px";
        im.style.paddingTop = "0px";
        im.setAttribute("onclick", "eliminar(event)");

        //añade el precio subtotal del producto
        let sub = document.createElement("p");
        sub.setAttribute("id", objeto.id+"s");
        sub.innerHTML = "........" + (objeto.subtotal).toFixed(2) + "€";

        //añade la cantidad
        let cant = document.createElement("p");
        cant.setAttribute("id", nombre+"c");
        cant.innerHTML = "x" + objeto.cantidad;

        //añade el producto al carro
        lista = document.querySelector("ul#carrito");

        let div1 = document.createElement("div");
        div1.setAttribute("class", clase);
        div1.appendChild(producto);
        div1.appendChild(im);

        lista.appendChild(div1);

        let div2 = document.createElement("div");
        div2.setAttribute("class", clase);
        div2.appendChild(cant);
        div2.appendChild(sub);

        lista.appendChild(div2);
    }

    //calcula el precio total
    total_num += parseFloat(prec);
    total.innerHTML = (total_num).toFixed(2); //redondea el precio a 2 decimales
}

//ELIMINAR PRODUCTO--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

function eliminar(event){
    //selecciona el objeto a eliminar
    let i = carro.findIndex((objeto => (objeto.id).replace(/ /g, "")==event.target.getAttribute("class"))); //obtiene el índice
    let obj = carro[i];

    //actualiza la cantidad
    obj.cantidad-=1;

    //actualiza el precio total    
    total_num -= parseFloat(obj.precio);
    total.innerHTML = (total_num).toFixed(2); //redondea el precio a 2 decimales

    if (obj.cantidad>0){
        //actualiza la cantidad
        let cant = document.getElementById(obj.id+"c");
        cant.innerHTML = "x" + obj.cantidad;

        //actualiza el subtotal
        obj.subtotal = obj.precio*obj.cantidad;

        //actualiza el subtotal
        let s = document.getElementById(obj.id+"s");
        s.innerHTML = "........" + (obj.subtotal).toFixed(2) + "€";
    }
    else{
        //elimina el elemento del carro
        carro.splice(i, 1); //elimina el elemento del array carro

        let cls = (obj.id).replace(/ /g, "");
        let divs = document.querySelectorAll("div."+cls);
        
        //elimina del carrito de la compra
        for (let d of divs){
            lista.removeChild(d);
        }
    }

    if (carro.length==0){
        carro = [0]; //para que la función vaciar() no alerte de que el carro está vacío
        vaciar();
    }

}

//COMPRAR------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

function comprar(){
    //avisa de que el carro está vacío
    if (carro.length == 0){
        alert("Añada elementos al carro para comprar");
    }

    //mensaje de compra y vacía el carro
    else{
        alert("¡Compra realizada con exito!\nVuelva pronto :)");
        vaciar();
    }
}

//VACIAR CARRO-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

function vaciar(){
    //avisa de que el carro está vacío
    if (carro.length == 0){
        alert("El carro está vacío");
    }

    else{
        carro = []; //vacía el array

        //elimina los elementos HTML
        while (lista.firstChild){
            lista.removeChild(lista.lastChild);
        }

        //resetea el carro
        car = document.getElementById("carro");
        arrastra = document.createElement("p");
        arrastra.setAttribute("id", "desaparece");
        arrastra.innerHTML = "Arrastre los productos aquí";
        car.insertBefore(arrastra, car.firstChild);
        total.innerHTML = "0.00";
    }
}

//SALIR DE LA PÁGINA-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
window.onbeforeunload = confirmExit;
function confirmExit()
{
    if (carro.length>0){
        return "";
    }
}

//AUMENTAR IMGS-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
function aumentar(event){
    event.target.style.height = "200px";
    event.target.style.width = "145px";
    event.target.style.border = "2px solid #ab90b9";
}

function disminuir(event){
    event.target.style.height = "170px";
    event.target.style.width = "115px";
    event.target.style.border = "0px solid";
}