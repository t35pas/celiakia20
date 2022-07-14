$(document).ready(function() {
    $('#listadoRecetas').DataTable({
        "autoWidth": true,
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