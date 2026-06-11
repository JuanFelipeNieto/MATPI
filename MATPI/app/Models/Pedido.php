<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Pedido extends Model
{
    use HasFactory;

    protected $table = 'pedidos';
    protected $primaryKey = 'ID';
    public $timestamps = true;

    protected $fillable = [
        'Fecha',
        'Estado',
        'Valor',
        'Mesa',
        'Numero_Personas',
        'ID_Usr',
        'ID_Reserva',
        'ID_Cliente'
    ];

    // Relación con Empleado
    public function empleado()
    {
        return $this->belongsTo(Empleado::class, 'ID_Usr', 'ID_Usr');
    }

    // Relación con Cliente (opcional)
    public function cliente()
    {
        return $this->belongsTo(Cliente::class, 'ID_Cliente', 'ID');
    }

    // Relación con Reserva (opcional)
    public function reserva()
    {
        return $this->belongsTo(Reserva::class, 'ID_Reserva', 'ID');
    }

    // Relación muchos a muchos con Productos
    public function productos()
    {
        return $this->belongsToMany(
            Producto::class,
            'pedido_producto',
            'pedido_id',
            'producto_id'
        )->withPivot('cantidad')
         ->withTimestamps();
    }
}
