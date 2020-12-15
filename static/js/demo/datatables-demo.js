// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable({
    responsive: true,
    language: {
        "processing": "Procesando...",
        "lengthMenu": "Mostrar _MENU_ ",
        "zeroRecords": "No se encontraron resultados",
        "emptyTable": "Ninguna resultado disponible en esta tabla",
        "info": "Mostrando del _START_ al _END_ de un total de _TOTAL_ ",
        "infoEmpty": "Mostrando del 0 al 0 de un total de 0 ",
        "infoFiltered": "(filtrado de un total de _MAX_ )",
        "search": "Buscar:",
        "infoThousands": ",",
        "loadingRecords": "Cargando...",
        "paginate": {
            "first": "Primero",
            "last": "Último",
            "next": "Siguiente",
            "previous": "Anterior"
        }
    } 
  })
});