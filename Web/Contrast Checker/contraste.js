function calculaContraste(colores){
    L = [];
    for (const color of colores){
        // Paso 1
        rgb = hexToRGB(color);
        rgb = rgb.map(elemento => elemento/255);
        console.log(rgb)

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

    const ul = document.createElement("ul");

    for (let i=0;i<ratios.length;i++){
        const li = document.createElement("li");
        li.textContent = "Ratio "+ratios[i];
        ul.appendChild(li);
    }

    resultadoDiv.appendChild(ul);
}

document.addEventListener("DOMContentLoaded", function() {
    var col = [["#000000","#FFFFFF"],["#000000","#ABB123"],["#FFFFFF","#ABB123"]];
    var colores = ["#000000","#FFFFFF","#ABB123"];
    calculaContraste(colores);
});
