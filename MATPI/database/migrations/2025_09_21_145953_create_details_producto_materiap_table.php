<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('details_producto_materiap', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            $table->unsignedSmallInteger('producto_id');
            $table->unsignedSmallInteger('materiaprima_id');
            $table->unsignedSmallInteger('cantidad_usada');
            $table->primary(['producto_id', 'materiaprima_id']);

            $table->foreign('producto_id')
                  ->references('id')
                  ->on('producto')
                  ->onDelete('cascade')
                  ->onUpdate('cascade');

            $table->foreign('materiaprima_id')
                  ->references('id')
                  ->on('materia_prima')
                  ->onDelete('cascade')
                  ->onUpdate('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('details_producto_materiap');
    }
};


