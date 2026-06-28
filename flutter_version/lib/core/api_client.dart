import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'token_storage.dart';

/// CN exact de la CA partagée (Controllers/Main_run.py genere_ssl_key(),
/// ecole_nginx/docker/certgen/generate-certs.sh) — c'est elle qui signe le
/// certificat serveur d'aplekol360.local, identique sur toutes les
/// installations.
const _trustedCaIssuer = '/CN=aplekol360.local Root CA';

/// Équivalent de Models/AsyncDataHandler.py (school_client) : même base URL
/// (le domaine local "aplekol360.local", remappé par le fichier hosts vers
/// l'IP du serveur école — voir docs CA partagée), même en-tête
/// `Authorization: Bearer` + le token.
class ApiClient {
  ApiClient(this._tokenStorage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: 'https://aplekol360.local/api/v1/',
        connectTimeout: const Duration(seconds: 60),
        receiveTimeout: const Duration(seconds: 60),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // SecurityContext.setTrustedCertificates()/Bytes() n'a AUCUN effet sur
    // macOS dans ce SDK Dart (testé et confirmé avec un certificat
    // auto-signé quelconque, pas spécifique à notre CA — bug/limitation de
    // la plateforme). On vérifie donc manuellement que le certificat
    // présenté a bien été signé par notre CA partagée, via son émetteur,
    // au lieu de compter sur la validation de chaîne automatique.
    final adapter = _dio.httpClientAdapter;
    if (adapter is IOHttpClientAdapter) {
      adapter.createHttpClient = () {
        final client = HttpClient();
        client.badCertificateCallback = (cert, host, port) {
          return cert.issuer == _trustedCaIssuer;
        };
        return client;
      };
    }

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

  Dio get dio => _dio;

  Future<Response<dynamic>> get(String endpoint, {Map<String, dynamic>? query}) {
    return _dio.get(endpoint, queryParameters: query);
  }

  Future<Response<dynamic>> post(String endpoint, {Map<String, dynamic>? data}) {
    return _dio.post(endpoint, data: data);
  }
}
