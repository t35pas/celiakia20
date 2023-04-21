$(document).ready(function () {
    $("#table_listadoRecetas").DataTable({
      autoWidth: true,
      language: {
        lengthMenu: "Mostrar _MENU_ Recetas por página",
        zeroRecords: "¡No existen recetas!",
        info: "Mostrando página _PAGE_ de _PAGES_",
        infoEmpty: "No se encontraron resultados",
        search: "Buscar:",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        paginate: {
          first: "Primero",
          last: "Último",
          next: "Siguiente",
          previous: "Anterior",
        },
        infoFiltered: "(Filtrado de _MAX_ recetas totales)",
      },
    });
  });

  $(document).ready(function () {
    $("#table_listadoIngredientes").DataTable({
      autoWidth: true,
      language: {
        lengthMenu: "Mostrar _MENU_ Ingredientes por página",
        zeroRecords: "No Existe ese ingrediente",
        info: "Mostrando página _PAGE_ de _PAGES_",
        infoEmpty: "No se encontraron resultados",
        search: "Buscar:",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        paginate: {
          first: "Primero",
          last: "Último",
          next: "Siguiente",
          previous: "Anterior",
        },
        infoFiltered: "(Filtrado de _MAX_ ingredientes totales)",
      },
    });
  });

  $(document).ready(function () {
    $("#table_listadoPreparacion").DataTable({
      autoWidth: true,
      language: {
        lengthMenu: "Mostrar _MENU_ Pasos por página",
        zeroRecords: "No existe ese paso",
        info: "Mostrando página _PAGE_ de _PAGES_",
        infoEmpty: "No se encontraron resultados",
        search: "Buscar:",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        paginate: {
          first: "Primero",
          last: "Último",
          next: "Siguiente",
          previous: "Anterior",
        },
        infoFiltered: "(Filtrado de _MAX_ pasos totales)",
      },
    });
  });