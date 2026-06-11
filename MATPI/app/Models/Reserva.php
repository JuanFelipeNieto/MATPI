<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Reserva extends Model
{
    use HasFactory;

    // Nombre de la tabla si no sigue la convención plural
    protected $table = 'Reservas';

    // Campos que se pueden llenar masivamente
   protected $fillable = [
    'Fecha',
    'Estado',
    'Observaciones',
    'ID_Usr',
    'registrado_por',
];


    // Desactivar el uso de nombre de columnas en snake_case
    public $timestamps = true;

    /**
     * Relación con Cliente
     */
    public function cliente()
    {
        // ID_Usr en Reservas apunta a ID en Cliente
        return $this->belongsTo(Cliente::class, 'ID_Usr', 'ID');
    }
}
