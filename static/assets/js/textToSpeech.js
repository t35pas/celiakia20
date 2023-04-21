let speech = window.speechSynthesis;

// Set Speech Language
speech.lang = "es";


var id_anterior = 1;



function Play(id_play){

    var reproduce = document.getElementById(id_play);
    var resetea = document.getElementById(id_play);

    var id_text = 'paso'+ id_play.substring(4)
    var text = document.getElementById(id_text);
    
    if (id_anterior != id_play.substring(4)){
        speech.cancel();
        var reproduce_anterior = document.getElementById('play'+ id_anterior);
        var resetea_anterior = document.getElementById('stop'+ id_anterior);
        resetea_anterior.style.display = "block";
        reproduce_anterior.style.display = "block";
    } else {
        let texto = new SpeechSynthesisUtterance(text.textContent)

        texto.onend = function () {
            speech.cancel();
            var reproduce = document.getElementById('play'+ id_anterior);
            var resetea = document.getElementById('stop'+ id_anterior);
            reproduce.style.display = "block";
            resetea.style.display = "block";
        }
        speech.speak(texto);
        reproduce.style.display = "none";
    }

    id_anterior = id_play.substring(4);
    
}
    
function Stop(id_stop) {
    var id_play = 'play' + id_stop.substring(4)
    
    var reproduce = document.getElementById(id_play);
    var resetea = document.getElementById(id_stop);

    
    if (id_anterior != id_stop.substring(4)) {
        speech.cancel();
        var reproduce_anterior = document.getElementById('play'+ id_anterior);
        var resetea_anterior = document.getElementById('stop'+ id_anterior);
        reproduce_anterior.style.display = "block";
        resetea_anterior.style.display = "block";
        
    }
    speech.cancel();
    reproduce.style.display = "block";
    resetea.style.display = "block";    
}

function Leer_Escuchar(totalPasos){
    let total = totalPasos.substring(13);
    for (i=1;i<=total;i++) {
      var id_escuchar = "escuchar" + i;
      var x = document.getElementById(id_escuchar);
      if (x.style.display === "none") {
          x.style.display = "block";
      } else {
          x.style.display = "none";
      }
    }  
  }
    