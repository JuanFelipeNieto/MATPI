<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('details_proveedor_materiap', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            
            // 🔹 Clave primaria
            $table->id();

            // 🔹 Llaves foráneas
            $table->unsignedSmallInteger('proveedor_id');
            $table->unsignedSmallInteger('materiaprima_id');

            // 🔹 Datos adicionales
            $table->integer('cantidad'); // cantidad suministrada
            $table->decimal('precio_unitario', 10, 2);
            $table->dateTime('fecha_suministro')->useCurrent();

            // 🔹 Relaciones
            $table->foreign('proveedor_id')
                  ->references('id')
                  ->on('proveedor')
                  ->onDelete('cascade')
                  ->onUpdate('cascade');

            $table->foreign('materiaprima_id')
                  ->references('id')
                  ->on('materia_prima')
                  ->onDelete('cascade')
                  ->onUpdate('cascade');

            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('details_proveedor_materiap');
    }
};
