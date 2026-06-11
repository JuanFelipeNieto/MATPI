<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\MateriaPrima;
use Illuminate\Support\Facades\Auth;
use Barryvdh\DomPDF\Facade\Pdf;

class MateriaPrimaController extends Controller
{
    /**
     * Obtener el layout según el rol del usuario.
     */
    private function getLayout()
    {
        $user = Auth::user();
        return match($user->Rol) {
            'Administrador' => 'layouts.admin',
            'Empleado' => 'layouts.empleado',
            default => 'layouts.app',
        };
    }

    /**
     * Mostrar listado de materias primas con búsqueda opcional.
     */
    public function index(Request $request)
    {
        $buscar = $request->get('buscar', '');

        $materiasPrimas = MateriaPrima::query()
            ->when($buscar, function ($query, $buscar) {
                $query->where('nombre_materia_prima', 'like', "%{$buscar}%");
            })
            ->orderBy('nombre_materia_prima')
            ->paginate(10)
            ->withQueryString();

        return view('materia_prima.index', [
            'materiasPrimas' => $materiasPrimas,
            'layout' => $this->getLayout(),
            'buscar' => $buscar,
        ]);
    }

    /**
     * Mostrar el formulario de creación.
     */
    public function create()
    {
        $this->authorizeRole('Administrador');

        return view('materia_prima.create', [
            'layout' => $this->getLayout(),
        ]);
    }

    /**
     * Guardar nueva materia prima.
     */
    public function store(Request $request)
    {
        $this->authorizeRole('Administrador');

        $validated = $request->validate([
            'nombre_materia_prima' => 'required|string|max:60',
            'unidad_medida' => 'required|string|max:20',
            'cantidad' => 'required|integer|min:0',
            'fecha_ingreso' => 'required|date',
            'fecha_vencimiento' => 'nullable|date',
        ]);

        MateriaPrima::create($validated);

        return redirect()->route('materia_prima.index')->with('success', 'Materia prima creada exitosamente.');
    }

    /**
     * Mostrar detalle de una materia prima.
     */
    public function show(MateriaPrima $materiaPrima)
    {
        return view('materia_prima.show', [
            'materiaPrima' => $materiaPrima,
            'layout' => $this->getLayout(),
        ]);
    }

    /**
     * Mostrar formulario de edición.
     */
    public function edit(MateriaPrima $materiaPrima)
    {
        $this->authorizeRole('Administrador');

        return view('materia_prima.edit', [
            'materiaPrima' => $materiaPrima,
            'layout' => $this->getLayout(),
        ]);
    }

    /**
     * Actualizar materia prima.
     */
    public function update(Request $request, MateriaPrima $materiaPrima)
    {
        $this->authorizeRole('Administrador');

        $validated = $request->validate([
            'nombre_materia_prima' => 'required|string|max:60',
            'unidad_medida' => 'required|string|max:20',
            'cantidad' => 'required|integer|min:0',
            'fecha_ingreso' => 'required|date',
            'fecha_vencimiento' => 'nullable|date',
        ]);

        $materiaPrima->update($validated);

        return redirect()->route('materia_prima.index')->with('success', 'Materia prima actualizada exitosamente.');
    }

    /**
     * Eliminar materia prima.
     */
    public function destroy(MateriaPrima $materiaPrima)
    {
        $this->authorizeRole('Administrador');

        $materiaPrima->delete();

        return redirect()->route('materia_prima.index')->with('success', 'Materia prima eliminada exitosamente.');
    }

    /**
     * Validar rol de usuario.
     */
    private function authorizeRole($role)
    {
        if (Auth::user()->Rol !== $role) {
            abort(403, 'No tienes permisos para realizar esta acción.');
        }
        
    }
    
    public function reportePDF(Request $request)
{
    $buscar = $request->get('buscar', '');

    $materiasPrimas = MateriaPrima::query()
        ->when($buscar, function($query, $buscar) {
            $query->where('nombre_materia_prima', 'like', "%{$buscar}%");
        })
        ->orderBy('nombre_materia_prima')
        ->get();

    $pdf = Pdf::loadView('materia_prima.reporte', compact('materiasPrimas'));

    return $pdf->download('reporte_materias_primas.pdf');
}
}
