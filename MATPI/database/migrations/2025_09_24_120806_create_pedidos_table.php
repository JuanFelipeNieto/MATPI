<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('pedidos', function (Blueprint $table) {
            $table->smallIncrements('ID');
            $table->date('Fecha');
            $table->boolean('Estado');
            $table->unsignedInteger('Valor');
            $table->tinyInteger('Mesa')->nullable();
            $table->tinyInteger('Numero_Personas')->nullable();

            // FK hacia Empleado: tipo string(16) como en tu tabla Empleado
            $table->string('ID_Usr', 16);
            $table->unsignedBigInteger('ID_Reserva')->nullable(); // FK a Reservas
            $table->unsignedBigInteger('ID_Cliente')->nullable(); // FK a Cliente
            $table->timestamps();

            // Claves foráneas
            $table->foreign('ID_Usr')
                  ->references('ID_Usr')->on('Empleado')
                  ->onDelete('cascade');

            $table->foreign('ID_Reserva')
                  ->references('id')->on('Reservas')
                  ->onDelete('set null');

            $table->foreign('ID_Cliente')
                  ->references('ID')->on('Cliente')
                  ->onDelete('set null');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pedidos');
    }
};
