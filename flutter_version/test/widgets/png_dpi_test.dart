import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/widgets/png_dpi.dart';

const _pngSignature = [137, 80, 78, 71, 13, 10, 26, 10];

/// Construit un PNG 1×1 RGB minimal mais VALIDE (compression zlib réelle
/// via `dart:io`'s `ZLibCodec`, pas des octets inventés) — permet de
/// tester `injectPngDpi` sans passer par `dart:ui` (`Image.toByteData`),
/// dont le rendu hors-écran (`Picture.toImage`) ne se termine jamais dans
/// cet environnement d'exécution (confirmé indépendamment de ce fichier).
Uint8List _minimalPng() {
  Uint8List chunk(String type, List<int> data) {
    final typeBytes = type.codeUnits;
    final crcInput = Uint8List.fromList([...typeBytes, ...data]);
    return (BytesBuilder()
          ..add((ByteData(4)..setUint32(0, data.length)).buffer.asUint8List())
          ..add(typeBytes)
          ..add(data)
          ..add(
            (ByteData(4)..setUint32(0, _crc32(crcInput))).buffer.asUint8List(),
          ))
        .toBytes();
  }

  final ihdrData = ByteData(13)
    ..setUint32(0, 1) // largeur
    ..setUint32(4, 1) // hauteur
    ..setUint8(8, 8) // profondeur de bits
    ..setUint8(9, 2) // type de couleur : 2 = RGB vrai
    ..setUint8(10, 0)
    ..setUint8(11, 0)
    ..setUint8(12, 0);

  // Une ligne de balayage : [type de filtre=0, R, G, B].
  final raw = Uint8List.fromList([0, 255, 0, 0]);
  final compressed = ZLibCodec(level: 6).encode(raw);

  final builder = BytesBuilder()
    ..add(_pngSignature)
    ..add(chunk('IHDR', ihdrData.buffer.asUint8List()))
    ..add(chunk('IDAT', compressed))
    ..add(chunk('IEND', const []));
  return builder.toBytes();
}

final List<int> _crcTable = List<int>.generate(256, (n) {
  var c = n;
  for (var k = 0; k < 8; k++) {
    c = (c & 1) != 0 ? (0xEDB88320 ^ (c >> 1)) : (c >> 1);
  }
  return c;
});

int _crc32(List<int> data) {
  var c = 0xFFFFFFFF;
  for (final byte in data) {
    c = _crcTable[(c ^ byte) & 0xFF] ^ (c >> 8);
  }
  return c ^ 0xFFFFFFFF;
}

/// Reparcourt les morceaux PNG (longueur/type/données/CRC) — utilisé pour
/// vérifier la sortie de [injectPngDpi] indépendamment de sa propre
/// implémentation (pas de simple comparaison d'octets attendus).
List<(String type, Uint8List data, int storedCrc)> _parseChunks(Uint8List png) {
  final chunks = <(String, Uint8List, int)>[];
  var offset = 8;
  while (offset < png.length) {
    final view = ByteData.sublistView(png, offset, offset + 4);
    final length = view.getUint32(0);
    final type = String.fromCharCodes(png.sublist(offset + 4, offset + 8));
    final data = png.sublist(offset + 8, offset + 8 + length);
    final crc = ByteData.sublistView(
      png,
      offset + 8 + length,
      offset + 12 + length,
    ).getUint32(0);
    chunks.add((type, data, crc));
    offset += 12 + length;
  }
  return chunks;
}

void main() {
  test(
    'injectPngDpi insère un morceau pHYs valide juste après IHDR, sans toucher au reste',
    () {
      final original = _minimalPng();
      final originalChunks = _parseChunks(original);
      expect(
        originalChunks.map((c) => c.$1),
        ['IHDR', 'IDAT', 'IEND'],
        reason: 'PNG de test correctement construit',
      );

      final withDpi = injectPngDpi(original, dpi: 300);
      final chunks = _parseChunks(withDpi);

      expect(chunks.map((c) => c.$1), ['IHDR', 'pHYs', 'IDAT', 'IEND']);
      expect(
        withDpi.length,
        original.length + 21,
        reason:
            'un morceau pHYs fait exactement 21 octets (4 longueur + 4 type + 9 données + 4 CRC)',
      );

      // IHDR/IDAT/IEND doivent rester BYTE POUR BYTE identiques.
      expect(chunks[0].$2, originalChunks[0].$2);
      expect(chunks[2].$2, originalChunks[1].$2);
      expect(chunks[3].$2, originalChunks[2].$2);

      final physData = chunks[1].$2;
      final pixelsPerMeterX = ByteData.sublistView(physData, 0, 4).getUint32(0);
      final pixelsPerMeterY = ByteData.sublistView(physData, 4, 8).getUint32(0);
      final unit = physData[8];
      // 300 DPI = 300 / 0,0254 m ≈ 11811 pixels par mètre.
      expect(pixelsPerMeterX, 11811);
      expect(pixelsPerMeterY, 11811);
      expect(unit, 1, reason: 'unité = mètre');

      // Le CRC stocké doit être celui qu'un vrai lecteur PNG recalculerait
      // (type + données) — sinon la plupart des lecteurs rejettent le
      // morceau comme corrompu.
      final expectedCrc = _crc32([...'pHYs'.codeUnits, ...physData]);
      expect(chunks[1].$3, expectedCrc);
    },
  );

  test('dpi personnalisé (ex. 150) produit les bons pixels par mètre', () {
    final withDpi = injectPngDpi(_minimalPng(), dpi: 150);
    final physData = _parseChunks(withDpi)[1].$2;
    final pixelsPerMeter = ByteData.sublistView(physData, 0, 4).getUint32(0);
    expect(pixelsPerMeter, 5906); // 150 / 0.0254, arrondi
  });
}
