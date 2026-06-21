Parfait — je te fournis un module complet qui ajoute :

rotation et redimensionnement interactifs des images (poignées visibles quand l’item est sélectionné),

import direct depuis la caméra (capture webcam via OpenCV),

traitement automatique de la photo : détection de visage et crop centré sur le visage (si trouvé),

intégration dans le même éditeur recto/verso déjà vu (création ou remplacement d’un élément photo),

boutons simples pour les actions courantes (importer, détecter/crop, rotate left/right, reset scale).


Le code est prêt à coller dans ton projet PySide6. Il nécessite PySide6 et opencv-python (pip install PySide6 opencv-python).


---

Points importants avant d’exécuter

Assure-toi d’avoir Python 3.8+ et pip install PySide6 opencv-python numpy.

La capture utilise l’index 0 (caméra intégrée). Si tu veux une IP camera, il faudra remplacer cv2.VideoCapture(0) par l’URL RTSP/HTTP.

La détection de visage utilise le cascade Haar inclus dans OpenCV : cv2.data.haarcascades + "haarcascade_frontalface_default.xml" — ça marche hors-ligne si opencv-python est installé.



---

Code complet (éditeur + transformation + camera + face crop)

import sys
import os
import tempfile
import math
import numpy as np
import cv2

from PySide6.QtWidgets import (
    QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QSlider
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QTransform, QColor, QPen, Qt
from PySide6.QtCore import QPointF, QRectF, QSizeF


# ---------------------------
# Utility : convert cv2 image -> QPixmap
# ---------------------------
def cv2_to_qpixmap(cv_img):
    """Convert BGR OpenCV image to QPixmap."""
    height, width = cv_img.shape[:2]
    if cv_img.ndim == 2:
        fmt = QImage.Format_Grayscale8
        img = QImage(cv_img.data, width, height, cv_img.strides[0], fmt)
    else:
        # BGR -> RGB
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img = QImage(rgb.data, width, height, rgb.strides[0], QImage.Format_RGB888)
    return QPixmap.fromImage(img.copy())


# ---------------------------
# TransformablePixmapItem
# - Permet move, resize (coins), rotate (handle haut)
# - Affiche des poignées quand sélectionné
# ---------------------------
class HandleItem(QGraphicsRectItem):
    """Small square handle used for resizing / rotating."""
    def __init__(self, x, y, size=10, role="resize", parent=None):
        super().__init__(-size/2, -size/2, size, size, parent)
        self.setBrush(QColor(255, 255, 255))
        self.setPen(QPen(QColor(0, 0, 0)))
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setZValue(1000)
        self.role = role  # "resize" or "rotate"
        self.setPos(x, y)

class TransformablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap: QPixmap, name=None):
        super().__init__(pixmap)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.name = name or ""
        self.handles = []
        self.handle_size = 10
        self._creating_handles = False
        self._active_handle = None
        self._start_rect = None
        self._start_mouse_pos = None
        self._start_transform = QTransform()
        self._rotating = False
        self.update_handles()

    def boundingRect(self):
        # keep default boundingRect (pixmap's)
        return super().boundingRect()

    def update_handles(self):
        # remove old
        for h in self.handles:
            scene = h.scene()
            if scene:
                scene.removeItem(h)
        self.handles = []

        if not self.isSelected():
            return

        rect = self.boundingRect()
        # corners: top-left, top-right, bottom-right, bottom-left
        corners = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomRight(),
            rect.bottomLeft()
        ]
        # add corner handles
        for pt in corners:
            h = HandleItem(pt.x(), pt.y(), size=self.handle_size, role="resize", parent=self)
            h.setPos(pt)
            h.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
            self.handles.append(h)

        # rotation handle: above center-top
        center_top = QPointF((rect.left() + rect.right()) / 2, rect.top() - 20)
        rh = HandleItem(center_top.x(), center_top.y(), size=self.handle_size + 2, role="rotate", parent=self)
        rh.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        rh.setPos(center_top)
        self.handles.append(rh)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            # update handles when selection changes
            self.update_handles()
        if change == QGraphicsItem.ItemPositionHasChanged:
            # ensure handles follow (they are children, but update anyway)
            self.update_handles()
        return super().itemChange(change, value)

    def hoverMoveEvent(self, event):
        # cursor feedback when hovering handles
        pos = event.position()
        for h in self.handles:
            # map event pos to parent coords
            local = self.mapFromItem(h, 0, 0)
            rect = QRectF(local.x() - self.handle_size, local.y() - self.handle_size,
                          self.handle_size*2, self.handle_size*2)
            if rect.contains(event.pos()):
                if h.role == "rotate":
                    self.setCursor(Qt.OpenHandCursor)
                else:
                    self.setCursor(Qt.SizeFDiagCursor)
                return
        self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        # detect if we pressed a handle (child) - we check proximity
        pos = event.position()
        for h in self.handles:
            # map event pos to parent's coordinates
            hp = self.mapFromItem(h, 0, 0)
            hit_rect = QRectF(hp.x() - self.handle_size, hp.y() - self.handle_size,
                              self.handle_size*2, self.handle_size*2)
            if hit_rect.contains(event.pos()):
                self._active_handle = h
                self._start_rect = QRectF(self.boundingRect())
                self._start_mouse_pos = event.scenePosition()
                self._start_transform = QTransform(self.transform())
                if h.role == "rotate":
                    self._rotating = True
                else:
                    self._rotating = False
                event.accept()
                return
        # else normal drag
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._active_handle is not None:
            cur_scene_pos = event.scenePosition()
            start_scene_pos = self._start_mouse_pos
            delta = cur_scene_pos - start_scene_pos

            if self._rotating:
                # rotation: angle between center and start / current
                center_scene = self.mapToScene(self.boundingRect().center())
                v1 = start_scene_pos - center_scene
                v2 = cur_scene_pos - center_scene
                if v1.manhattanLength() == 0 or v2.manhattanLength() == 0:
                    angle = 0
                else:
                    angle = math.degrees(math.atan2(v2.y(), v2.x()) - math.atan2(v1.y(), v1.x()))
                # apply incremental rotation from start
                t = QTransform(self._start_transform)
                t.rotate(angle)
                self.setTransform(t)
                event.accept()
                return
            else:
                # resizing: compute scale factor based on drag along diagonal from opposite corner
                # determine opposite corner in scene coords
                handle = self._active_handle
                # find index of handle to know opposite corner
                rect = self._start_rect
                # compute local positions of corners
                tl = rect.topLeft()
                tr = rect.topRight()
                br = rect.bottomRight()
                bl = rect.bottomLeft()
                corners = [tl, tr, br, bl]
                # find closest corner to active handle
                # map active handle pos to local coords (we kept handle as child positioned at corner)
                local_handle_pos = QPointF(handle.pos())
                # determine which corner index
                idx = 0
                min_d = float("inf")
                for i, c in enumerate(corners):
                    d = (c - local_handle_pos).manhattanLength()
                    if d < min_d:
                        min_d = d
                        idx = i
                # opposite corner index
                opp_idx = (idx + 2) % 4
                opp_corner = corners[opp_idx]
                # project movement to compute new rect diagonal length ratio
                # convert scene positions
                opp_scene = self.mapToScene(opp_corner)
                start_corner_scene = self.mapToScene(corners[idx])
                start_len = (start_corner_scene - opp_scene).manhattanLength()
                cur_len = (event.scenePosition() - opp_scene).manhattanLength()
                if start_len == 0:
                    scale_factor = 1.0
                else:
                    scale_factor = cur_len / start_len
                # apply uniform scaling about center
                center = self.boundingRect().center()
                t = QTransform()
                t.translate(center.x(), center.y())
                t.scale(scale_factor, scale_factor)
                t.translate(-center.x(), -center.y())
                # combine with any prior rotation existing in start transform
                # apply to start transform by concatenation
                new_t = QTransform(self._start_transform)
                new_t = new_t * t
                self.setTransform(new_t)
                event.accept()
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._active_handle = None
        self._start_rect = None
        self._start_mouse_pos = None
        self._rotating = False
        # update handle positions now that transforms changed
        self.update_handles()
        super().mouseReleaseEvent(event)

    def setPixmap(self, pixmap: QPixmap):
        super().setPixmap(pixmap)
        # whenever pixmap changes, update handles so they are positioned properly
        self.update_handles()


# ---------------------------
# BadgeEditor amélioré avec boutons pour importer / detector / rotate / scale
# ---------------------------
class BadgeEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Badge Editor — Recto / Verso avec camera & face crop")
        self.resize(900, 700)

        # scenes
        self.recto_scene = QGraphicsScene(0, 0, 400, 600)
        self.verso_scene = QGraphicsScene(0, 0, 400, 600)

        # view
        self.view = QGraphicsView(self.recto_scene)
        self.view.setFixedSize(420, 620)
        self.current_side = "recto"

        # elements dicts
        self.recto = {}
        self.verso = {}

        # init scenes with placeholders
        self.init_recto()
        self.init_verso()

        # UI layout
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.view)

        panel = QVBoxLayout()
        main_layout.addLayout(panel)

        btn_import = QPushButton("Importer photo (fichier)")
        btn_import.clicked.connect(self.import_photo_file)
        panel.addWidget(btn_import)

        btn_camera = QPushButton("Prendre photo (caméra)")
        btn_camera.clicked.connect(self.import_from_camera)
        panel.addWidget(btn_camera)

        btn_face = QPushButton("Detect & Crop visage (photo sélectionnée)")
        btn_face.clicked.connect(self.detect_and_crop_face_of_selected)
        panel.addWidget(btn_face)

        btn_recto = QPushButton("Afficher recto")
        btn_recto.clicked.connect(self.show_recto)
        panel.addWidget(btn_recto)

        btn_verso = QPushButton("Afficher verso")
        btn_verso.clicked.connect(self.show_verso)
        panel.addWidget(btn_verso)

        panel.addWidget(QLabel("Rotation rapide"))
        hrot = QHBoxLayout()
        rleft = QPushButton("⟲ -15°")
        rleft.clicked.connect(lambda: self.rotate_selected(-15))
        rright = QPushButton("⟳ +15°")
        rright.clicked.connect(lambda: self.rotate_selected(15))
        hrot.addWidget(rleft); hrot.addWidget(rright)
        panel.addLayout(hrot)

        panel.addWidget(QLabel("Échelle"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 300)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.scale_selected_from_slider)
        panel.addWidget(self.scale_slider)

        save_png_recto = QPushButton("Exporter PNG recto")
        save_png_recto.clicked.connect(lambda: self.export_png(is_recto=True))
        panel.addWidget(save_png_recto)

        save_png_verso = QPushButton("Exporter PNG verso")
        save_png_verso.clicked.connect(lambda: self.export_png(is_recto=False))
        panel.addWidget(save_png_verso)

        export_pdf = QPushButton("Exporter PDF (2 pages)")
        export_pdf.clicked.connect(self.export_pdf)
        panel.addWidget(export_pdf)

        panel.addStretch()

    # ----------------------------
    # Scenes init
    # ----------------------------
    def init_recto(self):
        # simple background (white)
        self.recto_scene.setBackgroundBrush(QColor(255, 255, 255))
        # default photo item
        default_pix = QPixmap(200, 240)
        default_pix.fill(QColor(200, 200, 200))
        photo_item = TransformablePixmapItem(default_pix, name="photo")
        photo_item.setPos(100, 60)
        self.recto_scene.addItem(photo_item)
        self.recto["photo"] = photo_item

        # name and function (text as pixmap for simplicity)
        # We'll use QGraphicsPixmapItem for images and QGraphicsPixmapItem for text as images
        # But we can also use QGraphicsTextItem in a real project. Keep it simple here.
        # Add placeholder text as pixmap
        txt_pix = QPixmap(300, 80)
        txt_pix.fill(QColor(255, 255, 255))
        painter = QPainter(txt_pix)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font())
        painter.drawText(QRectF(0, 0, 300, 80), Qt.AlignLeft | Qt.AlignVCenter, "Nom complet")
        painter.end()
        name_item = TransformablePixmapItem(txt_pix, name="nom")
        name_item.setPos(50, 320)
        self.recto_scene.addItem(name_item)
        name_item.setFlags(name_item.flags() | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.recto["nom"] = name_item

    def init_verso(self):
        self.verso_scene.setBackgroundBrush(QColor(240, 240, 240))
        default_pix = QPixmap(200, 200)
        default_pix.fill(QColor(220, 220, 220))
        qr_item = TransformablePixmapItem(default_pix, name="qrcode")
        qr_item.setPos(100, 200)
        self.verso_scene.addItem(qr_item)
        self.verso["qrcode"] = qr_item

    # ----------------------------
    # Show sides
    # ----------------------------
    def show_recto(self):
        self.view.setScene(self.recto_scene)
        self.current_side = "recto"

    def show_verso(self):
        self.view.setScene(self.verso_scene)
        self.current_side = "verso"

    # ----------------------------
    # Import file
    # ----------------------------
    def import_photo_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not fname:
            return
        pix = QPixmap(fname)
        if pix.isNull():
            print("Impossible de charger l'image.")
            return
        # place as a new TransformablePixmapItem in the current scene
        item = TransformablePixmapItem(pix, name="photo_imported")
        item.setPos(80, 80)
        scene = self.recto_scene if self.current_side == "recto" else self.verso_scene
        scene.addItem(item)

    # ----------------------------
    # Camera import (capture one frame)
    # ----------------------------
    def import_from_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # try DirectShow on Windows; otherwise remove flag
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Impossible d'ouvrir la caméra.")
            return
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("Impossible de capturer depuis la caméra.")
            return
        # convert and create QPixmap
        pix = cv2_to_qpixmap(frame)
        # add to scene as TransformablePixmapItem
        item = TransformablePixmapItem(pix, name="photo_camera")
        item.setPos(80, 80)
        scene = self.recto_scene if self.current_side == "recto" else self.verso_scene
        scene.addItem(item)

    # ----------------------------
    # Face detect & crop for selected TransformablePixmapItem
    # ----------------------------
    def detect_and_crop_face_of_selected(self):
        scene = self.view.scene()
        items = scene.selectedItems()
        if not items:
            print("Sélectionne d'abord un item image à traiter.")
            return
        item = items[0]
        if not isinstance(item, TransformablePixmapItem):
            print("L'item sélectionné n'est pas une image transformable.")
            return
        pix = item.pixmap()
        if pix.isNull():
            print("Pixmap vide.")
            return
        # convert QPixmap -> cv2 image (BGR)
        img_qimage = pix.toImage().convertToFormat(QImage.Format.Format_RGB888)
        width = img_qimage.width()
        height = img_qimage.height()
        ptr = img_qimage.bits()
        ptr.setsize(img_qimage.byteCount())
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        cv_rgb = arr.copy()
        cv_bgr = cv2.cvtColor(cv_rgb, cv2.COLOR_RGB2BGR)

        # face detection
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            print("Aucun visage détecté.")
            return

        # pick largest face (most likely main face)
        faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        x, y, w, h = faces[0]
        # add margin
        margin = int(0.4 * max(w, h))
        cx = x + w // 2
        cy = y + h // 2
        x0 = max(0, cx - (w // 2) - margin)
        y0 = max(0, cy - (h // 2) - margin)
        x1 = min(cv_bgr.shape[1], cx + (w // 2) + margin)
        y1 = min(cv_bgr.shape[0], cy + (h // 2) + margin)

        cropped = cv_bgr[y0:y1, x0:x1]
        if cropped.size == 0:
            print("Erreur lors du crop.")
            return

        # convert back to QPixmap and set to the item (reset transform)
        new_pix = cv2_to_qpixmap(cropped)
        item.setTransform(QTransform())  # reset transform (optionnel)
        item.setPixmap(new_pix)
        print("Visage détecté et recadré.")

    # ----------------------------
    # Rotate selected by degrees
    # ----------------------------
    def rotate_selected(self, degrees):
        scene = self.view.scene()
        items = scene.selectedItems()
        if not items:
            print("Sélectionne un élément d'abord.")
            return
        item = items[0]
        # apply rotation relative to current transform
        t = QTransform(item.transform())
        t.rotate(degrees)
        item.setTransform(t)
        item.update_handles()

    # ----------------------------
    # Scale selected using slider value (percentage)
    # ----------------------------
    def scale_selected_from_slider(self, value_percent):
        scene = self.view.scene()
        items = scene.selectedItems()
        if not items:
            return
        item = items[0]
        # scale relative to base pixmap size (we assume slider 100 => 1.0)
        scale_factor = value_percent / 100.0
        # reset transform then scale (keeps rotation lost; if rotation must be preserved handle accordingly)
        # preserve rotation: extract rotation angle from current transform
        current_t = item.transform()
        # approximate rotation angle from transform
        m11 = current_t.m11()
        m12 = current_t.m12()
        angle = math.degrees(math.atan2(m12, m11)) if (m11 or m12) else 0
        t = QTransform()
        # rotate then scale then translate to keep center
        center = item.boundingRect().center()
        t.translate(center.x(), center.y())
        t.rotate(angle)
        t.scale(scale_factor, scale_factor)
        t.translate(-center.x(), -center.y())
        item.setTransform(t)
        item.update_handles()

    # ----------------------------
    # Export PNG / PDF (like earlier)
    # ----------------------------
    def export_png(self, is_recto=True):
        scene = self.recto_scene if is_recto else self.verso_scene
        # high-resolution scaling: e.g. 300 DPI
        width = int(scene.width() * 3)
        height = int(scene.height() * 3)
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor(255, 255, 255))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # scale painter to increase resolution
        painter.scale(3, 3)
        scene.render(painter)
        painter.end()
        name = "recto_highres.png" if is_recto else "verso_highres.png"
        image.save(name)
        print("Export PNG:", name)

    def export_pdf(self):
        from PySide6.QtPdf import QPdfWriter
        pdf = QPdfWriter("badge_two_pages.pdf")
        pdf.setResolution(300)
        pdf.setPageSize(pdf.PageSize.Letter)  # or set custom with QPageSize
        painter = QPainter(pdf)
        # recto
        self.recto_scene.render(painter)
        pdf.newPage()
        # verso
        self.verso_scene.render(painter)
        painter.end()
        print("Export PDF: badge_two_pages.pdf")


# ---------------------------
# Lancement
# ---------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = BadgeEditorWidget()
    w.show()
    sys.exit(app.exec())


---

Explications / points d’amélioration possibles

Le TransformablePixmapItem ci-dessus propose une implémentation pratique (handles enfants) pour redimensionner uniformément et rotater via handle. C’est volontairement simple — pour un produit pro tu peux :

ajouter des handles indépendants (redimensionnement non uniforme X/Y),

ajouter l’affichage d’un contour ou grille d’alignement,

permettre le redimensionnement par saisie numérique.


Scale slider remplace la mise à l’échelle brute ; il préserve approximativement la rotation.

Import camera : j’ai utilisé cv2.VideoCapture(0) — pour IP camera, remplace 0 par URL (ex: rtsp://...).

Détection de visage : j’utilise Haarcascade (rapide). Pour plus de robustesse (angles, masque, etc.), tu peux intégrer un modèle DNN (face detector) ou une librairie comme mediapipe.

Export : PNG en haute résolution (scaling painter.scale(3,3)) et PDF 300 DPI.



---

Si tu veux, je peux continuer et faire une version améliorée :

handles graphiquement plus jolis, rotation en degrés affichée,

redimensionnement non uniforme et verrouillage d’aspect,

double-clic pour éditer texte (QGraphicsTextItem),

recadrage automatique de la photo pour s’adapter à un cadre prédéfini (ex: ellipse pour photo d’identité),

génération automatique du QR code (depuis une donnée en DB),

connexion exemplaire à ta base SQLite (lecture en lot et génération automatisée).


Tu veux que j’ajoute l’un de ces raffinements maintenant ? lequel en priorité ?