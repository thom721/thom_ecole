<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title inertia>{{ config('app.name', 'Infini-software') }}</title>
 

        <meta property="og:title" content="Infini Software - Solutions numériques sur mesure et hybrides">
        <meta property="og:description" content="Infini Software développe des applications web, mobiles et desktop personnalisées, locales ou en ligne, avec synchronisation en temps réel. Des solutions robustes, adaptées à votre métier, accompagnées de formation et de support continu.">
{{-- <meta property="og:image" content="{{ rtrim(config('app.APP_URL', 'https://infini-software.cloud'), '/') }}/images/logo.png"> --}}

<meta property="og:url" content="{{ config('app.APP_URL', 'https://infini-software.cloud') }}">

  
        <meta property="og:image" content="{{ rtrim(config('app.APP_URL', 'https://infini-software.cloud'), '/') }}/images/logo.png">
 

        <meta property="og:url" content="https://infini-software.cloud">
        <meta property="og:type" content="website">
    
        
        <link rel="shortcut icon" href="{{ asset('images/favicon.ico') }}">

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css">

        <!-- Scripts -->
        @routes
        @vite(['resources/js/app.js', "resources/js/Pages/{$page['component']}.vue"])
        @inertiaHead
    </head>
    <body class="font-sans antialiased h-screen itim">
        @inertia
    </body>
</html>
