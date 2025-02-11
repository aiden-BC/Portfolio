//====================================================================================//
//                                FUNCIONALIDAD PAGINA                                //
//===================================================================================//

// CONSTANTES------------------------------------------------------------
const colorInput = document.getElementById("colorInput");
const circle = document.getElementById("circle");
const botonColorPicker = document.getElementById("boton-colorpicker");
const botonCuentagotas = document.getElementById("cuentagotas");
const botonAdd = document.getElementById('boton-add');
const botonAceptar = document.getElementById("boton-aceptar");
const botonEliminarTodo = document.getElementById("boton-eliminar-todo");
const botonSubirArchivo = document.getElementById("boton-archivo");
const botonEliminarImagen = document.getElementById("boton-eliminar-img");
const paleta = document.getElementById('paleta');
const imgInput = document.querySelector('.img-input');

var contador = 0;
var coloresAgregados = new Set();
var pares = [];

// Llamar a la función para actualizar el color del círculo inicialmente
updateCircleColor();

// FUNCIONES-------------------------------------------------------------
// Función para actualizar el color del círculo
function updateCircleColor() {
    const colorValue = colorInput.value;

    // Validar si el valor es un color hexadecimal
    if (/^#([0-9A-F]{3}){1,2}$/i.test(colorValue)) {
        circle.style.backgroundColor = colorValue;
    } else {
        circle.style.backgroundColor = "#000"; // Restaurar color por defecto si el formato no es válido
    }
}

// Función para actualizar el color del círculo y el texto
function actualizarColor() {
    const colorSeleccionado = botonColorPicker.value; // Obtener el color seleccionado
    circle.style.backgroundColor = colorSeleccionado; // Actualizar el color del círculo
    colorInput.value = colorSeleccionado.toUpperCase(); // Actualizar el texto
}

// Función para activar el cuentagotas
function activarCuentagotas() {
    botonColorPicker.click(); // Simula un clic en el input de color
}

// Función para agregar un nuevo color
function agregarColor() {
    var colorValue = colorInput.value;

    // Verificar si el color ya ha sido agregado
    if (coloresAgregados.has(colorValue)) {
        alert('Este color ya ha sido agregado.');
        return;
    }

    // Añadir el nuevo color al conjunto de colores agregados
    coloresAgregados.add(colorValue);

    // Crear un nuevo elemento div con la clase .color
    var nuevoColor = document.createElement('div');
    nuevoColor.classList.add('color-paleta');

    // Contenido interno del nuevo color
    nuevoColor.innerHTML = `
        <p class="hex" id="hex${contador}">color</p>
        <div class="muestra-color"></div>
        <img src="imagenes/x.png" height="20px" class="eliminar" id="eliminar${contador}"></img>
    `;

    var hexParagraph = nuevoColor.querySelector('.hex');
    var muestraColorDiv = nuevoColor.querySelector('.muestra-color');
    hexParagraph.textContent = colorValue.toUpperCase();
    muestraColorDiv.style.backgroundColor = colorValue;

    // Agregar el nuevo color al contenedor de la paleta
    paleta.appendChild(nuevoColor);

    var eliminar = document.querySelector("#eliminar"+contador);

    // Event listener para el boton de eliminar
    eliminar.addEventListener("mousedown", function(event) {
        var imagen = document.getElementById(event.target.id);
        imagen.src = "imagenes/x_inv.png"; // Cambiar a la segunda imagen
    });
    eliminar.addEventListener("mouseup", function(event) {
        var imagen = document.getElementById(event.target.id);
        imagen.src = "imagenes/x.png"; // Cambiar a la primera imagen
    });
    eliminar.addEventListener("click", function(event) {
        var elementoPadre = event.target.parentElement;
        var id = event.target.id;
        var code = id[id.length - 1];
        var parrafo = document.getElementById("hex"+code);

        // En caso de que el parrafo no exista, no hace nada
        if (parrafo==null){
            console.log("Elemento no existe");
            return;
        }
        
        var color = parrafo.textContent;
        coloresAgregados.delete(color);
        elementoPadre.remove();
    });
    
    // Aumenta el contador
    contador++;
}

function actualizarContador() {
    var input = document.getElementById("textInput");
    var longitudActual = input.value.length;
    
    document.getElementById("contador").innerText = longitudActual + "/30";
}

// EVENTOS-------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function() {
    var input = document.getElementById("textInput");
    input.addEventListener("focus", function() {
        if (input.value === "Texto de ejemplo") {
            input.value = "";
        }
    });
    input.addEventListener("blur", function() {
        if (input.value === "") {
            input.value = "Texto de ejemplo";
        }
    });
});

// Agregar evento change al input de color
botonColorPicker.addEventListener("input", actualizarColor);

// Agregar evento al botón de cuentagotas
botonCuentagotas.addEventListener("click", activarCuentagotas);
circle.addEventListener("click", activarCuentagotas);

// Agregar evento para detectar cambios en el campo de texto
colorInput.addEventListener("input", updateCircleColor);

// Evento click para el botón de agregar color
botonAdd.addEventListener('click', agregarColor);

// Evento click para el boton de aceptar
botonAceptar.addEventListener('click', function(){
    if (!paleta.innerHTML){
        alert("Añade colores para empezar");
    }else if (coloresAgregados.size == 1){
        
        alert("Añade más de un color");

    }else{
        calculaContraste();
    }
    
});

// Evento click para el boton de eliminar todo
botonEliminarTodo.addEventListener('click', function(){
    document.getElementById('paleta').replaceChildren();
    document.getElementById('ratio').replaceChildren();
    coloresAgregados.clear();
    contador=0;
})

botonEliminarImagen.addEventListener('click', function(){
    img = document.querySelector(".img-input");
    img.innerHTML = "";
})

// Evento de clic al botón "Subir archivo"
botonSubirArchivo.addEventListener('click', function() { 
    // Crear un elemento de tipo input de archivo
    const inputArchivo = document.createElement('input');
    inputArchivo.type = 'file';
    inputArchivo.accept = "image/*";
  
    // Agregar un evento de cambio al input de archivo
    inputArchivo.addEventListener('change', function() {
        // Obtener el archivo seleccionado por el usuario
        const file = inputArchivo.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = 'Imagen seleccionada';
                img.style.maxWidth = '300px';
                img.style.maxHeight = '300px';

                imgInput.innerHTML = ''; // Limpiar contenido previo
                imgInput.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    });
    // Hacer clic en el input de archivo para abrir el diálogo de selección de archivo
    inputArchivo.click();
});

//====================================================================================//
//                              CALCULADORA DE CONTRASTE                              //
//====================================================================================//

function calculaContraste(){
    L = [];
    pares = [];
    coloresList = Array.from(coloresAgregados);
    
    for (const color of coloresAgregados){
        // Paso 1
        rgb = hexToRGB(color);
        rgb = rgb.map(elemento => elemento/255);

        // Paso 2 + Paso 3
        for (i=0;i<3;i++){
            if (rgb[i]<=0.03928){
                rgb[i] /= 12.92
            }else{
                rgb[i] = ((rgb[i]+0.055)/1.055)**2.4
            }
        }

        // Paso 4
        l = rgb[0]*0.2126 + rgb[1]*0.7152 + rgb[2]*0.0722;
        L.push(l);
    }

    let ratios = [];
    for (let i=0;i<L.length;i++){
        for(let j=i+1;j<L.length;j++){
            ratio = (L[i]+0.05)/(L[j]+0.05)
            if (ratio>1/ratio){
                ratios.push(ratio);
            }else{
                ratios.push(1/ratio);
            }
            pares.push(coloresList[i]+"----"+coloresList[j])
        }
        
    }
    mostrarResultado(ratios);
}

function hexToRGB(hex){
    // Eliminar el '#' del inicio, si está presente
    hex = hex.replace(/^#/, '');

    // Separar el código hexadecimal en componentes (RRGGBB)
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);

    // Devolver el color RGB en formato string
    return [r,g,b];
}

function mostrarResultado(ratios) {
    let resultadoDiv = document.getElementById("ratio");
    resultadoDiv.innerHTML=" ";
    text = document.getElementById("textInput").value;

    for (let i=0;i<ratios.length;i++){
        // Crear un nuevo elemento div con la clase .cajaRatio
        var divRatio = document.createElement('div');
        divRatio.classList.add('cajaRatio');
        divRatio.setAttribute('id','cajaRatio'+i);
        divRatio.style.width = "100%";

        // Contenido interno del nuevo color
        divRatio.innerHTML = `
        <div class="color-contraste" id="contraste-${i}">
            <p class="inner-text"></p>
            <div class="boton" id="shuffle-${i}">
                <button class="shuffle" id="btn-shuffle-${i}">
                    <img src="imagenes/shuffle.png" id="img-shuffle-${i}">
                </button>
            </div>
        </div>
        <p id="texto-ratio-${i}"></p>
        <img height="20px" id="img-ratio-${i}">
        `;

        resultadoDiv.appendChild(divRatio);

        textoRatio = document.getElementById("texto-ratio-"+i);
        textoRatio.innerHTML = ratios[i].toFixed(2);

        divContraste = document.getElementById("contraste-"+i);
        divContraste.style.backgroundColor = pares[i].split("----")[0];
        divContraste.style.color = pares[i].split("----")[1];

        imgRatio = document.getElementById("img-ratio-"+i);
        if (ratios[i] < 4.5){
            imgRatio.setAttribute('src',"imagenes/forbidden.png");
        }else{
            imgRatio.setAttribute('src',"imagenes/check.png");
        }
        
    }
    const innerText = document.querySelectorAll(".inner-text");
    innerText.forEach(function(element){
        console.log(1)
        element.innerHTML = text;
    });

    shuffle();
}

function shuffle(){
    const botonesShuffle = document.querySelectorAll(".shuffle");

    // Iterar sobre cada elemento y agregar el event listener
    botonesShuffle.forEach(function(elemento) {
        elemento.addEventListener("click", function(event) {
            var id = event.target.id;
            var code = id[id.length - 1];
            var element = document.getElementById("contraste-"+code);

            var currentBackgroundColor = element.style.backgroundColor;
            var currentColor = element.style.color;

            element.style.backgroundColor = currentColor;
            element.style.color = currentBackgroundColor;

        });
    });
}