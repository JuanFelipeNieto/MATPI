<?php

namespace App\Http\Controllers;

use App\Models\Cliente;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class ClienteController extends Controller
{
    /**
     * 🔹 Retorna el layout correcto según el rol del usuario
     */
    private function getLayout()
    {
        return Auth::user()->Rol === 'Administrador'
            ? 'layouts.admin'
            : 'layouts.empleado';
    }

    // 📌 Listado de clientes
    public function index(Request $request)
    {
        $query = Cliente::query();

        // 🔹 Filtrar por búsqueda si existe
        if ($request->filled('buscar')) {
            $buscar = $request->buscar;
            $query->where('ID', 'like', "%$buscar%")
                  ->orWhere('Nombre_Completo', 'like', "%$buscar%");
        }

        $clientes = $query->orderBy('Nombre_Completo')->paginate(10);

        return view('clientes.index', [
            'clientes' => $clientes,
            'layout' => $this->getLayout(),
            'buscar' => $request->buscar ?? ''
        ]);
    }

    // 📌 Formulario de creación
    public function create()
    {
        return view('clientes.create', [
            'layout' => $this->getLayout()
        ]);
    }

    // 📌 Guardar cliente
    public function store(Request $request)
    {
        $request->validate([
            'ID' => 'required|numeric|digits:10|unique:Cliente,ID',
            'Nombre_Completo' => 'required|string|max:40',
            'Telefono' => 'nullable|string|max:14',
        ]);

        // Determinar ID_Usr según rol
        $empleado = Auth::user()->Rol === 'Empleado' ? Auth::user()->empleado : null;

        Cliente::create([
            'ID' => $request->ID,
            'Nombre_Completo' => $request->Nombre_Completo,
            'Telefono' => $request->Telefono ?? null,
            'Ultima_Visita' => null,
            'Total_Consumo' => 0,
            'Fecha_Registro' => now(),
            'ID_Usr' => $empleado ? $empleado->ID_Usr : null, // null si es admin
        ]);

        return redirect()->route('clientes.index')
                         ->with('success', 'Cliente registrado correctamente');
    }

    // 📌 Formulario de edición
    public function edit(Cliente $cliente)
    {
        return view('clientes.edit', [
            'cliente' => $cliente,
            'layout' => $this->getLayout()
        ]);
    }

    // 📌 Actualizar cliente
    public function update(Request $request, Cliente $cliente)
    {
        $request->validate([
            'Nombre_Completo' => 'required|string|max:40',
            'Telefono' => 'nullable|string|max:14',
        ]);

        $cliente->update($request->only('Nombre_Completo', 'Telefono'));

        return redirect()->route('clientes.index')
                         ->with('success', 'Cliente actualizado correctamente');
    }

    // 📌 Eliminar cliente
    public function destroy(Cliente $cliente)
    {
        $cliente->delete();

        return redirect()->route('clientes.index')
                         ->with('success', 'Cliente eliminado correctamente');
    }
}
