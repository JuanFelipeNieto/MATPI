<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Cliente extends Model
{
    protected $table = 'Cliente';
    protected $primaryKey = 'ID';
    public $incrementing = false; // porque lo asignas manualmente
    public $timestamps = false;   // ✨ Evita que Laravel busque created_at y updated_at

    protected $fillable = [
        'ID',
        'Nombre_Completo',
        'Telefono',
        'Ultima_Visita',
        'Total_Consumo',
        'Fecha_Registro',
        'ID_Usr'
    ];
}
