<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Empleado extends Model
{
    protected $table = 'Empleado';
    public $timestamps = false;

    // Clave primaria personalizada
    protected $primaryKey = 'ID_Usr';

    // La PK no es autoincremental
    public $incrementing = false;

    // Tipo de dato de la PK
    protected $keyType = 'string';

    protected $fillable = [
        'EPS',
        'tipo_contrato',
        'Contacto_Emergencia_Nombre',
        'Contacto_Emergencia_Parentesco',
        'Contacto_Emergencia_Numero',
        'Fecha_Terminacion_Contrato',
        'ID_Usr',
    ];

    // Relación con Usuario
    public function usuario()
    {
        return $this->belongsTo(Usuario::class, 'ID_Usr', 'ID');
    }
}
