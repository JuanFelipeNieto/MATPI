
<?php

use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\PerfilController;
use App\Http\Controllers\EmpleadoController;
use App\Http\Controllers\UsuarioController;
use App\Http\Controllers\ClienteController;
use App\Http\Controllers\ReservaController;
use App\Http\Controllers\MateriaPrimaController;
use App\Http\Controllers\ProductoController;
use App\Http\Controllers\ProveedorController;
use App\Http\Controllers\PedidoController;


use Illuminate\Support\Facades\Route;

//Mostrar formulario login
Route::get('/', [LoginController::class, 'showLoginForm'])->name('login');

//Proceso de login
Route::post('/login', [LoginController::class, 'login'])->name('login.post');

//Logout
Route::post('/logout', [LoginController::class, 'logout'])->name('logout');

//Rutas protegidas por autenticación
Route::middleware(['auth'])->group(function () {

    Route::get('/administrador/dashboard', [DashboardController::class, 'administrador'])
        ->name('administrador.dashboard');

    Route::get('/empleado/dashboard', [DashboardController::class, 'empleado'])
        ->name('empleado.dashboard');


    Route::prefix('administrador/perfil')->name('administrador.perfil')->group(function () {
        Route::get('/', [PerfilController::class, 'index']);
        Route::get('/editar', [PerfilController::class, 'edit'])->name('.editar');
        Route::put('/', [PerfilController::class, 'update'])->name('.update');

        // 🔑 Cambio de contraseña
        Route::get('/password', [PerfilController::class, 'editPassword'])->name('.password.edit');
        Route::put('/password', [PerfilController::class, 'updatePassword'])->name('.password.update');
    });

    Route::prefix('empleado/perfil')->name('empleado.perfil')->group(function () {
        Route::get('/', [PerfilController::class, 'perfilEmpleado']);
        Route::get('/password', [PerfilController::class, 'editPasswordEmpleado'])->name('.password.edit');
        Route::put('/password', [PerfilController::class, 'updatePasswordEmpleado'])->name('.password.update');
    });

    Route::prefix('administrador')->name('administrador.')->group(function () {
        Route::resource('empleados', EmpleadoController::class);
    });

    Route::resource('usuarios', UsuarioController::class);

    Route::resource('clientes', ClienteController::class)->except(['show']);

    Route::prefix('administrador')->name('administrador.')->group(function () {
        Route::view('/productos', 'administrador.productos.index')->name('productos.index');
        Route::view('/pedidos', 'administrador.pedidos.index')->name('pedidos.index');
        Route::view('/proveedores', 'administrador.proveedores.index')->name('proveedores.index');
        Route::view('/materia-prima', 'administrador.materiaPrima.index')->name('materiaPrima.index');
        Route::view('/reportes', 'administrador.reportes.index')->name('reportes.index');
        Route::view('/facturas', 'administrador.facturas.index')->name('facturas.index');
    });

Route::resource('reservas', ReservaController::class);


Route::resource('materia_prima', MateriaPrimaController::class);


Route::resource('producto', ProductoController::class);

Route::resource('proveedor', ProveedorController::class);


Route::resource('pedido', PedidoController::class);

Route::get('/empleados/reporte', [EmpleadoController::class, 'reportePDF'])
    ->name('administrador.empleados.reporte');


Route::get('materia-prima/reporte', [MateriaPrimaController::class, 'reportePDF'])
    ->name('materia_prima.reporte');


});
