<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Reserva;
use App\Models\Cliente;
use Illuminate\Support\Facades\Auth;

class ReservaController extends Controller
{
    /**
     * Obtener el layout según el rol del usuario.
     */
    private function getLayout()
    {
        $user = Auth::user();

        switch ($user->Rol) {
            case 'Administrador':
                return 'layouts.admin';
            case 'Empleado':
                return 'layouts.empleado';
            default:
                return 'layouts.app';
        }
    }

    /**
     * Mostrar todas las reservas.
     */
    public function index(Request $request)
    {
        $layout = $this->getLayout();
        $buscar = $request->get('buscar');
        $query = Reserva::with('cliente');

        if ($buscar) {
            $query->whereHas('cliente', function ($q) use ($buscar) {
                $q->where('Nombre_Completo', 'like', "%$buscar%")
                  ->orWhere('ID', 'like', "%$buscar%");
            })->orWhere('Fecha', 'like', "%$buscar%");
        }

        $reservas = $query->get();

        return view('reservas.index', compact('reservas', 'layout', 'buscar'));
    }

    /**
     * Mostrar formulario para crear nueva reserva.
     */
    public function create()
    {
        $layout = $this->getLayout();
        $clientes = Cliente::all();

        return view('reservas.create', compact('clientes', 'layout'));
    }

    /**
     * Almacenar nueva reserva.
     */
    public function store(Request $request)
    {
        $request->validate([
            'fecha' => 'required|date',
            'hora' => 'required',
            'estado' => 'required|boolean',
            'id_cliente' => 'required|exists:Cliente,ID',
            'observaciones' => 'nullable|string',
        ]);

        // Combinar fecha y hora en datetime
        $fechaCompleta = $request->fecha . ' ' . $request->hora;

        Reserva::create([
            'Fecha' => $fechaCompleta,
            'Estado' => $request->estado,
            'ID_Usr' => $request->id_cliente,
            'Observaciones' => $request->observaciones,
            'registrado_por' => auth()->user()->Nombre_Completo,
        ]);

        return redirect()->route('reservas.index')->with('success', 'Reserva creada correctamente.');
    }

    /**
     * Mostrar formulario para editar reserva.
     */
    public function edit($id)
    {
        $layout = $this->getLayout();
        $reserva = Reserva::findOrFail($id);
        $clientes = Cliente::all();

        return view('reservas.edit', compact('reserva', 'clientes', 'layout'));
    }

    /**
     * Actualizar reserva.
     */
    public function update(Request $request, $id)
    {
        $reserva = Reserva::findOrFail($id);

        $request->validate([
            'fecha' => 'required|date',
            'hora' => 'required',
            'estado' => 'required|boolean',
            'id_cliente' => 'required|exists:Cliente,ID',
            'observaciones' => 'nullable|string',
        ]);

        // Combinar fecha y hora en datetime
        $fechaCompleta = $request->fecha . ' ' . $request->hora;

        $reserva->update([
            'Fecha' => $fechaCompleta,
            'Estado' => $request->estado,
            'ID_Usr' => $request->id_cliente,
            'Observaciones' => $request->observaciones,
        ]);

        return redirect()->route('reservas.index')->with('success', 'Reserva actualizada correctamente.');
    }

    /**
     * Eliminar reserva.
     */
    public function destroy($id)
    {
        $reserva = Reserva::findOrFail($id);
        $reserva->delete();

        return redirect()->route('reservas.index')->with('success', 'Reserva eliminada correctamente.');
    }
}
