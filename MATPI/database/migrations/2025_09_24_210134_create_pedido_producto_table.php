<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('pedido_producto', function (Blueprint $table) {
            $table->id();

            $table->unsignedSmallInteger('pedido_id');   // coincide con pedidos.ID
            $table->unsignedSmallInteger('producto_id'); // coincide con producto.id
            $table->unsignedSmallInteger('cantidad')->default(1);

            $table->timestamps();

            $table->foreign('pedido_id')->references('ID')->on('pedidos')->onDelete('cascade');
            $table->foreign('producto_id')->references('id')->on('producto')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pedido_producto');
    }
};
