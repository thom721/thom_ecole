import 'dart:typed_data';

/// Injecte un morceau `pHYs` (résolution physique) dans des octets PNG
/// déjà encodés — `dart:ui`'s `Image.toByteData(format: ImageByteFormat.png)`
/// (utilisé par `badge_renderer.dart`/`badge_layout_renderer.dart`)
/// n'expose aucun moyen de fixer la résolution ; les PNG produits n'ont
/// donc AUCUN morceau `pHYs`, ce qui fait que la plupart des logiciels
/// (Aperçu macOS compris) affichent 72 DPI par défaut — alors que les
/// dimensions en pixels (1013×638, voir `models/badge_layout.dart`) sont
/// calculées pour un rendu net à 300 DPI (8,5×5,1cm). N'affecte PAS les
/// pixels eux-mêmes, seulement la métadonnée de résolution physique lue
/// par les logiciels d'impression/édition.
Uint8List injectPngDpi(Uint8List png, {int dpi = 300}) {
  const signatureLength = 8;
  // 1 pouce = 0,0254 mètre exactement — conversion standard DPI -> pixels
  // par mètre, l'unité attendue par le morceau `pHYs` (spécification PNG).
  final pixelsPerMeter = (dpi / 0.0254).round();

  final physData = ByteData(9)
    ..setUint32(0, pixelsPerMeter)
    ..setUint32(4, pixelsPerMeter)
    ..setUint8(8, 1); // unité = mètre (0 = inconnue, 1 = mètre)
  final physChunk = _buildChunk('pHYs', physData.buffer.asUint8List());

  // IHDR est TOUJOURS le tout premier morceau après la signature PNG, et
  // sa taille de données est FIXE (13 octets : largeur, hauteur, profondeur
  // de bits, type de couleur, compression, filtre, entrelacement — voir la
  // spécification PNG) — sa longueur totale (longueur + type + données +
  // CRC) est donc connue sans avoir à la parser.
  const ihdrChunkTotalLength = 4 + 4 + 13 + 4;
  final insertAt = signatureLength + ihdrChunkTotalLength;

  final result = BytesBuilder()
    ..add(png.sublist(0, insertAt))
    ..add(physChunk)
    ..add(png.sublist(insertAt));
  return result.toBytes();
}

Uint8List _buildChunk(String type, Uint8List data) {
  final typeBytes = Uint8List.fromList(type.codeUnits);
  final crcInput = Uint8List(typeBytes.length + data.length)
    ..setRange(0, typeBytes.length, typeBytes)
    ..setRange(typeBytes.length, typeBytes.length + data.length, data);

  final chunk = BytesBuilder()
    ..add((ByteData(4)..setUint32(0, data.length)).buffer.asUint8List())
    ..add(typeBytes)
    ..add(data)
    ..add((ByteData(4)..setUint32(0, _crc32(crcInput))).buffer.asUint8List());
  return chunk.toBytes();
}

// Table CRC32 standard (IEEE 802.3, celle utilisée par PNG/zlib) —
// construite une seule fois au chargement du fichier.
final List<int> _crcTable = List<int>.generate(256, (n) {
  var c = n;
  for (var k = 0; k < 8; k++) {
    c = (c & 1) != 0 ? (0xEDB88320 ^ (c >> 1)) : (c >> 1);
  }
  return c;
});

int _crc32(Uint8List data) {
  var c = 0xFFFFFFFF;
  for (final byte in data) {
    c = _crcTable[(c ^ byte) & 0xFF] ^ (c >> 8);
  }
  return c ^ 0xFFFFFFFF;
}
