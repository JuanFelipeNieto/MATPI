<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Pedido;
use App\Models\Producto;
use App\Models\Cliente;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class PedidoController extends Controller
{
    // Selecciona layout según rol del usuario
    private function getLayout()
    {
        $user = Auth::user();
        return match($user->Rol) {
            'Administrador' => 'layouts.admin',
            'Empleado' => 'layouts.empleado',
            default => 'layouts.app',
        };
    }

    // Mostrar formulario para crear un pedido
    public function create()
    {
        $layout = $this->getLayout();
        $productos = Producto::all();    // Todos los productos disponibles
        $clientes = Cliente::all();      // Todos los clientes existentes

        return view('pedido.create', compact('productos', 'clientes', 'layout'));
    }

    // Guardar el pedido en la base de datos
    public function store(Request $request)
    {
        $request->validate([
            'productos' => 'required|array',
            'productos.*.id' => 'required|exists:producto,id',
            'productos.*.cantidad' => 'required|integer|min:1',
            'mesa' => 'nullable|integer|min:1',
            'numero_personas' => 'nullable|integer|min:1',
            'ID_Cliente' => 'nullable|exists:Cliente,ID',
        ]);

        DB::transaction(function () use ($request) {
            $user = Auth::user();

            // Crear pedido
            $pedido = Pedido::create([
                'Fecha' => now(),                  // Fecha automática
                'Estado' => true,                  // Pedido activo
                'Valor' => 0,                      // Se calculará después
                'Mesa' => $request->mesa,
                'Numero_Personas' => $request->numero_personas,
                'ID_Usr' => $user->ID_Usr,
                'ID_Reserva' => null,
                'ID_Cliente' => $request->ID_Cliente ?? null,
            ]);

            $total = 0;

            // Guardar productos del pedido y calcular total
            foreach ($request->productos as $prod) {
                $producto = Producto::find($prod['id']);
                $cantidad = $prod['cantidad'];

                $pedido->productos()->attach($producto->id, ['cantidad' => $cantidad]);

                $total += $producto->Precio * $cantidad; // Suponiendo que Producto tiene campo Precio
            }

            // Actualizar valor total del pedido
            $pedido->Valor = $total;
            $pedido->save();
        });

        return redirect()->route('pedido.create')->with('success', 'Pedido creado correctamente.');
    }

    // Mostrar todos los pedidos
    public function index()
    {
        $layout = $this->getLayout();
        $pedidos = Pedido::with('productos', 'empleado', 'cliente')->get();

        return view('pedido.index', compact('pedidos', 'layout'));
    }

    // Mostrar detalle de un pedido
    public function show(Pedido $pedido)
    {
        $layout = $this->getLayout();
        $pedido->load('productos', 'empleado', 'cliente'); // Cargar relaciones

        return view('pedido.show', compact('pedido', 'layout'));
    }
}
