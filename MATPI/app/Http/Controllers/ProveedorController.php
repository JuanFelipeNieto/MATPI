<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Proveedor;
use App\Models\MateriaPrima;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class ProveedorController extends Controller
{
    private function getLayout()
    {
        $user = Auth::user();
        return match($user->Rol) {
            'Administrador' => 'layouts.admin',
            'Empleado' => 'layouts.empleado',
            default => 'layouts.app',
        };
    }

    public function index(Request $request)
    {
        $buscar = $request->input('buscar');
        $query = Proveedor::with('materiasPrimas');

        if ($buscar) {
            $query->where('nombre_proveedor', 'like', "%$buscar%")
                  ->orWhere('telefono', 'like', "%$buscar%");
        }

        $proveedores = $query->paginate(10);

        return view('proveedor.index', [
            'layout' => $this->getLayout(),
            'proveedores' => $proveedores,
            'buscar' => $buscar
        ]);
    }

    public function create()
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        $materiasPrimas = MateriaPrima::all();
        return view('proveedor.create', [
            'layout' => $this->getLayout(),
            'materiasPrimas' => $materiasPrimas
        ]);
    }

    public function store(Request $request)
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        $request->validate([
            'nombre_proveedor' => 'required|string|max:50',
            'direccion' => 'required|string|max:120',
            'correo_electronico' => 'nullable|email|max:35',
            'telefono' => 'required|string|max:14',
            'materia_prima_id' => 'required|exists:materia_prima,id',
            'precio_unitario' => 'required|numeric|min:0',
        ]);

        DB::transaction(function () use ($request) {
            $proveedor = Proveedor::create([
                'nombre_proveedor' => $request->nombre_proveedor,
                'direccion' => $request->direccion,
                'correo_electronico' => $request->correo_electronico,
                'telefono' => $request->telefono,
                'id_usr' => Auth::id(),
                'cantidad' => 0 // 🔹 siempre arranca en 0
            ]);

            // 🔹 No registramos cantidad aquí
            $proveedor->materiasPrimas()->attach($request->materia_prima_id, [
                'cantidad' => 0,
                'precio_unitario' => $request->precio_unitario,
                'fecha_suministro' => now()
            ]);
        });

        return redirect()->route('proveedor.index')->with('success', 'Proveedor creado correctamente.');
    }

    public function show(Proveedor $proveedor)
    {
        $proveedor->load('materiasPrimas');
        return view('proveedor.show', [
            'layout' => $this->getLayout(),
            'proveedor' => $proveedor
        ]);
    }

    public function edit(Proveedor $proveedor)
    {
        if (!in_array(Auth::user()->Rol, ['Administrador', 'Empleado'])) {
            abort(403, 'Acceso no autorizado');
        }

        $materiasPrimas = MateriaPrima::all();
        $proveedor->load('materiasPrimas');

        return view('proveedor.edit', [
            'layout' => $this->getLayout(),
            'proveedor' => $proveedor,
            'materiasPrimas' => $materiasPrimas
        ]);
    }

    public function update(Request $request, Proveedor $proveedor)
    {
        if (!in_array(Auth::user()->Rol, ['Administrador', 'Empleado'])) {
            abort(403, 'Acceso no autorizado');
        }

        $rules = [
            'materia_prima_id' => 'required|exists:materia_prima,id',
            'cantidad' => 'required|integer|min:1',
            'precio_unitario' => 'required|numeric|min:0',
        ];

        if (Auth::user()->Rol === 'Administrador') {
            $rules = array_merge($rules, [
                'nombre_proveedor' => 'required|string|max:50',
                'direccion' => 'required|string|max:120',
                'correo_electronico' => 'nullable|email|max:35',
                'telefono' => 'required|string|max:14',
            ]);
        }

        $request->validate($rules);

        DB::transaction(function () use ($request, $proveedor) {
            if (Auth::user()->Rol === 'Administrador') {
                $proveedor->update([
                    'nombre_proveedor' => $request->nombre_proveedor,
                    'direccion' => $request->direccion,
                    'correo_electronico' => $request->correo_electronico,
                    'telefono' => $request->telefono,
                ]);
            }

            // 🔹 Proveedor sigue en 0
            $proveedor->update([
                'cantidad' => 0,
                'id_usr' => Auth::id(),
            ]);

            // 🔹 Se registra la entrega en la tabla pivote
            $proveedor->materiasPrimas()->attach($request->materia_prima_id, [
                'cantidad' => $request->cantidad,
                'precio_unitario' => $request->precio_unitario,
                'fecha_suministro' => now()
            ]);

            // 🔹 Se suma stock
            $materia = MateriaPrima::find($request->materia_prima_id);
            $materia->cantidad += $request->cantidad;
            $materia->save();
        });

        return redirect()->route('proveedor.index')->with('success', 'Entrega registrada y materia prima actualizada.');
    }

    public function destroy(Proveedor $proveedor)
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        DB::transaction(function () use ($proveedor) {
            $proveedor->materiasPrimas()->detach();
            $proveedor->delete();
        });

        return redirect()->route('proveedor.index')->with('success', 'Proveedor eliminado correctamente.');
    }
}
