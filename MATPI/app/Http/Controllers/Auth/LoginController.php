<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class LoginController extends Controller
{
    // Mostrar formulario de login
    public function showLoginForm()
    {
        return view('auth.login'); 
    }

    // Procesar login
public function login(Request $request)
{
   $request->validate([
    'ID' => 'required',
    'password' => 'required',
], [
    'ID.required' => '⚠️ El campo usuario es obligatorio.',
    'password.required' => '⚠️ Por favor, ingresa tu contraseña.',
]);

    if (Auth::attempt(['ID' => $request->ID, 'password' => $request->password], $request->filled('remember'))) {
        $request->session()->regenerate();

        $user = Auth::user();

        if ($user->Rol === 'Administrador') {
            return redirect()->intended('/administrador/dashboard');
        } elseif ($user->Rol === 'Empleado') {
            return redirect()->intended('/empleado/dashboard');
        } else {
            Auth::logout();
            return back()->withErrors([
                'ID' => 'No tienes permiso para acceder.',
            ]);
        }
    }

    return back()->withErrors([
        'ID' => 'Las credenciales no coinciden con nuestros registros.',
    ])->onlyInput('ID');
}



    // Cerrar sesión
    public function logout(Request $request)
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect('/');
    }
}
