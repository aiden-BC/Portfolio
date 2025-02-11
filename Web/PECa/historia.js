function redireccionar(destino) {
    window.location.href = destino;
}

window.addEventListener('load', function() {
    var fadeImage = document.getElementById('fadeImage');
    fadeImage.style.display = 'block';
  
    var opacity = 0;
    var timer = setInterval(function() {
      if (opacity >= 1) {
        clearInterval(timer);
      }
      fadeImage.style.opacity = opacity;
      opacity += 0.01;
    }, 10);
  });

  function scrollAnimation() {
    const headerContent = document.querySelector('header');
    const headerPosition = headerContent.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;
  
    if (headerPosition < windowHeight - 50) {
      headerContent.classList.add('show');
    } else {
      headerContent.classList.remove('show');
    }
  }
  
  window.addEventListener('scroll', scrollAnimation);