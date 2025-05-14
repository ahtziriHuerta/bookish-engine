document.querySelector("form").addEventListener("submit", function (e) {
    if (!confirm("¿Estás seguro que deseas eliminar este proveedor?")) {
        e.preventDefault();
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const botonesEliminar = document.querySelectorAll('.confirmar-eliminar');

    botonesEliminar.forEach(btn => {
        btn.addEventListener('click', function (e) {
            const confirmar = confirm("¿Estás seguro que deseas eliminar este proveedor?");
            if (!confirmar) {
                e.preventDefault();
            }
        });
    });
});
