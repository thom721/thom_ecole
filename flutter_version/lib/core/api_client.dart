import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'token_storage.dart';

/// CN exact de la CA partagée (Controllers/Main_run.py genere_ssl_key(),
/// ecole_nginx/docker/certgen/generate-certs.sh) — c'est elle qui signe le
/// certificat serveur d'aplekol360.local, identique sur toutes les
/// installations.
const _trustedCaIssuer = '/CN=aplekol360.local Root CA';

/// Base URL par défaut — serveur sur le réseau local, résolu via
/// aplekol360.local remappé par le fichier hosts (voir IpStorage).
const _localBaseUrl = 'https://aplekol360.local/api/v1/';

/// Équivalent de Models/AsyncDataHandler.py (school_client) : même base URL
/// (le domaine local "aplekol360.local", remappé par le fichier hosts vers
/// l'IP du serveur école — voir docs CA partagée), même en-tête
/// `Authorization: Bearer` + le token.
///
/// Deux modes de connexion, choisis explicitement par l'utilisateur sur
/// l'écran de connexion (jamais déduits automatiquement d'une saisie) :
/// - **Local** (par défaut) : aplekol360.local + validation manuelle du
///   certificat auto-signé de la CA partagée de l'école (voir
///   [_trustedCaIssuer]) — la validation de chaîne standard ne peut pas
///   fonctionner ici, ce certificat n'est signé par aucune autorité publique.
/// - **Cloud** : une URL fournie par l'utilisateur (serveur distant faisant
///   tourner le même backend), avec la validation TLS STANDARD (chaîne de
///   certification publique) — surtout PAS le contournement ci-dessus, qui
///   rejetterait à tort un vrai certificat public.
class ApiClient {
  ApiClient(this._tokenStorage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: _localBaseUrl,
        connectTimeout: const Duration(seconds: 60),
        receiveTimeout: const Duration(seconds: 60),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    useLocalServer();

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _tokenStorage.getToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );
  }

  final TokenStorage _tokenStorage;
  late final Dio _dio;
  bool _isCloudMode = false;

  Dio get dio => _dio;
  bool get isCloudMode => _isCloudMode;

  /// Bascule sur le serveur local (aplekol360.local) — comportement
  /// d'origine, avec la validation manuelle du certificat auto-signé.
  ///
  /// SecurityContext.setTrustedCertificates()/Bytes() n'a AUCUN effet sur
  /// macOS dans ce SDK Dart (testé et confirmé avec un certificat
  /// auto-signé quelconque, pas spécifique à notre CA — bug/limitation de
  /// la plateforme). On vérifie donc manuellement que le certificat
  /// présenté a bien été signé par notre CA partagée, via son émetteur,
  /// au lieu de compter sur la validation de chaîne automatique.
  void useLocalServer() {
    _isCloudMode = false;
    _dio.options.baseUrl = _localBaseUrl;
    _dio.httpClientAdapter = IOHttpClientAdapter()
      ..createHttpClient = () {
        final client = HttpClient();
        client.badCertificateCallback = (cert, host, port) {
          return cert.issuer == _trustedCaIssuer;
        };
        return client;
      };
  }

  /// Bascule sur un serveur distant (même backend, hébergé ailleurs) —
  /// validation TLS standard, un nouvel [IOHttpClientAdapter] par défaut
  /// (sans le `badCertificateCallback` du mode local) pour ne jamais
  /// rejeter un vrai certificat public par erreur.
  ///
  /// [rawUrl] doit être le chemin COMPLET de l'API telle qu'exposée par ce
  /// serveur précis — n'ajoute JAMAIS `api/v1/` automatiquement (seule
  /// normalisation : un unique slash de fin). Un hébergement mutualisé
  /// entre plusieurs écoles peut très bien exposer un préfixe propre à
  /// l'établissement au lieu de `/api/v1/` (constaté en pratique :
  /// `ecole_nginx/frontend/.env` pointe vers
  /// "https://admin.institutionlemignon.com/le-mignon", pas "/api/v1") —
  /// deviner ce préfixe casserait silencieusement la connexion.
  void useCloudServer(String rawUrl) {
    _isCloudMode = true;
    var base = rawUrl.trim();
    if (!base.endsWith('/')) base = '$base/';
    _dio.options.baseUrl = base;
    _dio.httpClientAdapter = IOHttpClientAdapter();
  }

  Future<Response<dynamic>> get(
    String endpoint, {
    Map<String, dynamic>? query,
  }) {
    return _dio.get(endpoint, queryParameters: query);
  }

  Future<Response<dynamic>> post(
    String endpoint, {
    Map<String, dynamic>? data,
  }) {
    return _dio.post(endpoint, data: data);
  }

  Future<Response<dynamic>> delete(
    String endpoint, {
    Map<String, dynamic>? query,
  }) {
    return _dio.delete(endpoint, queryParameters: query);
  }
}
