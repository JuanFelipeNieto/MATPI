<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Producto extends Model
{
    use HasFactory;

    protected $table = 'producto';
    protected $primaryKey = 'id';
    public $timestamps = true;

    protected $fillable = [
        'nombre_producto',
        'descripcion',
        'cantidad',
        'valor',
        'categoria',
        'imagen',
    ];

    // Relación con Materia Prima (muchos a muchos)
    public function materiasPrimas()
    {
        return $this->belongsToMany(
            MateriaPrima::class,
            'details_producto_materiap',
            'producto_id',
            'materiaprima_id'
        )->withPivot('cantidad_usada');
    }
    public function pedidos()
{
    return $this->belongsToMany(Pedido::class, 'pedido_producto', 'producto_id', 'pedido_id')
                ->withPivot('cantidad')
                ->withTimestamps();
}

}
