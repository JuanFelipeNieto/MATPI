<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;

class PerfilController extends Controller
{
    /**
     * Mostrar la información del perfil del administrador autenticado.
     */
    public function index()
    {
        $administrador = Auth::user()->administrador;
        $administrador->load('usuario');
        return view('administrador.perfil.index', compact('administrador'));
    }

    /**
     * Mostrar el formulario para editar el perfil del administrador autenticado.
     */
    public function edit()
    {
        $administrador = Auth::user()->administrador;
        $administrador->load('usuario');
        return view('administrador.perfil.edit', compact('administrador'));
    }

    /**
     * Actualizar la información del perfil del administrador autenticado.
     */
    public function update(Request $request)
    {
        $usuario = Auth::user();
        $administrador = $usuario->administrador;

        $validatedUsuario = $request->validate([
            'Telefono' => 'nullable|string|max:20',
            'Correo_Electronico' => ['required', 'email', Rule::unique('Usuario', 'Correo_Electronico')->ignore($usuario->ID, 'ID')],
            'Fecha_Nacimiento' => 'nullable|date',
            'Nombre_Completo' => 'required|string|max:255',
            'Estado' => 'nullable|string|max:50',
            'Direccion' => 'nullable|string|max:255',
            'Fecha_ingreso' => 'nullable|date',
            'Experiencia_Laboral' => 'nullable|string',
        ]);

        $usuario->update($validatedUsuario);

        $validatedAdmin = $request->validate([
            'Formacion_Educativa' => 'nullable|string|max:255',
        ]);

        $administrador->update($validatedAdmin);

        return redirect()->route('administrador.perfil')->with('success', 'Perfil actualizado correctamente.');
    }

    /**
     * Mostrar formulario de cambio de contraseña para administrador.
     */
    public function editPassword()
    {
        return view('administrador.perfil.password');
    }

    /**
     * Actualizar la contraseña del administrador autenticado.
     */
    public function updatePassword(Request $request)
    {
        $request->validate([
            'password_actual' => 'required',
            'password' => 'required|min:8|confirmed',
        ]);

        $usuario = Auth::user();

        if (!Hash::check($request->password_actual, $usuario->Contraseña)) {
            return back()->withErrors(['password_actual' => 'La contraseña actual no es correcta.']);
        }

        $usuario->Contraseña = Hash::make($request->password);
        $usuario->save();

        return redirect()->route('administrador.perfil')->with('success', 'Contraseña actualizada correctamente.');
    }

    // ============================================================
    // =================== MÉTODOS PARA EMPLEADO ==================
    // ============================================================

    /**
     * Mostrar la información del perfil del empleado autenticado.
     */
    public function perfilEmpleado()
    {
        $empleado = Auth::user()->empleado;
        $empleado->load('usuario');
        return view('empleado.perfil.index', compact('empleado'));
    }

    /**
     * Mostrar el formulario para editar el perfil del empleado autenticado.
     */
    public function editEmpleado()
    {
        $empleado = Auth::user()->empleado;
        $empleado->load('usuario');
        return view('empleado.perfil.edit', compact('empleado'));
    }

    /**
     * Actualizar la información del perfil del empleado autenticado.
     */
    public function updateEmpleado(Request $request)
    {
        $usuario = Auth::user();
        $empleado = $usuario->empleado;

        $validatedUsuario = $request->validate([
            'Telefono' => 'nullable|string|max:20',
            'Correo_Electronico' => ['required', 'email', Rule::unique('Usuario', 'Correo_Electronico')->ignore($usuario->ID, 'ID')],
            'Fecha_Nacimiento' => 'nullable|date',
            'Nombre_Completo' => 'required|string|max:255',
            'Estado' => 'nullable|string|max:50',
            'Direccion' => 'nullable|string|max:255',
        ]);

        $usuario->update($validatedUsuario);

        $validatedEmpleado = $request->validate([
            'Cargo' => 'nullable|string|max:100',
            'Salario' => 'nullable|numeric',
        ]);

        $empleado->update($validatedEmpleado);

        return redirect()->route('empleado.perfil')->with('success', 'Perfil actualizado correctamente.');
    }

    /**
     * Mostrar formulario de cambio de contraseña para empleado.
     */
    public function editPasswordEmpleado()
    {
        return view('empleado.perfil.password');
    }

    /**
     * Actualizar la contraseña del empleado autenticado.
     */
    public function updatePasswordEmpleado(Request $request)
    {
        $request->validate([
            'password_actual' => 'required',
            'password' => 'required|min:8|confirmed',
        ]);

        $usuario = Auth::user();

        if (!Hash::check($request->password_actual, $usuario->Contraseña)) {
            return back()->withErrors(['password_actual' => 'La contraseña actual no es correcta.']);
        }

        $usuario->Contraseña = Hash::make($request->password);
        $usuario->save();

        return redirect()->route('empleado.perfil')->with('success', 'Contraseña actualizada correctamente.');
    }
}
