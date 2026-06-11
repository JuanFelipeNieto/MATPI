<?php namespace App\Models;
 use Illuminate\Foundation\Auth\User as Authenticatable;
 use Illuminate\Notifications\Notifiable; 
 class Usuario extends Authenticatable
  { 
    use Notifiable;
     // Nombre real de la tabla 
     protected $table = 'Usuario'; 
     // Clave primaria personalizada 
     protected $primaryKey = 'ID';
      // La PK no es autoincremental 
     public $incrementing = false; // Tipo de dato de la PK 
     protected $keyType = 'string';
      // Tu tabla no maneja timestamps 
      public $timestamps = false; 
      // Campos que se pueden asignar masivamente 
      protected $fillable = [ 
        'ID', 
        'Telefono', 
        'Contraseña',
         'Correo_Electronico', 
         'Rol', 'Fecha_Nacimiento',
          'Nombre_Completo',
          'Estado', 'Direccion', 
          'Fecha_ingreso', 
          'Experiencia_Laboral', 
        ]; /** * Laravel necesita saber qué campo usar como "password". */ 
        public function getAuthPassword() 
        { 
            return $this->Contraseña;
         } /** * Sobrescribir la clave de autenticación para que no sea "email" * sino tu campo personalizado "ID". */ 
         public function getAuthIdentifierName()
          { 
            return 'ID';
         }

         public function getNombreCortoAttribute()
         {
             $partes = explode(' ', trim($this->Nombre_Completo));
             $cantidad = count($partes);

             if ($cantidad >= 4) {
                 return $partes[0] . ' ' . $partes[2];
             } elseif ($cantidad == 3) {
                 // Asumiendo formato: Nombre1 Nombre2 Apellido1
                 return $partes[0] . ' ' . $partes[2];
             } elseif ($cantidad == 2) {
                 return $partes[0] . ' ' . $partes[1];
             } else {
                 return $partes[0] ?? '';
             }
         }

         // Relaciones
          public function administrador() 
         { 
            return $this->hasOne(Administrador::class, 'ID_Usr', 'ID');
         } public function empleado()
          { 
            return $this->hasOne(Empleado::class, 'ID_Usr', 'ID');
         } 
         public function cliente()
          { 
            return $this->hasOne(Cliente::class, 'ID_Usr', 'ID'); 
        } }