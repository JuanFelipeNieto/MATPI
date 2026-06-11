@extends('layouts.auth')

@section('title', 'Inicio Sesión | Matpi')

@section('head')
    <meta name="description" content="Descubre las mejores hamburguesas de Matpi. Productos destacados, calidad y sabor garantizado.">
    <meta name="keywords" content="hamburguesas, comida rápida, matpi, destacados">

    {{-- Favicon --}}
    <link rel="icon" href="{{ asset('img/Favicon.png') }}" />

    {{-- CSS personalizado --}}
    <link rel="stylesheet" href="{{ asset('css/style1.css') }}">
@endsection

@section('content')
<header>
  <img src="{{ asset('img/Matpi.png') }}" alt="Logo" />
</header>

<main>
  <section>
    <div class="logo">
      <img src="{{ asset('img/Logomatpi.png') }}" alt="logo" />
    </div>
    <h2>Bienvenido</h2>

   <form method="POST" action="{{ route('login.post') }}" id="inicio_sesion">
    @csrf {{-- IMPORTANTE: token CSRF --}}
    
    <div class="campo">
        <label for="ID">Usuario</label>
        <input id="ID" type="text" name="ID" placeholder="Ingresa tu número de documento" required
            value="{{ old('ID') }}"
            class="@error('ID') is-invalid @enderror" autofocus>
        @error('ID')
          <span class="invalid-feedback" role="alert"><strong>{{ $message }}</strong></span>
        @enderror
    </div>

   <div class="campo">
    <label for="password">Contraseña</label>
    <div class="input-group">
        <input id="password" type="password" name="password" placeholder="Ingresa tu contraseña" required
            class="@error('password') is-invalid @enderror" autocomplete="current-password">
        <button type="button" class="toggle-password" onclick="togglePassword('password', this)">👁️</button>
    </div>
    @error('password')
      <span class="invalid-feedback" role="alert"><strong>{{ $message }}</strong></span>
    @enderror
</div>

   

    <div class="boton">
        <button type="submit" name="boton">Ingresar</button>
    </div>
</form>

  </section>
</main>

<footer>
  <p>© 2025 Matpi. Todos los derechos reservados.</p>
  <ul class="footer-links">
    <li><a href="{{ url('Policys.html') }}">Política de privacidad</a></li>
    <li><a href="{{ url('Useterms.html') }}">Términos de uso</a></li>
  </ul>

  <div class="social-login">

</footer>
<script>
function togglePassword(id, btn) {
    const input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
        btn.textContent = "🙈";
    } else {
        input.type = "password";
        btn.textContent = "👁️";
    }
}
</script>

@endsection
