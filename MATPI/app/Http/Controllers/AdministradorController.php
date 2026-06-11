<?php

namespace App\Http\Controllers;

use App\Models\administrador;
use Illuminate\Http\Request;

class AdministradorController extends Controller
{

    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        // Obtener todos los administradores con su usuario relacionado
        $administradores = Administrador::with('usuario')->paginate(10);
        return view('administradores.index', compact('administradores'));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        // Mostrar formulario para crear administrador
        return view('administradores.create');
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        // Validar datos para usuario y administrador
        $validatedUsuario = $request->validate([
            'ID' => 'required|string|unique:Usuario,ID',
            'Telefono' => 'nullable|string|max:20',
            'Contraseña' => 'required|string|min:6|confirmed',
            'Correo_Electronico' => 'required|email|unique:Usuario,Correo_Electronico',
            'Rol' => ['required', Rule::in(['Administrador'])], // Solo Administrador aquí
            'Fecha_Nacimiento' => 'nullable|date',
            'Nombre_Completo' => 'required|string|max:255',
            'Estado' => 'nullable|string|max:50',
            'Direccion' => 'nullable|string|max:255',
            'Fecha_ingreso' => 'nullable|date',
            'Experiencia_Laboral' => 'nullable|string',
        ]);

        // Hashear contraseña
        $validatedUsuario['Contraseña'] = bcrypt($validatedUsuario['Contraseña']);

        // Crear usuario
        $usuario = Usuario::create($validatedUsuario);

        // Validar datos específicos de administrador
        $validatedAdmin = $request->validate([
            'Cargo' => 'required|string|max:255',
            'ID_Usr' => 'required|string|exists:Usuario,ID',
        ]);

        // Asegurar que ID_Usr sea el usuario creado
        $validatedAdmin['ID_Usr'] = $usuario->ID;

        // Crear administrador
        Administrador::create($validatedAdmin);

        return redirect()->route('administradores.index')->with('success', 'Administrador creado correctamente.');
    }

    /**
     * Display the specified resource.
     */
    public function show(Administrador $administrador)
    {
        $administrador->load('usuario');
        return view('administradores.show', compact('administrador'));
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Administrador $administrador)
    {
        $administrador->load('usuario');
        return view('administradores.edit', compact('administrador'));
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Administrador $administrador)
    {
        // Validar datos para usuario
        $usuario = $administrador->usuario;

        $validatedUsuario = $request->validate([
            'Telefono' => 'nullable|string|max:20',
            'Contraseña' => 'nullable|string|min:6|confirmed',
            'Correo_Electronico' => ['required', 'email', Rule::unique('Usuario', 'Correo_Electronico')->ignore($usuario->ID, 'ID')],
            'Fecha_Nacimiento' => 'nullable|date',
            'Nombre_Completo' => 'required|string|max:255',
            'Estado' => 'nullable|string|max:50',
            'Direccion' => 'nullable|string|max:255',
            'Fecha_ingreso' => 'nullable|date',
            'Experiencia_Laboral' => 'nullable|string',
        ]);

        if (!empty($validatedUsuario['Contraseña'])) {
            $validatedUsuario['Contraseña'] = bcrypt($validatedUsuario['Contraseña']);
        } else {
            unset($validatedUsuario['Contraseña']);
        }

        $usuario->update($validatedUsuario);

        // Validar datos específicos de administrador
        $validatedAdmin = $request->validate([
            'Cargo' => 'required|string|max:255',
        ]);

        $administrador->update($validatedAdmin);

        return redirect()->route('administradores.index')->with('success', 'Administrador actualizado correctamente.');
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Administrador $administrador)
    {
        // Eliminar primero el administrador
        $administrador->delete();

        // Opcional: eliminar también el usuario relacionado
        $administrador->usuario->delete();

        return redirect()->route('administradores.index')->with('success', 'Administrador eliminado correctamente.');
    }
}