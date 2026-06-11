@extends('layouts.admin')

@section('title', 'Cambiar Contraseña | Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/perfil.css') }}">

<section class="formulario-seccion">
    <h1>Cambiar Contraseña</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    @if($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <form action="{{ route('administrador.perfil.password.update') }}" method="POST">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label for="password_actual">Contraseña actual</label>
            <div class="input-group">
                <input type="password" name="password_actual" id="password_actual" required>
                <button type="button" class="toggle-password" onclick="togglePassword('password_actual', this)">👁️</button>
            </div>
        </div>

      <div class="form-group">
    <label for="password">Nueva contraseña</label>
    <div class="input-group">
        <input type="password" name="password" id="password" required>
        <button type="button" class="toggle-password" onclick="togglePassword('password', this)">👁️</button>
    </div>
</div>

<div class="form-group">
    <label for="password_confirmation">Confirmar nueva contraseña</label>
    <div class="input-group">
        <input type="password" name="password_confirmation" id="password_confirmation" required>
        <button type="button" class="toggle-password" onclick="togglePassword('password_confirmation', this)">👁️</button>
    </div>
</div>


        <button type="submit" class="btn btn-guardar">Actualizar Contraseña</button>
    </form>
</section>

{{-- Script para mostrar/ocultar contraseña --}}
<script>
function togglePassword(id, btn) {
    const input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
        btn.textContent = "🙈"; // icono cuando se ve
    } else {
        input.type = "password";
        btn.textContent = "👁️"; // icono cuando está oculto
    }
}
</script>
@endsection
