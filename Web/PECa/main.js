const checkboxes = document.querySelectorAll('.checkbox-input');

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        // Desmarcar todas las casillas de verificación excepto la actualmente seleccionada
        checkboxes.forEach(cb => {
            if (cb !== this) {
                cb.checked = false;
            }
        });
    });
});

// Capturar el elemento del botón "Subir archivo"
const botonSubirArchivo = document.getElementById('botonSubirArchivo');

// Elemento y contexto de audio
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const audio = new Audio();
const source = audioContext.createMediaElementSource(audio);

// Variables para el audio y la respuesta al impulso (IR)
let audioBuffer;
let buffers = {}; // Objeto para almacenar los buffers de respuesta al impulso
let efectos = ["backwards","chorus","reverb","robot","telephone","wildecho"] // Listado de efectos

// Llamar a la función para cargar la respuesta al impulso cuando se carga la página
window.addEventListener('DOMContentLoaded', () => {
  let i = 0;
  for (efecto of efectos){
    cargarIR("sonido/" + efecto + ".wav", i);
    i++;
  }
});
console.log(buffers);

botonSubirArchivo.addEventListener('click', function() { // evento de clic al botón "Subir archivo"
  // Crear un elemento de tipo input de archivo
  const inputArchivo = document.createElement('input');
  inputArchivo.type = 'file';

  // Agregar un evento de cambio al input de archivo
  inputArchivo.addEventListener('change', function() {
    // Obtener el archivo seleccionado por el usuario
    const archivoSeleccionado = inputArchivo.files[0];

    // Actualizar el texto del elemento con el nombre del archivo seleccionado
    const nombreArchivo = document.querySelector('.rectangulo').firstChild;
    nombreArchivo.textContent = archivoSeleccionado.name;

    // Crear una URL del objeto Blob del archivo seleccionado
    const url = URL.createObjectURL(archivoSeleccionado);

    // Eliminamos el audio que ya estaba cargado para cargar el nuevo
    audio.remove();
    audio.src = url;
  });
// Hacer clic en el input de archivo para abrir el diálogo de selección de archivo
inputArchivo.click();
});

// Agregar el evento de clic al botón "Empezar"
document.querySelector('.empezar').addEventListener('click', () => {
  if (audioContext.state === 'suspended') {audioContext.resume()}

  // Reproducir el audio
  aplicarEfectosSegunEstado();
  audio.play();
});

// Agregar el evento de clic al botón "Detener"
document.querySelector('.detener').addEventListener('click', () => {
  // Reproducir el audio
  audio.pause();
});

// Función para cargar los archivos de respuesta al impulso (IR)
function cargarIR(url, key) {
  fetch(url)
    .then(response => response.arrayBuffer())
    .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
    .then(buffer => {
      // Almacenar el buffer con la clave correcta
      buffers[key] = buffer;
    })
    .catch(error => console.error('Error al cargar el archivo de respuesta al impulso:', error));
}

// Función para aplicar el efecto (convolución)
function convolver(key) {
  var convolverNode = audioContext.createConvolver();
  console.log(efectos.indexOf(key));
  convolverNode.buffer = buffers[efectos.indexOf(key)];

  var gainNode = audioContext.createGain();
  gainNode.gain.value = 1; // Ajusta el valor del ganancia según sea necesario

  // Conectar los nodos
  source.disconnect(); // Desconectar el audio original
  source.connect(convolverNode);
  convolverNode.connect(gainNode);
  gainNode.connect(audioContext.destination);
}

// Función para cambiar la velocidad del audio
function velocidad() {
  // Obtener los valores de los sliders
  const velocidad = parseFloat(pitchSlider.value);
  let pitchCheckbox = document.getElementById('pitch');

  audio.playbackRate = velocidad;

  if (pitchCheckbox.checked){
    audio.preservesPitch = true;
  }else{
    audio.preservesPitch = false;
  }
}

function pasoBanda(){
  // Crear un nodo de filtro paso banda
  const filtroPasoBanda = audioContext.createBiquadFilter();
  filtroPasoBanda.type = 'bandpass'; // Establecer el tipo de filtro

  // Obtener los valores de los sliders
  const minFreq = parseFloat(limiteInferiorSlider.value);
  const maxFreq = parseFloat(limiteSuperiorSlider.value);

  // Calcular parametros
  const frecCentral = Math.round((minFreq + maxFreq) / 2); // Frecuencia central
  const anchoBanda = maxFreq-minFreq; // Factor de calidad
  
  // Establecer frecuencia y calidad del filtro
  filtroPasoBanda.frequency.value = frecCentral; 
  filtroPasoBanda.Q.value = frecCentral/anchoBanda; 

  // Conectar los nodos
  source.disconnect(); // Desconectar el audio original
  source.connect(filtroPasoBanda); // Conectar el audio original al nodo del filtro
  filtroPasoBanda.connect(audioContext.destination); // Conectar el filtro al destino principal
}

function tremolo() {
  // Crear un nodo de oscilador para modular la amplitud
  const oscilador = audioContext.createOscillator();
  const gananciaModuladora = audioContext.createGain();

  // Obtener los valores de los sliders
  const frecuencia = parseFloat(frecuenciaModulacionSlider.value);
  const profundidad = parseFloat(amplitudModulacionSlider.value);

  // Establecer la frecuencia del oscilador
  oscilador.frequency.value = frecuencia;

  // Conectar el oscilador a la ganancia moduladora
  oscilador.connect(gananciaModuladora.gain);

  // Establecer la amplitud de la modulación
  gananciaModuladora.gain.value = profundidad;

  // Conectar los nodos
  // Conectar los nodos
  source.disconnect(); // Desconectar el audio original
  gananciaModuladora.connect(audioContext.destination); // Conectar la ganancia moduladora al destino principal
  source.connect(gananciaModuladora); // Conectar el audio original a la ganancia moduladora

  oscilador.start(); // Iniciar el oscilador

  // Modificar la velocidad del audio para aplicar el efecto de trémolo
  audio.playbackRate = 1 - profundidad; // Reducir la velocidad del audio según la profundidad del trémolo
}

function eco() {
  // Crear un nodo de efecto de eco
  const nodoEco = audioContext.createDelay();
  const gananciaEco = audioContext.createGain();

  // Obtener los valores de los sliders
  const retardoValue = parseFloat(retardoSlider.value);
  const amplitudValue = parseFloat(amplitudSlider.value);

  // Establecer el retardo y la amplitud del eco
  nodoEco.delayTime.value = retardoValue;
  gananciaEco.gain.value = amplitudValue;

  // Conectar los nodos
  source.disconnect(); // Desconectar el audio original
  source.connect(audioContext.destination); // Conectar el audio original al destino principal
  source.connect(nodoEco); // Conectar el audio original al nodo de eco
  nodoEco.connect(gananciaEco); // Conectar el nodo de eco al nodo de ganancia
  gananciaEco.connect(audioContext.destination); // Conectar el nodo de ganancia al destino principal
}

function vibrato() {
  let delay = new DelayNode(audioContext,{delayTime:0.1,maxDelayTime:10});
  let LFOGain = new GainNode(audioContext,{gain:0});
  let LFO = new OscillatorNode(audioContext,{frequency:5});
  LFO.start();
  source.connect(delay);
  LFO.connect(LFOGain).connect(delay.delayTime);
  delay.connect(audioContext.destination);

  LFO.frequency.value = frecuenciaModulacionSliderVibrato.value;
  LFOGain.gain.value = amplitudModulacionSliderVibrato.value/(2*Math.PI*frecuenciaModulacionSliderVibrato.value);
}

function verificarCambiosEnCheckbox_Sliders() {
  const checkboxes = document.querySelectorAll('.checkbox-input');

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      aplicarEfectosSegunEstado();
    });
  });

  // Verificar cambios en los sliders
  const sliders = document.querySelectorAll('.slider');
  
  sliders.forEach(slider => {
    slider.addEventListener('input', () => {
      aplicarEfectosSegunEstado();
    });
  });
}

function aplicarEfectosSegunEstado() {
  const efectos = [
    { checkbox: 'paso-banda', efecto: pasoBanda },
    { checkbox: 'eco', efecto: eco },
    { checkbox: 'Tremolo', efecto: tremolo },
    {
      checkbox: 'Vibrato', efecto: () => {
        source.disconnect();
        vibrato(audioContext, source, frecuenciaModulacionSliderVibrato.value, amplitudModulacionSliderVibrato.value, 44100);
      }
    },
    { checkbox: 'backwards', efecto: () => convolver('backwards') },
    { checkbox: 'chorus', efecto: () => convolver('chorus') },
    { checkbox: 'reverb', efecto: () => convolver('reverb') },
    { checkbox: 'robot', efecto: () => convolver('robot') },
    { checkbox: 'telephone', efecto: () => convolver('telephone') },
    { checkbox: 'wildecho', efecto: () => convolver('wildecho') }
  ];

  let efectoAplicado = false;

  for (const { checkbox, efecto } of efectos) {
    const element = document.getElementById(checkbox);
    if (element && element.checked) {
      efecto();
      efectoAplicado = true;
      break;
    }
  }

  if (!efectoAplicado) {
    source.disconnect();
    source.connect(audioContext.destination);
  }

  velocidad();
}

// Capturar el slider de  pitch 
const pitchSlider = document.getElementById('pitchSlider');
// Capturar el slider de retardo y sus números correspondientes
const pitchValor = document.getElementById('pitchValor');
// Actualizar el número mostrado al lado del slider mientras se mueve
pitchSlider.addEventListener('input', function() {
  pitchValor.textContent = pitchSlider.value;
});


// Capturar los sliders de Frecuencia modulacion vibrato y Amplitud modulacion vibrato
const frecuenciaModulacionSliderVibrato = document.getElementById('frecuenciaModulacionSliderVibrato');
const amplitudModulacionSliderVibrato = document.getElementById('amplitudModulacionSliderVibrato');
// Capturar los sliders de retardo y amplitud y sus números correspondientes
const frecuenciaModulacionValorVibrato = document.getElementById('frecuenciaModulacionValorVibrato');
const amplitudModulacionValorVibrato = document.getElementById('amplitudModulacionValorVibrato');
// Actualizar el número mostrado al lado del slider mientras se mueve
frecuenciaModulacionSliderVibrato.addEventListener('input', function() {
  frecuenciaModulacionValorVibrato.textContent = frecuenciaModulacionSliderVibrato.value;
});
amplitudModulacionSliderVibrato.addEventListener('input', function() {
  amplitudModulacionValorVibrato.textContent = amplitudModulacionSliderVibrato.value;
});


// Capturar los sliders de Limite inferior y Limite superior
const limiteInferiorSlider = document.getElementById('limiteInferiorSlider');
const limiteSuperiorSlider = document.getElementById('limiteSuperiorSlider');
// Capturar los sliders de Limite inferior y Limite superior y sus números correspondientes
const limiteInferiorValor = document.getElementById('limiteInferiorValor');
const limiteSuperiorValor = document.getElementById('limiteSuperiorValor');
// Actualizar el número mostrado al lado del slider mientras se mueve
limiteInferiorSlider.addEventListener('input', function() {
  limiteInferiorValor.textContent = limiteInferiorSlider.value;
});
limiteSuperiorSlider.addEventListener('input', function() {
  limiteSuperiorValor.textContent = limiteSuperiorSlider.value;
});


// Capturar los sliders de retardo y amplitud
const retardoSlider = document.getElementById('retardoSlider');
const amplitudSlider = document.getElementById('amplitudSlider');
// Capturar los sliders de retardo y amplitud y sus números correspondientes
const retardoValor = document.getElementById('retardoValor');
const amplitudValor = document.getElementById('amplitudValor');
// Actualizar el número mostrado al lado del slider mientras se mueve
retardoSlider.addEventListener('input', function() {
  retardoValor.textContent = retardoSlider.value;
});
amplitudSlider.addEventListener('input', function() {
  amplitudValor.textContent = amplitudSlider.value;
});


// Capturar los sliders de Frecuencia modulacion y Amplitud modulacion
const frecuenciaModulacionSlider = document.getElementById('frecuenciaModulacionSlider');
const amplitudModulacionSlider = document.getElementById('amplitudModulacionSlider');
// Capturar los sliders de Frecuencia modulacion y Amplitud modulacion y sus números correspondientes
const frecuenciaModulacionValor = document.getElementById('frecuenciaModulacionValor');
const amplitudModulacionValor = document.getElementById('amplitudModulacionValor');
// Actualizar el número mostrado al lado del slider mientras se mueve
frecuenciaModulacionSlider.addEventListener('input', function() {
  frecuenciaModulacionValor.textContent = frecuenciaModulacionSlider.value;
});
amplitudModulacionSlider.addEventListener('input', function() {
  amplitudModulacionValor.textContent = amplitudModulacionSlider.value;
});


// Llamar a la función para verificar cambios en las casillas de verificación
verificarCambiosEnCheckbox_Sliders();