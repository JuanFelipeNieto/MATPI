<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MateriaPrima extends Model
{
    use HasFactory;

    protected $table = 'materia_prima';
    protected $primaryKey = 'id';
    public $timestamps = true;

    protected $fillable = [
        'nombre_materia_prima',
        'unidad_medida',
        'cantidad',
        'fecha_ingreso',
        'fecha_vencimiento'
    ];

    // Relación con Producto (muchos a muchos)
    public function productos()
    {
        return $this->belongsToMany(
            Producto::class,
            'details_producto_materiap',
            'materiaprima_id',
            'producto_id'
        )->withPivot('cantidad_usada');
    }

    // Relación con Proveedor (muchos a muchos)
    public function proveedores()
    {
        return $this->belongsToMany(
            Proveedor::class,
            'details_proveedor_materiap', // tabla pivote
            'materiaprima_id',            // clave FK local
            'proveedor_id'                // clave FK relacionada
        )->withPivot('cantidad', 'precio_unitario', 'fecha_suministro')
         ->withTimestamps();
    }
}
