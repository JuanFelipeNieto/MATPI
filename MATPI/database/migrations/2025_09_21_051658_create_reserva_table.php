<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('Reservas', function (Blueprint $table) {
            $table->id(); // ID autoincremental
            $table->dateTime('Fecha');
            $table->boolean('Estado');
            $table->text('Observaciones')->nullable();
            $table->unsignedBigInteger('ID_Usr'); // referencia al cliente
            $table->string('registrado_por'); // nombre del usuario que registra la reserva
            $table->timestamps();

            // Llave foránea a Cliente
            $table->foreign('ID_Usr')
                  ->references('ID')->on('Cliente')
                  ->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('Reservas');
    }
};
