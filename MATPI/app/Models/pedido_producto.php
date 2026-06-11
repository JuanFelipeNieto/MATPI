<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('pedido_producto', function (Blueprint $table) {
            $table->id(); // id auto incrementable de la tabla pivot
            $table->unsignedBigInteger('pedido_id');   // FK hacia pedidos
            $table->unsignedBigInteger('producto_id'); // FK hacia productos
            $table->integer('cantidad')->default(1);   // cantidad de productos
            $table->timestamps();

            // Definir llaves foráneas
            $table->foreign('pedido_id')->references('ID')->on('pedidos')->onDelete('cascade');
            $table->foreign('producto_id')->references('ID')->on('productos')->onDelete('cascade');

            // Evitar duplicados: un mismo producto no puede repetirse en el mismo pedido
            $table->unique(['pedido_id', 'producto_id']);
        });
    }

    public function down()
    {
        Schema::dropIfExists('pedido_producto');
    }
};
