<?php 
use Illuminate\Database\Migrations\Migration; 
use Illuminate\Database\Schema\Blueprint; 
use Illuminate\Support\Facades\Schema; 

return new class extends Migration 
{ 
    /** * Run the migrations. */ 
    public function up() 
    { 
        Schema::create('Usuario', function (Blueprint $table) { 
            $table->string('ID', 16)->primary(); 
            $table->string('Telefono', 14); 
            $table->string('Contraseña', 255); 
            $table->string('Correo_Electronico', 35);
             $table->enum('Rol', ['Administrador', 'Empleado']);
              $table->date('Fecha_Nacimiento')->nullable(); 
              $table->string('Nombre_Completo', 40); 
              $table->boolean('Estado');
               $table->string('Direccion', 50);
                $table->date('Fecha_ingreso'); 
                $table->string('Experiencia_Laboral', 15); 
            });
                 Schema::create('Administrador', function (Blueprint $table) { 
                    $table->dateTime('Ult_Fecha_login')->nullable();
                     $table->string('Ult_IP_login', 45)->nullable(); 
                     $table->string('Formacion_Educativa', 35)->nullable(); 
                     $table->string('ID_Usr', 16); 
                     $table->foreign('ID_Usr')->references('ID')->on('Usuario')->onDelete('cascade'); 
                    }); 
                    Schema::create('Empleado', function (Blueprint $table) {
                         $table->enum('EPS', [ 
                            'Nueva EPS', 'Sanitas', 'SURA', 'Salud Total',
                             'Compensar', 'Famisanar', 'Coosalud', 'Mutual Ser',
                              'SOS', 'Salud Mía', 'Aliansalud', 'Dusakawi', 
                              'Salud Bolívar', 'Savia Salud', 'Cajacopi', 
                              'Asmet Salud', 'Emssanar', 'Capital Salud' 
                            ]);
                             $table->enum('tipo_contrato', ['Indefinido', 'Fijo', 'Servicios', 'Temporal']); 
                             $table->string('Contacto_Emergencia_Nombre', 35);
                              $table->string('Contacto_Emergencia_Parentesco', 15); 
                              $table->string('Contacto_Emergencia_Numero', 14); 
                              $table->date('Fecha_Terminacion_Contrato')->nullable(); 
                              $table->string('ID_Usr', 16); 
                              $table->foreign('ID_Usr')->references('ID')->on('Usuario')->onDelete('cascade'); 
                            }); 
                              Schema::create('Cliente', function (Blueprint $table) { 

                                $table->unsignedBigInteger('ID')->primary(); 
                                // ID manual asignado, no autoincrement 
                                $table->string('Nombre_Completo', 40); 
                                $table->string('Telefono', 14)->nullable(); 
                                // ahora es opcional
                                 $table->dateTime('Ultima_Visita')->nullable(); 
                                 $table->unsignedInteger('Total_Consumo')->default(0);
                                  $table->timestamp('Fecha_Registro')->useCurrent();
                                   // se asigna automáticamente
                                    $table->string('ID_Usr', 16)->nullable();
                                    $table->foreign('ID_Usr')->references('ID_Usr')->on('Empleado')->onDelete('cascade'); 
                                    
                                }); 
                            } 
                                public function down()
                                 {
                                     Schema::dropIfExists('Cliente');
                                      Schema::dropIfExists('Empleado');
                                       Schema::dropIfExists('Administrador'); 
                                       Schema::dropIfExists('Usuario'); } };
                                    