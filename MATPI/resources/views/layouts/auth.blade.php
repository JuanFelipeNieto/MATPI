<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Descubre las mejores hamburguesas de Matpi. Productos destacados, calidad y sabor garantizado." />
    <meta name="keywords" content="hamburguesas, comida rápida, matpi, destacados" />
    <title>@yield('title', 'Matpi')</title>
    <link rel="icon" href="{{ asset('img/Favicon.png') }}" />
    <!-- Aquí puedes agregar tus archivos CSS -->
    <link rel="stylesheet" href="{{ asset('css/style1.css') }}">
    <!-- Bootstrap CSS (opcional, si quieres usarlo) -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    @stack('styles')
</head>

<body>
    <div id="app">
        @yield('content')
    </div>

    <!-- Scripts JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    @stack('scripts')
</body>

</html>