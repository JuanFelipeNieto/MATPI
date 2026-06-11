<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class administrador extends Model
{
 protected $table = 'administrador';
    public $timestamps = false;
    protected $fillable = [
        'Ult_Fecha_login',
        'Ult_IP_login',
        'Formacion_Educativa',
        'ID_Usr',
    ];
    // Relación inversa con Usuario
    public function usuario()
    {
        return $this->belongsTo(Usuario::class, 'ID_Usr', 'ID');
    }
}