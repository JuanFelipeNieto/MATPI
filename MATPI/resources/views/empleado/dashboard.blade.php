@extends('layouts.empleado')

@section('title', 'Dashboard Empleado | Matpi')

@section('head')
    <link rel="stylesheet" href="{{ asset('css/cssDashboard.css') }}">
    <link rel="stylesheet" href="{{ asset('css/dropdown.css') }}">
     <link rel="icon" href="{{ asset('img/Favicon.png') }}" />
@endsection

@section('content')
    <section id="dashboard" class="formulario-seccion">
        <div class="dashboard-header">
            <h1>🍔 Dashboard Matpi</h1>
            <p>Panel de control de ventas y estadísticas</p>
        </div>

        {{-- Estadísticas --}}
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🍔</div>
                <div class="stat-number" id="totalVentas">156</div>
                <div class="stat-label">Pedidos del día</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-number" id="ingresos">$234,500</div>
                <div class="stat-label">Ingresos del Mes</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-number" id="clientes">89</div>
                <div class="stat-label">Clientes Atendidos</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🌭</div>
                <div class="stat-number" id="productos">204</div>
                <div class="stat-label">Productos totales</div>
            </div>
        </section>

        {{-- Actividad reciente --}}
        <section class="main-content">
            <div class="content-card">
                <h3 class="content-title">Actividad Reciente</h3>
                <div class="activity-item">
                    <div class="activity-icon">🍔</div>
                    <div class="activity-content">
                        <h4>Nueva orden: Matpi L</h4>
                        <p>Hace 2 minutos</p>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">🚚</div>
                    <div class="activity-content">
                        <h4>Proveedor registrado</h4>
                        <p>Hace 8 minutos</p>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">👤</div>
                    <div class="activity-content">
                        <h4>Cliente nuevo registrado</h4>
                        <p>Hace 12 minutos</p>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">💰</div>
                    <div class="activity-content">
                        <h4>Pago procesado: $25,000</h4>
                        <p>Hace 15 minutos</p>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">🔔</div>
                    <div class="activity-content">
                        <h4>Notificación: Stock bajo</h4>
                        <p>Hace 20 minutos</p>
                    </div>
                </div>
            </div>
        </section>
    </section>

    {{-- Productos más vendidos --}}
    <section class="productos-dashboard">
        <h2>Productos Más Vendidos</h2>
        <div class="producto-lista">
            <div class="producto">
                <img src="{{ asset('img/Triple.jpeg') }}" alt="Matpi L">
                <div class="producto-info">
                    <h3>Matpi L</h3>
                    <p>Tres pisos de sabor..!</p>
                    <div class="producto-ventas">45 vendidas hoy</div>
                </div>
            </div>
            <div class="producto">
                <img src="{{ asset('img/T2.jpeg') }}" alt="Hawaiana X">
                <div class="producto-info">
                    <h3>Hawaiana X</h3>
                    <p>Sencilla pero sabrosa..!</p>
                    <div class="producto-ventas">32 vendidas hoy</div>
                </div>
            </div>
            <div class="producto">
                <img src="{{ asset('img/T3.jpeg') }}" alt="Criolla X">
                <div class="producto-info">
                    <h3>Criolla X</h3>
                    <p>Un poco de maíz criollo..?</p>
                    <div class="producto-ventas">28 vendidas hoy</div>
                </div>
            </div>
        </div>
    </section>

    {{-- Progreso --}}
    <section class="progress-section">
        <div class="progress-card">
            <h3 class="chart-title">Meta Mensual de Ventas</h3>
            <p>$300,000 objetivo</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 78%;"></div>
            </div>
            <p><strong>$234,500</strong> completado (78%)</p>
        </div>
      
        </div>
        <div class="progress-card">
            <h3 class="chart-title">Pedidos Completados</h3>
            <p>200 pedidos meta diaria</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 77%;"></div>
            </div>
            <p><strong>156</strong> pedidos completados</p>
        </div>
    </section>
@endsection
