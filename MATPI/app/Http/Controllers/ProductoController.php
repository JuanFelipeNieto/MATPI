<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Producto;
use App\Models\MateriaPrima;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;

class ProductoController extends Controller
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

    /**
     * Listar productos (Admin y Empleado)
     */
    public function index(Request $request)
    {
        $query = Producto::with('materiasPrimas');

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where('nombre_producto', 'like', "%{$search}%")
                  ->orWhere('categoria', 'like', "%{$search}%");
        }

        $productos = $query->get();

        foreach ($productos as $producto) {
            $producto->cantidad = $this->calcularCantidadDisponible($producto);
        }

        return view('producto.index', [
            'layout' => $this->getLayout(),
            'productos' => $productos,
            'search' => $request->search
        ]);
    }

    /**
     * Mostrar producto (Admin y Empleado)
     */
    public function show(Producto $producto)
    {
        $producto->load('materiasPrimas');
        $producto->cantidad = $this->calcularCantidadDisponible($producto);

        return view('producto.show', [
            'layout' => $this->getLayout(),
            'producto' => $producto
        ]);
    }

    /**
     * Formulario de creación (solo Admin)
     */
    public function create()
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        $materiasPrimas = MateriaPrima::all();

        return view('producto.create', [
            'layout' => $this->getLayout(),
            'materiasPrimas' => $materiasPrimas
        ]);
    }

    /**
     * Guardar nuevo producto (solo Admin)
     */
    public function store(Request $request)
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        $request->validate([
            'nombre_producto' => 'required|string|max:35',
            'descripcion' => 'nullable|string',
            'valor' => 'required|integer|min:0',
            'categoria' => 'required|in:Hamburguesas,Perros,Empanadas,Bebidas,Guarniciones,Especias y Condimentos,Salsas y Aderezos,Otros',
            'imagen' => 'nullable|image|max:2048',
            'materias_primas' => 'required|array',
            'materias_primas.*.id' => 'required|exists:materia_prima,id',
            'materias_primas.*.cantidad_usada' => 'required|integer|min:1',
        ]);

        DB::transaction(function () use ($request) {
            $producto = new Producto();
            $producto->nombre_producto = $request->nombre_producto;
            $producto->descripcion = $request->descripcion;
            $producto->valor = $request->valor;
            $producto->categoria = $request->categoria;

            if ($request->hasFile('imagen')) {
                $path = $request->file('imagen')->store('productos', 'public');
                $producto->imagen = $path;
            }

            $producto->save();

            foreach ($request->materias_primas as $mp) {
                $producto->materiasPrimas()->attach($mp['id'], [
                    'cantidad_usada' => $mp['cantidad_usada']
                ]);
            }

            $producto->cantidad = $this->calcularCantidadDisponible($producto);
            $producto->save();
        });

        return redirect()->route('producto.index')->with('success', 'Producto creado correctamente.');
    }

    /**
     * Formulario de edición (solo Admin)
     */
    public function edit(Producto $producto)
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        $materiasPrimas = MateriaPrima::all();
        $producto->load('materiasPrimas');
        $producto->cantidad = $this->calcularCantidadDisponible($producto);

        return view('producto.edit', [
            'layout' => $this->getLayout(),
            'producto' => $producto,
            'materiasPrimas' => $materiasPrimas
        ]);
    }

    /**
     * Actualizar producto (solo Admin)
     */
    public function update(Request $request, Producto $producto)
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        $request->validate([
            'nombre_producto' => 'required|string|max:35',
            'descripcion' => 'nullable|string',
            'valor' => 'required|integer|min:0',
            'categoria' => 'required|in:Hamburguesas,Perros,Empanadas,Bebidas,Guarniciones,Especias y Condimentos,Salsas y Aderezos,Otros',
            'imagen' => 'nullable|image|max:2048',
            'materias_primas' => 'required|array',
            'materias_primas.*.id' => 'required|exists:materia_prima,id',
            'materias_primas.*.cantidad_usada' => 'required|integer|min:1',
        ]);

        DB::transaction(function () use ($request, $producto) {
            $producto->nombre_producto = $request->nombre_producto;
            $producto->descripcion = $request->descripcion;
            $producto->valor = $request->valor;
            $producto->categoria = $request->categoria;

            if ($request->hasFile('imagen')) {
                if ($producto->imagen) {
                    Storage::disk('public')->delete($producto->imagen);
                }
                $path = $request->file('imagen')->store('productos', 'public');
                $producto->imagen = $path;
            }

            $producto->save();

            $syncData = [];
            foreach ($request->materias_primas as $mp) {
                $syncData[$mp['id']] = ['cantidad_usada' => $mp['cantidad_usada']];
            }
            $producto->materiasPrimas()->sync($syncData);

            $producto->cantidad = $this->calcularCantidadDisponible($producto);
            $producto->save();
        });

        return redirect()->route('producto.index')->with('success', 'Producto actualizado correctamente.');
    }

    /**
     * Eliminar producto (solo Admin)
     */
    public function destroy(Producto $producto)
    {
        if (Auth::user()->Rol !== 'Administrador') {
            abort(403, 'Acceso no autorizado');
        }

        if ($producto->imagen) {
            Storage::disk('public')->delete($producto->imagen);
        }

        $producto->materiasPrimas()->detach();
        $producto->delete();

        return redirect()->route('producto.index')->with('success', 'Producto eliminado correctamente.');
    }

    /**
     * Calcular cantidad disponible
     */
    private function calcularCantidadDisponible(Producto $producto)
    {
        $producto->load('materiasPrimas');

        if ($producto->materiasPrimas->isEmpty()) {
            return 0;
        }

        $cantidades = [];

        foreach ($producto->materiasPrimas as $mp) {
            $stock = $mp->cantidad;
            $usada = $mp->pivot->cantidad_usada;

            if ($usada > 0) {
                $cantidades[] = intdiv($stock, $usada);
            }
        }

        return empty($cantidades) ? 0 : min($cantidades);
    }
}
