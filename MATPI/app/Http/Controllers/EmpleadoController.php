<?php

namespace App\Http\Controllers;

use App\Models\Empleado;
use App\Models\Usuario;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;
use Barryvdh\DomPDF\Facade\Pdf;


class EmpleadoController extends Controller
{
    public function reportePDF(Request $request)
{
    $query = Empleado::with('usuario');

    // Filtro opcional por buscador
    if ($request->filled('buscar')) {
        $buscar = $request->buscar;
        $query->whereHas('usuario', function($q) use ($buscar) {
            $q->where('ID', 'like', "%$buscar%")
              ->orWhere('Nombre_Completo', 'like', "%$buscar%");
        });
    }

    $empleados = $query->orderBy('ID_Usr', 'asc')->get();

    // Generar PDF desde la vista de reporte
    $pdf = Pdf::loadView('administrador.empleados.reporte', compact('empleados'));

    return $pdf->download('reporte_empleados.pdf');
}
    // Listado de empleados con búsqueda
    public function index(Request $request)
{
    $query = Empleado::with('usuario');

    if ($request->filled('buscar')) {
        $buscar = $request->buscar;
        $query->whereHas('usuario', function($q) use ($buscar) {
            $q->where('ID', 'like', "%$buscar%")
              ->orWhere('Nombre_Completo', 'like', "%$buscar%");
        });
    }

    $empleados = $query->orderBy('ID_Usr', 'asc')->paginate(10)->withQueryString();

    // Definir layout dinámico según rol
    $layout = auth()->user()->Rol === 'Administrador' ? 'layouts.admin' : 'layouts.app';

    return view('administrador.empleados.index', [
        'empleados' => $empleados,
        'buscar' => $request->buscar ?? '',
        'layout' => $layout
    ]);
}


    // Guardar nuevo empleado
    public function store(Request $request)
    {
        $validatedUsuario = $request->validate([
            'ID' => 'required|string|max:16|unique:Usuario,ID',
            'Nombre_Completo' => 'required|string|max:40',
            'Correo_Electronico' => 'required|email|max:35|unique:Usuario,Correo_Electronico',
            'Telefono' => 'required|string|max:14',
            'Contraseña' => 'required|string|min:6|confirmed',
            'Direccion' => 'required|string|max:50',
            'Estado' => 'required|boolean',
            'Fecha_ingreso' => 'required|date',
            'Experiencia_Laboral' => 'required|string|max:15',
            'Fecha_Nacimiento' => 'required|date',
            'Rol' => ['required', Rule::in(['Empleado'])]
        ]);

        $validatedUsuario['Contraseña'] = bcrypt($validatedUsuario['Contraseña']);

        $validatedEmpleado = $request->validate([
            'EPS' => ['required', Rule::in([
                'Nueva EPS','Sanitas','SURA','Salud Total','Compensar','Famisanar','Coosalud',
                'Mutual Ser','SOS','Salud Mía','Aliansalud','Dusakawi','Salud Bolívar',
                'Savia Salud','Cajacopi','Asmet Salud','Emssanar','Capital Salud'
            ])],
            'tipo_contrato' => ['required', Rule::in(['Indefinido','Fijo','Servicios','Temporal'])],
            'Contacto_Emergencia_Nombre' => 'required|string|max:35',
            'Contacto_Emergencia_Parentesco' => 'required|string|max:15',
            'Contacto_Emergencia_Numero' => 'required|string|max:14',
            'Fecha_Terminacion_Contrato' => 'nullable|date',
        ]);

        \DB::beginTransaction();
        try {
            $usuario = Usuario::create($validatedUsuario);

            $validatedEmpleado['ID_Usr'] = $usuario->ID;
            Empleado::create($validatedEmpleado);

            \DB::commit();

            return redirect()->route('administrador.empleados.index')
                ->with('success', 'Empleado creado correctamente.');
        } catch (\Exception $e) {
            \DB::rollBack();
            return back()->withInput()->withErrors(['error' => 'No se pudo crear el empleado: ' . $e->getMessage()]);
        }
    }

    // Mostrar un empleado
    public function show(Empleado $empleado)
    {
        $empleado->load('usuario');
        return view('administrador.empleados.show', compact('empleado'));
    }
public function create()
{
    return view('administrador.empleados.create');
}
    // Formulario de edición
    public function edit(Empleado $empleado)
    {
        $empleado->load('usuario');
        return view('administrador.empleados.edit', compact('empleado'));
    }

    // Actualizar empleado
    public function update(Request $request, Empleado $empleado)
    {
        $usuario = $empleado->usuario;

        $validatedUsuario = $request->validate([
            'Telefono' => 'required|string|max:14',
            'Contraseña' => 'nullable|string|min:6|confirmed',
            'Correo_Electronico' => [
                'required','email','max:35',
                Rule::unique('Usuario','Correo_Electronico')->ignore($usuario->ID,'ID')
            ],
            'Fecha_Nacimiento' => 'required|date',
            'Nombre_Completo' => 'required|string|max:40',
            'Estado' => 'required|boolean',
            'Direccion' => 'required|string|max:50',
            'Fecha_ingreso' => 'required|date',
            'Experiencia_Laboral' => 'required|string|max:15',
        ]);

        if (!empty($validatedUsuario['Contraseña'])) {
            $validatedUsuario['Contraseña'] = bcrypt($validatedUsuario['Contraseña']);
        } else {
            unset($validatedUsuario['Contraseña']);
        }

        try {
            $usuario->update($validatedUsuario);

            $validatedEmpleado = $request->validate([
                'EPS' => ['required', Rule::in([
                    'Nueva EPS','Sanitas','SURA','Salud Total','Compensar','Famisanar','Coosalud',
                    'Mutual Ser','SOS','Salud Mía','Aliansalud','Dusakawi','Salud Bolívar',
                    'Savia Salud','Cajacopi','Asmet Salud','Emssanar','Capital Salud'
                ])],
                'tipo_contrato' => ['required', Rule::in(['Indefinido','Fijo','Servicios','Temporal'])],
                'Contacto_Emergencia_Nombre' => 'required|string|max:35',
                'Contacto_Emergencia_Parentesco' => 'required|string|max:15',
                'Contacto_Emergencia_Numero' => 'required|string|max:14',
                'Fecha_Terminacion_Contrato' => 'nullable|date',
            ]);

            $empleado->update($validatedEmpleado);

            return redirect()->route('administrador.empleados.index')
                ->with('success', 'Empleado actualizado correctamente.');

        } catch (\Exception $e) {
            return back()->withInput()->with('error', 'Error al actualizar empleado: ' . $e->getMessage());
        }
    }

    // Eliminar empleado
    public function destroy(Empleado $empleado)
    {
        try {
            $usuario = $empleado->usuario;
            $empleado->delete();
            if ($usuario) {
                $usuario->delete();
            }
            return redirect()->route('administrador.empleados.index')
                ->with('success', 'Empleado eliminado correctamente.');
        } catch (\Exception $e) {
            return back()->with('error', 'Error al eliminar empleado: ' . $e->getMessage());
        }
    }
}
