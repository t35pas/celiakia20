let speech = window.speechSynthesis;

// Set Speech Language
speech.lang = "es";


var id_anterior = 1;

speech.onend = function () {
    speech.cancel();
    console.log(speaking);
    console.log(id_anterior);
    var x = document.getElementById('pausa'+ id_anterior);
    var y = document.getElementById('play'+ id_anterior);
    if (y.style.display === "none") {
        y.style.display = "block";
        x.style.display = "none";
    }

}

function Play(id_play){
    var id_pausa = 'pausa'+ id_play.substring(4)
    var id_text = 'paso'+ id_play.substring(4)
    var text = document.getElementById(id_text);
    var x = document.getElementById(id_pausa);
    var y = document.getElementById(id_play);

    if (id_anterior != id_play.substring(4)){
        speech.cancel();
        var x_anterior = document.getElementById('pausa'+ id_anterior);
        var y_anterior = document.getElementById('play'+ id_anterior);
        if (y_anterior.style.display === "none") {
            y_anterior.style.display = "block";
            x_anterior.style.display = "none";
        }
    }
    console.log(speech.speaking)
    if (speech.speaking) {
        speech.resume();

        let timer

        speech.onstart = () => {
        resumeInfinity(speech)
        }

        const clear = () => {  clearTimeout(timer) }

        speech.onerror = clear

        const resumeInfinity = (target) => {
        // prevent memory-leak in case speech is deleted, while this is ongoing
        if (!target && timer) { return clear() }

        speechSynthesis.pause()
        speechSynthesis.resume()

        timer = setTimeout(function () {
            resumeInfinity(target)
        }, 5000)
        }


      } else {      
        console.log(speech)
        let texto = new SpeechSynthesisUtterance(text.textContent)
        speech.speak(texto);
        
      } 
      if (x.style.display === "none") {
          x.style.display = "block";
          y.style.display = "none";
      }
      console.log("Cambio el anterior por el nuevo")
      console.log(id_play.substring(4))
      id_anterior = id_play.substring(4);
    
    }
function Pausa(id_pausa){
    let id_play = 'play' + id_pausa.substring(5)
    var x = document.getElementById(id_pausa);
    var y = document.getElementById(id_play);
    speech.pause();
    if (y.style.display === "none") {
        y.style.display = "block";
        x.style.display = "none";
    }
}
    
function Stop(id_stop) {
    var id_play = 'play' + id_stop.substring(4)
    var id_pausa = 'pausa' + id_stop.substring(4)
    
    var x = document.getElementById(id_pausa);
    var y = document.getElementById(id_play);
    
    if (id_anterior != id_stop.substring(4)) {
        speech.cancel();
        speaking = 0;
        var x_anterior = document.getElementById('pausa'+ id_anterior);
        var y_anterior = document.getElementById('play'+ id_anterior);
        if (y_anterior.style.display === "none") {
            y_anterior.style.display = "block";
            x_anterior.style.display = "none";
        }
    }
    speech.cancel();
    speaking = 0;
    if (y.style.display === "none") {
        y.style.display = "block";
        x.style.display = "none";
    } 
    }

    