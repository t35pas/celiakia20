$(document).ready(function() {
    $('#listadoRecetas').DataTable({
        "language": {
            "lengthMenu": "Mostrar _MENU_ Recetas por página",
            "zeroRecords": "¡No existen recetas!",
            "info": "Mostrando página _PAGE_ de _PAGES_",
            "infoEmpty": "No se encontraron resultados",
            "search":"Buscar:",
            "loadingRecords": "Cargando...",
            "processing":"Procesando...",
            "paginate": {
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior"
            },
            "infoFiltered": "(Filtrado de _MAX_ recetas totales)"
        }
    });
});

$(document).ready(function() {
    $('#listadoIngEnRecetas').DataTable({
        "language": {
            "lengthMenu": "Mostrar _MENU_ Ingredientes por página",
            "zeroRecords": "¡No agregaste ingredientes aún!",
            "info": "Mostrando página _PAGE_ de _PAGES_",
            "infoEmpty": "No se encontraron ingredientes",
            "search":"Buscar:",
            "loadingRecords": "Cargando...",
            "processing":"Procesando...",
            "paginate": {
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior"
            },
            "infoFiltered": "(Filtrado de _MAX_ ingredientes totales)"
        }
    });
});

$(document).ready(function() {
    $('table.display').DataTable({
        "language": {
            "lengthMenu": "Mostrar _MENU_ Ingredientes por página",
            "zeroRecords": "¡No agregaste ingredientes aún!",
            "info": "Mostrando página _PAGE_ de _PAGES_",
            "infoEmpty": "No se encontraron ingredientes",
            "search":"Buscar:",
            "loadingRecords": "Cargando...",
            "processing":"Procesando...",
            "paginate": {
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior"
            },
            "infoFiltered": "(Filtrado de _MAX_ ingredientes totales)"
        }
    });
});

$(document).ready(function() {
    $('#listadoPreparacion').DataTable({
        "language": {
            "lengthMenu": "Mostrar _MENU_ Pasos por página",
            "zeroRecords": "¡No agregaste pasos aún!",
            "info": "Mostrando página _PAGE_ de _PAGES_",
            "infoEmpty": "No se encontraron pasos",
            "search":"Buscar:",
            "loadingRecords": "Cargando...",
            "processing":"Procesando...",
            "paginate": {
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior"
            },
            "infoFiltered": "(Filtrado de _MAX_ pasos totales)"
        },
        "columnDefs": [{
            "width": "10px",
            "targets": 0
          },
          {
            "width": "250px",
            "targets": 1
          },
          {
            "width": "50px",
            "targets": 2,
            "orderable": "false"
          }]
    });
});


var dropdown = document.getElementsByClassName("dropdown-btn");
var i;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener("click", function() {
  this.classList.toggle("active-dropdown");
  var dropdownContent = this.nextElementSibling;
  if (dropdownContent.style.display === "block") {
  dropdownContent.style.display = "none";
  } else {
  dropdownContent.style.display = "block";
  }
  });
}

window.onload = function() {

    var existe = document.getElementById('existe');
    var noExiste = document.getElementById('noExiste');

    existe.onclick = mostrar;
    noExiste.onclick = ocultar;

    }
 
    function mostrar() {
            var x = document.getElementById("nombreImagen");
            var y = document.getElementById("imagenIngrediente");
            var z = document.getElementById("nombreIngrediente");
            var w = document.getElementById("elegirNombreIngrediente");

                if (x.style.display === "none") {
                    x.style.display = "block";
                }
                if (y.style.display === "none") {
                    y.style.display = "block";
                }
                if (z.style.display === "none") {
                    z.style.display = "block";
                    w.style.display = "none";
                }
    }

    function ocultar() {
            var x = document.getElementById("nombreImagen");
            var y = document.getElementById("imagenIngrediente");
            var z = document.getElementById("nombreIngrediente");
            var w = document.getElementById("elegirNombreIngrediente");

                if (x.style.display === "block") {
                    x.style.display = "none";
                }
                if (y.style.display === "block") {
                    y.style.display = "none";
                }
                if (z.style.display === "block") {
                    z.style.display = "none";
                    w.style.display = "block";
                }
    }
    