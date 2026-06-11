<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Auth;

class DashboardController extends Controller
{
    public function administrador()
    {
        $user = Auth::user();
        if ($user->Rol !== 'Administrador') {
            abort(403, 'Acción no autorizada');
        }
        return view('administrador.dashboard');
    }

    public function empleado()
    {
        $user = Auth::user();
        if ($user->Rol !== 'Empleado') {
            abort(403, 'Acción no autorizada');
        }
        return view('empleado.dashboard');
    }
}
