<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Proveedor extends Model
{
    use HasFactory;

    protected $table = 'proveedor';
    protected $primaryKey = 'id';
    public $timestamps = true;

    protected $fillable = [
        'nombre_proveedor',
        'direccion',
        'correo_electronico',
        'telefono',
        'id_usr',
        'cantidad'
    ];

    // Relación con MateriaPrima (muchos a muchos)
    public function materiasPrimas()
    {
        return $this->belongsToMany(
            MateriaPrima::class,
            'details_proveedor_materiap', // tabla pivote
            'proveedor_id',              // clave FK local
            'materiaprima_id'            // clave FK relacionada
        )->withPivot('cantidad', 'precio_unitario', 'fecha_suministro')
         ->withTimestamps();
    }
}
