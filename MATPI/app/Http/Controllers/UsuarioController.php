<?php

namespace App\Http\Controllers;

use App\Models\Usuario;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class UsuarioController extends Controller
{
    /**
     * Mostrar listado de usuarios.
     */
    public function index()
    {
        $usuarios = Usuario::paginate(10);
        return view('usuarios.index', compact('usuarios'));
    }

    /**
     * Formulario crear usuario.
     */
    public function create()
    {
        return view('usuarios.create');
    }

    /**
     * Guardar un nuevo usuario.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'ID' => 'required|string|unique:usuarios,ID',
            'Telefono' => 'nullable|string|max:20',
            'Contraseña' => 'required|string|min:6|confirmed',
            'Correo_Electronico' => 'required|email|unique:usuarios,Correo_Electronico',
            'Rol' => ['required', Rule::in(['Administrador', 'Empleado'])],
            'Fecha_Nacimiento' => 'nullable|date',
            'Nombre_Completo' => 'required|string|max:255',
            'Estado' => 'nullable|string|max:50',
            'Direccion' => 'nullable|string|max:255',
            'Fecha_ingreso' => 'nullable|date',
            'Experiencia_Laboral' => 'nullable|string',
        ]);

        // Hashear contraseña
        $validated['Contraseña'] = bcrypt($validated['Contraseña']);

        Usuario::create($validated);

        return redirect()->route('usuarios.index')->with('success', 'Usuario creado correctamente.');
    }

    /**
     * Mostrar un usuario específico.
     */
    public function show(Usuario $usuario)
    {
        return view('usuarios.show', compact('usuario'));
    }

    /**
     * Formulario editar usuario.
     */
    public function edit(Usuario $usuario)
    {
        return view('usuarios.edit', compact('usuario'));
    }

    /**
     * Actualizar usuario.
     */
    public function update(Request $request, Usuario $usuario)
    {
        $validated = $request->validate([
            'Telefono' => 'nullable|string|max:20',
            'Contraseña' => 'nullable|string|min:6|confirmed',
            'Correo_Electronico' => [
                'required',
                'email',
                Rule::unique('usuarios', 'Correo_Electronico')->ignore($usuario->ID, 'ID'),
            ],
            'Rol' => ['required', Rule::in(['Administrador', 'Empleado'])],
            'Fecha_Nacimiento' => 'nullable|date',
            'Nombre_Completo' => 'required|string|max:255',
            'Estado' => 'nullable|string|max:50',
            'Direccion' => 'nullable|string|max:255',
            'Fecha_ingreso' => 'nullable|date',
            'Experiencia_Laboral' => 'nullable|string',
        ]);

        // Solo actualizar contraseña si se envió
        if (!empty($validated['Contraseña'])) {
            $validated['Contraseña'] = bcrypt($validated['Contraseña']);
        } else {
            unset($validated['Contraseña']);
        }

        $usuario->update($validated);

        return redirect()->route('usuarios.index')->with('success', 'Usuario actualizado correctamente.');
    }

    /**
     * Eliminar usuario.
     */
    public function destroy(Usuario $usuario)
    {
        $usuario->delete();
        return redirect()->route('usuarios.index')->with('success', 'Usuario eliminado correctamente.');
    }
}
