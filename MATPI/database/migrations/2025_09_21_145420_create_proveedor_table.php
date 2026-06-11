<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
       Schema::create('Proveedor', function (Blueprint $table) {
    $table->engine = 'InnoDB';
    $table->smallIncrements('id');
    $table->string('nombre_proveedor', 50);
    $table->string('direccion', 120);
    $table->string('correo_electronico', 35)->nullable();
    $table->string('telefono', 14);
    $table->string('id_usr', 16); // 🔹 ID del usuario (puede ser admin o empleado)
    $table->unsignedSmallInteger('cantidad');
    $table->timestamps();

    $table->foreign('id_usr')
          ->references('ID')   // 🔹 referencia al ID de Usuario
          ->on('Usuario')
          ->onDelete('cascade')
          ->onUpdate('cascade');
});

    }

    public function down(): void
    {
        Schema::dropIfExists('proveedor');
    }
};

