<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('producto', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            $table->smallIncrements('id');
            $table->string('nombre_producto', 35);
            $table->tinyText('descripcion')->nullable();
            $table->unsignedSmallInteger('cantidad')->default(0);
            $table->unsignedInteger('valor');
            $table->enum('categoria', [
                'Hamburguesas',
                'Perros',
                'Empanadas',
                'Bebidas',
                'Guarniciones',
                'Especias y Condimentos',
                'Salsas y Aderezos',
                'Otros',
                
            ]);
            $table->string('imagen')->nullable();
            $table->timestamps();

        });
    }

    public function down(): void
    {
        Schema::dropIfExists('producto');
    }
};
