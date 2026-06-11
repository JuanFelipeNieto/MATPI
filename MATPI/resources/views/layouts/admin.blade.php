<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Matpi - Administrador')</title>

 
    <link rel="icon" href="{{ asset('img/Favicon.png') }}" />


    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
            <link rel="stylesheet" href="{{ asset('css/dropdown.css') }}">


    @yield('head')
</head>
<body class="@yield('body-class')">
   
    <header class="header">
        <img src="{{ asset('img/Logomatpi.png') }}" alt="Logo Matpi" class="logo">

        <nav class="top-nav">
            <a href="{{ route('administrador.dashboard') }}" class="nav-link active">🏠 Dashboard</a>
            <a href="{{ route('producto.index') }}" class="nav-link">🍔 Productos</a>
            <a href="{{ route('pedido.index') }}" class="nav-link">📋 Pedidos</a>
             <a href="{{ route('reservas.index') }}" class="nav-link">🪑Reservas</a>
            <a href="{{ route('clientes.index') }}" class="nav-link">👥 Clientes</a>
            <a href="{{ route('administrador.empleados.index') }}" class="nav-link">🧑‍💼 Empleados</a>
            <a href="{{ route('proveedor.index') }}" class="nav-link">🚚 Proveedores</a>
            <a href="{{ route('materia_prima.index') }}" class="nav-link">🥬 Materia Prima</a>
            <a href="#" class="nav-link">💰 Facturas</a>
        </nav>

        <div class="profile-dropdown">
            <button class="profile-btn">👤 {{ Auth::user()->Nombre_Completo }}</button>
            <div class="dropdown-content">
                <a href="{{ route('administrador.perfil') }}">Información de perfil</a>
                <a href="{{ route('logout') }}"
                   onclick="event.preventDefault(); document.getElementById('logout-form').submit();">
                    Cerrar sesión
                </a>
            </div>
        </div>

        <form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
            @csrf
        </form>
    </header>


    <main>
        @yield('content')
    </main>

  
    <footer>
        <p>© 2025 Matpi. Todos los derechos reservados.</p>
        <ul class="footer-links">
            <li><a href="#">Política de privacidad</a></li>
            <li><a href="#">Términos de uso</a></li>
        </ul>
    </footer>


    <script src="{{ asset('js/dropown.js') }}"></script>

</body>
</html>
