import sys
import os
import math
import numpy as np
import cv2
import mediapipe as mp

from PySide6.QtWidgets import (
    QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QLabel, QSlider, QMessageBox
)
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QTransform, QColor, QPen, Qt, 
    QBrush, QCursor, QFont
)
from PySide6.QtCore import QPointF, QRectF, Qt


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
# Simple PixmapItem avec gestion d'échelle
# ---------------------------
class SimplePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap: QPixmap, name=None):
        super().__init__(pixmap)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.name = name or ""
        self.original_pixmap = pixmap
        self.current_scale = 1.0
        
    def center_in_scene(self, scene):
        """Centre l'image dans la scène"""
        if scene:
            scene_center = scene.sceneRect().center()
            item_rect = self.boundingRect()
            item_pos = scene_center - item_rect.center()
            self.setPos(item_pos)
    
    def set_scale(self, scale_factor):
        """Redimensionne l'image avec un facteur d'échelle"""
        if self.original_pixmap:
            # Calculer la nouvelle taille
            new_size = self.original_pixmap.size() * scale_factor
            scaled_pixmap = self.original_pixmap.scaled(
                new_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            self.current_scale = scale_factor


# ---------------------------
# Main Editor Widget - VERSION CORRIGÉE
# ---------------------------
class BadgeEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Badge Editor — Recto / Verso avec camera & face crop")
        self.resize(1000, 700)

        # scenes
        self.recto_scene = QGraphicsScene(0, 0, 400, 600)
        self.verso_scene = QGraphicsScene(0, 0, 400, 600)

        # view
        self.view = QGraphicsView(self.recto_scene)
        self.view.setFixedSize(450, 650)
        
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setSceneRect(0, 0, 400, 600)
        self.current_side = "recto"

        # elements
        self.recto_items = {}
        self.verso_items = {}
        self.selection_rect = None
        self.selected_image_item = None
        self.last_slider_value = 100
        
        # Variables pour la sélection manuelle
        self.selection_start = None
        self.is_selecting = False
        self.temp_selection_rect = None
        
        # Mediapipe face detection
        self.mp_face = mp.solutions.face_detection.FaceDetection(
            model_selection=1, 
            min_detection_confidence=0.5
        )

        # UI
        self.setup_ui()
        
        # Init scenes
        self.init_recto()
        self.init_verso()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left panel - view
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Éditeur d'Image"))
        left_panel.addWidget(self.view)
        main_layout.addLayout(left_panel)

        # Right panel - controls
        panel = QVBoxLayout()
        
        # Import section
        import_group = QVBoxLayout()
        import_group.addWidget(QLabel("<b>Importer</b>"))
        
        btn_import = QPushButton("📁 Importer photo (fichier)")
        btn_import.clicked.connect(self.import_photo_file)
        import_group.addWidget(btn_import)

        btn_camera = QPushButton("📷 Prendre photo (caméra)")
        btn_camera.clicked.connect(self.import_from_camera)
        import_group.addWidget(btn_camera)
        
        panel.addLayout(import_group)
        panel.addSpacing(10)

        # Edit section
        edit_group = QVBoxLayout()
        edit_group.addWidget(QLabel("<b>Édition</b>"))
        
        btn_face = QPushButton("👤 Detect & Crop visage")
        btn_face.clicked.connect(self.detect_and_crop_face_of_selected)
        edit_group.addWidget(btn_face)

        btn_selection = QPushButton("⬜ Créer sélection manuelle")
        btn_selection.clicked.connect(self.start_manual_selection)
        edit_group.addWidget(btn_selection)

        btn_crop_manual = QPushButton("✂️ Appliquer crop")
        btn_crop_manual.clicked.connect(self.crop_selected_area)
        edit_group.addWidget(btn_crop_manual)
        
        panel.addLayout(edit_group)
        panel.addSpacing(10)

        # View section
        view_group = QVBoxLayout()
        view_group.addWidget(QLabel("<b>Vue</b>"))
        
        btn_recto = QPushButton("🔄 Afficher recto")
        btn_recto.clicked.connect(self.show_recto)
        view_group.addWidget(btn_recto)

        btn_verso = QPushButton("🔄 Afficher verso")
        btn_verso.clicked.connect(self.show_verso)
        view_group.addWidget(btn_verso)
        
        panel.addLayout(view_group)
        panel.addSpacing(10)

        # Transform section
        transform_group = QVBoxLayout()
        transform_group.addWidget(QLabel("<b>Transformation</b>"))
        
        hrot = QHBoxLayout()
        rleft = QPushButton("⟲ -15°")
        rleft.clicked.connect(lambda: self.rotate_selected(-15))
        rright = QPushButton("⟳ +15°")
        rright.clicked.connect(lambda: self.rotate_selected(15))
        hrot.addWidget(rleft)
        hrot.addWidget(rright)
        transform_group.addLayout(hrot)

        transform_group.addWidget(QLabel("Échelle:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 300)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.scale_selected_from_slider)
        transform_group.addWidget(self.scale_slider)
        
        panel.addLayout(transform_group)
        panel.addSpacing(10)

        # Export section
        export_group = QVBoxLayout()
        export_group.addWidget(QLabel("<b>Export</b>"))
        
        save_png_recto = QPushButton("💾 Exporter PNG recto")
        save_png_recto.clicked.connect(lambda: self.export_png(is_recto=True))
        export_group.addWidget(save_png_recto)

        save_png_verso = QPushButton("💾 Exporter PNG verso")
        save_png_verso.clicked.connect(lambda: self.export_png(is_recto=False))
        export_group.addWidget(save_png_verso)

        export_pdf = QPushButton("📄 Exporter PDF (2 pages)")
        export_pdf.clicked.connect(self.export_pdf)
        export_group.addWidget(export_pdf)
        
        panel.addLayout(export_group)
        panel.addStretch()

        main_layout.addLayout(panel)

    def init_recto(self):
        self.recto_scene.setBackgroundBrush(QColor(255, 255, 255))
        
        # Add default photo placeholder
        default_pix = QPixmap(200, 240)
        default_pix.fill(QColor(200, 200, 200))
        photo_item = SimplePixmapItem(default_pix, name="photo")
        photo_item.setPos(100, 60)
        self.recto_scene.addItem(photo_item)
        self.recto_items["photo"] = photo_item

        # Add name placeholder
        txt_pix = QPixmap(300, 40)
        txt_pix.fill(QColor(255, 255, 255))
        painter = QPainter(txt_pix)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(txt_pix.rect(), Qt.AlignCenter, "Nom complet")
        painter.end()
        
        name_item = SimplePixmapItem(txt_pix, name="nom")
        name_item.setPos(50, 320)
        self.recto_scene.addItem(name_item)
        self.recto_items["nom"] = name_item

    def init_verso(self):
        self.verso_scene.setBackgroundBrush(QColor(240, 240, 240))
        
        # QR code placeholder
        qr_pix = QPixmap(200, 200)
        qr_pix.fill(QColor(220, 220, 220))
        painter = QPainter(qr_pix)
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(qr_pix.rect(), Qt.AlignCenter, "QR Code")
        painter.end()
        
        qr_item = SimplePixmapItem(qr_pix, name="qrcode")
        qr_item.setPos(100, 200)
        self.verso_scene.addItem(qr_item)
        self.verso_items["qrcode"] = qr_item

    def show_recto(self):
        self.view.setScene(self.recto_scene)
        self.current_side = "recto"
        self.cleanup_selection()

    def show_verso(self):
        self.view.setScene(self.verso_scene)
        self.current_side = "verso"
        self.cleanup_selection()

    def import_photo_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if not fname:
            return
            
        pix = QPixmap(fname)
        if pix.isNull():
            QMessageBox.warning(self, "Erreur", "Impossible de charger l'image.")
            return
            
        scene = self.recto_scene if self.current_side == "recto" else self.verso_scene
        
        # Nettoyer la sélection existante
        self.cleanup_selection()
        
        # Redimensionner l'image pour qu'elle rentre dans la scène
        scene_rect = scene.sceneRect()
        pix_size = pix.size()
        
        # Calculer le facteur d'échelle pour que l'image rentre
        scale_x = scene_rect.width() * 0.8 / pix_size.width()
        scale_y = scene_rect.height() * 0.8 / pix_size.height()
        scale_factor = min(scale_x, scale_y)
        
        item = SimplePixmapItem(pix, name="imported_photo")
        
        # Appliquer l'échelle initiale
        if scale_factor < 1.0:
            item.set_scale(scale_factor)
        
        # Centrer l'image dans la scène
        item.center_in_scene(scene)
        
        scene.addItem(item)
        scene.clearSelection()
        item.setSelected(True)
        
        # Mettre à jour le slider avec l'échelle actuelle
        slider_value = int(scale_factor * 100) if scale_factor < 1.0 else 100
        self.scale_slider.setValue(slider_value)
        self.last_slider_value = slider_value
        
        QMessageBox.information(self, "Info", 
            f"Image importée: {pix_size.width()}x{pix_size.height()} pixels\n"
            f"Affichée à: {int(pix_size.width() * scale_factor)}x{int(pix_size.height() * scale_factor)} pixels")

    def import_from_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            # Try different camera indices
            for i in range(5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    break
                    
        if not cap.isOpened():
            QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir la caméra.")
            return
            
        # Create a simple dialog for camera capture
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
        dialog = QDialog(self)
        dialog.setWindowTitle("Capture Caméra")
        layout = QVBoxLayout(dialog)
        label = QLabel("Appuyez sur 'C' pour capturer ou 'Echap' pour annuler")
        layout.addWidget(label)
        dialog.resize(400, 300)
        
        def capture_frame():
            ret, frame = cap.read()
            if ret:
                # Convert to QPixmap
                pix = cv2_to_qpixmap(frame)
                scene = self.recto_scene if self.current_side == "recto" else self.verso_scene
                
                # Nettoyer la sélection existante
                self.cleanup_selection()
                
                # Redimensionner l'image pour qu'elle rentre dans la scène
                scene_rect = scene.sceneRect()
                pix_size = pix.size()
                
                # Calculer le facteur d'échelle
                scale_x = scene_rect.width() * 0.8 / pix_size.width()
                scale_y = scene_rect.height() * 0.8 / pix_size.height()
                scale_factor = min(scale_x, scale_y)
                
                item = SimplePixmapItem(pix, name="camera_photo")
                
                # Appliquer l'échelle initiale
                if scale_factor < 1.0:
                    item.set_scale(scale_factor)
                
                # Centrer l'image dans la scène
                item.center_in_scene(scene)
                
                scene.addItem(item)
                scene.clearSelection()
                item.setSelected(True)
                
                # Mettre à jour le slider
                slider_value = int(scale_factor * 100) if scale_factor < 1.0 else 100
                self.scale_slider.setValue(slider_value)
                self.last_slider_value = slider_value
            cap.release()
            dialog.accept()
        
        # Start a timer to update the camera view
        from PySide6.QtCore import QTimer
        timer = QTimer(dialog)
        
        def update_camera():
            ret, frame = cap.read()
            if ret:
                # Display in dialog
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                label.setPixmap(QPixmap.fromImage(qimg).scaled(
                    400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
        
        timer.timeout.connect(update_camera)
        timer.start(30)  # ~30 FPS
        
        # Set up key press event
        def key_press(event):
            if event.key() == Qt.Key_C:
                capture_frame()
            elif event.key() == Qt.Key_Escape:
                cap.release()
                dialog.reject()
        
        dialog.keyPressEvent = key_press
        dialog.exec()
        
        # Cleanup
        if cap.isOpened():
            cap.release()

    def rotate_selected(self, degrees):
        scene = self.view.scene()
        items = scene.selectedItems()
        if not items:
            QMessageBox.information(self, "Info", "Sélectionnez d'abord un élément.")
            return
            
        for item in items:
            if isinstance(item, (SimplePixmapItem, QGraphicsPixmapItem)):
                t = QTransform(item.transform())
                t.rotate(degrees)
                item.setTransform(t)

    def scale_selected_from_slider(self, value_percent):
        scene = self.view.scene()
        items = scene.selectedItems()
        if not items:
            return
            
        scale_factor = value_percent / 100.0
        
        for item in items:
            if isinstance(item, SimplePixmapItem):
                # Utiliser la méthode set_scale de SimplePixmapItem
                item.set_scale(scale_factor)
                
                # Centrer l'image après redimensionnement
                scene_center = scene.sceneRect().center()
                item_rect = item.boundingRect()
                item_pos = scene_center - item_rect.center()
                item.setPos(item_pos)
                
                # Mettre à jour la valeur du slider
                self.last_slider_value = value_percent

    def start_manual_selection(self):
        """Démarre le mode sélection manuelle"""
        scene = self.view.scene()
        items = scene.selectedItems()
        
        if not items:
            QMessageBox.information(self, "Info", "Sélectionnez d'abord une image.")
            return
            
        item = items[0]
        if not isinstance(item, (SimplePixmapItem, QGraphicsPixmapItem)):
            QMessageBox.warning(self, "Erreur", "L'élément sélectionné n'est pas une image.")
            return
        
        # Nettoyer l'ancienne sélection
        self.cleanup_selection()
        
        # Stocker l'image sélectionnée
        self.selected_image_item = item
        
        # Activer le mode sélection manuelle
        self.is_selecting = True
        
        # Créer un rectangle temporaire
        self.temp_selection_rect = QGraphicsRectItem()
        self.temp_selection_rect.setPen(QPen(QColor(0, 255, 0), 2, Qt.DashLine))
        self.temp_selection_rect.setBrush(QBrush(QColor(0, 255, 0, 30)))
        scene.addItem(self.temp_selection_rect)
        
        # Installer un event filter sur la vue
        self.view.viewport().installEventFilter(self)
        
        QMessageBox.information(self, "Info", 
            "Mode sélection activé. Cliquez et tirez POUR DESSINER UN RECTANGLE SUR L'IMAGE. "
            "Puis cliquez sur 'Appliquer crop'.\n\n"
            "⚠️ IMPORTANT: Dessinez le rectangle DIRECTEMENT SUR L'IMAGE, pas ailleurs!")

    def eventFilter(self, obj, event):
        """Gère les événements de souris pour la sélection manuelle"""
        if obj == self.view.viewport() and self.is_selecting:
            if event.type() == event.Type.MouseButtonPress:
                # Début de la sélection
                self.selection_start = self.view.mapToScene(event.pos())
                self.temp_selection_rect.setRect(QRectF(self.selection_start, self.selection_start))
                return True
                
            elif event.type() == event.Type.MouseMove and self.selection_start:
                # Mise à jour du rectangle pendant le drag
                current_pos = self.view.mapToScene(event.pos())
                rect = QRectF(self.selection_start, current_pos).normalized()
                self.temp_selection_rect.setRect(rect)
                return True
                
            elif event.type() == event.Type.MouseButtonRelease and self.selection_start:
                # Fin de la sélection
                current_pos = self.view.mapToScene(event.pos())
                self.selection_rect = QRectF(self.selection_start, current_pos).normalized()
                self.selection_start = None
                
                # Afficher un message avec les dimensions
                if self.selection_rect:
                    QMessageBox.information(self, "Sélection créée", 
                        f"Zone sélectionnée: {self.selection_rect.width():.1f} x {self.selection_rect.height():.1f} pixels\n"
                        f"Position: ({self.selection_rect.x():.1f}, {self.selection_rect.y():.1f})\n\n"
                        "Cliquez sur 'Appliquer crop' pour recadrer l'image.")
                return True
        
        return super().eventFilter(obj, event)

    def cleanup_selection(self):
        """Nettoie la sélection"""
        self.is_selecting = False
        self.selection_start = None
        self.selected_image_item = None
        
        # Retirer l'event filter
        if self.view.viewport():
            self.view.viewport().removeEventFilter(self)
        
        # Supprimer le rectangle temporaire
        if self.temp_selection_rect:
            scene = self.view.scene()
            if scene and self.temp_selection_rect in scene.items():
                scene.removeItem(self.temp_selection_rect)
            self.temp_selection_rect = None
        
        self.selection_rect = None

    def crop_selected_area(self):
        if not self.selection_rect or not self.selected_image_item:
            QMessageBox.information(self, "Info", "Créez d'abord une zone de sélection sur une image.")
            return
            
        scene = self.view.scene()
        item = self.selected_image_item
        
        if not isinstance(item, SimplePixmapItem):
            QMessageBox.warning(self, "Erreur", "L'élément sélectionné n'est pas une image SimplePixmapItem.")
            return
        
        print(f"Sélection dans scène: {self.selection_rect}")
        print(f"Position de l'image: {item.pos()}")
        print(f"Taille de l'image affichée: {item.boundingRect()}")
        print(f"Échelle actuelle: {item.current_scale}")
        
        # Vérifier si la sélection intersecte avec l'image
        item_scene_rect = item.mapRectToScene(item.boundingRect())
        print(f"Image dans scène: {item_scene_rect}")
        
        if not self.selection_rect.intersects(item_scene_rect):
            QMessageBox.warning(self, "Erreur", 
                "La zone de sélection ne touche pas l'image!\n\n"
                "Dessinez le rectangle DIRECTEMENT SUR L'IMAGE SVP.")
            return
        
        # Intersection entre la sélection et l'image
        intersection = self.selection_rect.intersected(item_scene_rect)
        if intersection.isEmpty():
            QMessageBox.warning(self, "Erreur", "La zone de sélection est hors de l'image.")
            return
        
        print(f"Intersection: {intersection}")
        
        # Convertir l'intersection en coordonnées locales de l'item
        selection_item_rect = item.mapFromScene(intersection).boundingRect()
        print(f"Sélection dans item (coords locales): {selection_item_rect}")
        
        # Obtenir le pixmap ORIGINAL (pas redimensionné)
        if not hasattr(item, 'original_pixmap') or item.original_pixmap.isNull():
            QMessageBox.warning(self, "Erreur", "Image originale non disponible.")
            return
        
        original_pixmap = item.original_pixmap
        print(f"Taille originale: {original_pixmap.width()}x{original_pixmap.height()}")
        
        # Convertir en QImage pour le recadrage
        qimg = original_pixmap.toImage()
        
        # Calculer le facteur d'échelle inverse
        if item.current_scale <= 0:
            QMessageBox.warning(self, "Erreur", "Facteur d'échelle invalide.")
            return
        
        scale_inverse = 1.0 / item.current_scale
        print(f"Facteur d'échelle inverse: {scale_inverse}")
        
        # Convertir les coordonnées locales en coordonnées de l'image originale
        original_x = int(selection_item_rect.x() * scale_inverse)
        original_y = int(selection_item_rect.y() * scale_inverse)
        original_width = int(selection_item_rect.width() * scale_inverse)
        original_height = int(selection_item_rect.height() * scale_inverse)
        
        print(f"Coordonnées originales: x={original_x}, y={original_y}, w={original_width}, h={original_height}")
        
        # S'assurer que le rectangle est dans les limites de l'image
        if (original_x < 0 or original_y < 0 or 
            original_x + original_width > qimg.width() or 
            original_y + original_height > qimg.height()):
            QMessageBox.warning(self, "Erreur", 
                "La zone de sélection dépasse les limites de l'image.")
            return
        
        # Assurer des dimensions positives
        if original_width <= 0 or original_height <= 0:
            QMessageBox.warning(self, "Erreur", f"Dimensions invalides: {original_width}x{original_height}")
            return
        
        # Effectuer le recadrage
        try:
            print(f"Recadrage sur image originale de taille {qimg.width()}x{qimg.height()}")
            cropped_img = qimg.copy(original_x, original_y, original_width, original_height)
            if cropped_img.isNull():
                QMessageBox.warning(self, "Erreur", "Échec du recadrage (image résultante vide).")
                return
            print(f"Recadrage réussi: {cropped_img.width()}x{cropped_img.height()}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors du recadrage: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # Mettre à jour l'item avec l'image recadrée
        item.original_pixmap = QPixmap.fromImage(cropped_img)
        
        # Réappliquer l'échelle actuelle à la nouvelle image
        item.set_scale(item.current_scale)
        
        # Centrer l'image recadrée
        scene_center = scene.sceneRect().center()
        item_rect = item.boundingRect()
        item_pos = scene_center - item_rect.center()
        item.setPos(item_pos)
        
        # Réinitialiser le slider d'échelle à 100%
        self.scale_slider.setValue(100)
        item.current_scale = 1.0
        self.last_slider_value = 100
        
        # Nettoyer la sélection
        self.cleanup_selection()
        
        QMessageBox.information(self, "Succès", 
            f"Image recadrée: {original_width}x{original_height} pixels\n"
            f"Affichée à: {int(original_width * item.current_scale)}x{int(original_height * item.current_scale)} pixels")

    def detect_and_crop_face_of_selected(self):
        scene = self.view.scene()
        items = scene.selectedItems()
        
        if not items:
            QMessageBox.information(self, "Info", "Sélectionnez d'abord une image.")
            return
            
        item = items[0]
        if not isinstance(item, SimplePixmapItem):
            QMessageBox.warning(self, "Erreur", "L'élément sélectionné n'est pas une image SimplePixmapItem.")
            return
        
        # Nettoyer la sélection existante
        self.cleanup_selection()
        
        # Get ORIGINAL pixmap
        if not hasattr(item, 'original_pixmap') or item.original_pixmap.isNull():
            QMessageBox.warning(self, "Erreur", "Image originale non disponible.")
            return
        
        original_pixmap = item.original_pixmap
        
        # Convert to QImage then to numpy array
        qimg = original_pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        
        # Get image data
        ptr = qimg.constBits()
        if ptr is None:
            QMessageBox.warning(self, "Erreur", "Impossible de lire les données de l'image.")
            return
        
        ptr.setsize(qimg.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        # Convert to BGR for OpenCV
        cv_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        
        # Detect faces
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        results = self.mp_face.process(rgb_img)
        
        if not results.detections:
            QMessageBox.information(self, "Info", "Aucun visage détecté.")
            return
        
        # Get first face
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        
        # Calculate face rectangle
        x = int(bbox.xmin * width)
        y = int(bbox.ymin * height)
        w = int(bbox.width * width)
        h = int(bbox.height * height)
        
        # Add margin (30% of max dimension)
        margin = int(0.3 * max(w, h))
        
        # Ensure within bounds
        x0 = max(0, x - margin)
        y0 = max(0, y - margin)
        x1 = min(width, x + w + margin)
        y1 = min(height, y + h + margin)
        
        # Crop image
        cropped = cv_img[y0:y1, x0:x1]
        
        if cropped.size == 0:
            QMessageBox.warning(self, "Erreur", "Le recadrage a échoué.")
            return
        
        # Convert back to QPixmap
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        h2, w2, _ = cropped_rgb.shape
        qimg2 = QImage(cropped_rgb.data, w2, h2, 3 * w2, QImage.Format_RGB888)
        
        # Update the item with cropped image
        item.original_pixmap = QPixmap.fromImage(qimg2.copy())
        item.set_scale(item.current_scale)  # Reapply current scale
        
        # Center the cropped image
        scene_center = scene.sceneRect().center()
        item_rect = item.boundingRect()
        item_pos = scene_center - item_rect.center()
        item.setPos(item_pos)
        
        # Reset scale slider to 100%
        self.scale_slider.setValue(100)
        item.current_scale = 1.0
        self.last_slider_value = 100
        
        QMessageBox.information(self, "Succès", 
            f"Visage détecté et recadré: {w2}x{h2} pixels\n"
            f"Affichée à: {int(w2 * item.current_scale)}x{int(h2 * item.current_scale)} pixels")

    def export_png(self, is_recto=True):
        scene = self.recto_scene if is_recto else self.verso_scene
        
        # High resolution export
        scale_factor = 3  # 3x resolution
        width = int(scene.width() * scale_factor)
        height = int(scene.height() * scale_factor)
        
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.white)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.scale(scale_factor, scale_factor)
        scene.render(painter)
        painter.end()
        
        # Get filename
        default_name = "recto_export.png" if is_recto else "verso_export.png"
        fname, _ = QFileDialog.getSaveFileName(
            self, "Exporter PNG", default_name,
            "PNG Images (*.png);;All Files (*)"
        )
        
        if fname:
            if not fname.lower().endswith('.png'):
                fname += '.png'
            image.save(fname, "PNG", 100)  # 100% quality
            QMessageBox.information(self, "Succès", f"Image exportée : {fname}")

    def export_pdf(self):
        try:
            from PySide6.QtPdf import QPdfWriter
            from PySide6.QtCore import QPageSize
        except ImportError:
            QMessageBox.warning(
                self, "Erreur", 
                "Le module PDF n'est pas disponible. Installez PySide6 avec support PDF."
            )
            return
        
        fname, _ = QFileDialog.getSaveFileName(
            self, "Exporter PDF", "badge.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not fname:
            return
            
        if not fname.lower().endswith('.pdf'):
            fname += '.pdf'
        
        # Create PDF writer
        pdf_writer = QPdfWriter(fname)
        pdf_writer.setResolution(300)  # 300 DPI
        pdf_writer.setPageSize(QPageSize(QPageSize.A4))
        
        painter = QPainter(pdf_writer)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Export recto
        self.export_scene_to_painter(self.recto_scene, painter, pdf_writer)
        pdf_writer.newPage()
        
        # Export verso
        self.export_scene_to_painter(self.verso_scene, painter, pdf_writer)
        
        painter.end()
        
        QMessageBox.information(self, "Succès", f"PDF exporté : {fname}")
    
    def export_scene_to_painter(self, scene, painter, pdf_writer):
        """Helper to render scene to painter with proper scaling."""
        from PySide6.QtPdf import QPdfWriter
        page_rect = pdf_writer.pageRect(QPdfWriter.Point)
        scene_rect = scene.sceneRect()
        
        # Calculate scaling to fit page
        scale_x = page_rect.width() / scene_rect.width()
        scale_y = page_rect.height() / scene_rect.height()
        scale = min(scale_x, scale_y) * 0.9  # 90% to add margins
        
        # Center on page
        offset_x = (page_rect.width() - scene_rect.width() * scale) / 2
        offset_y = (page_rect.height() - scene_rect.height() * scale) / 2
        
        painter.save()
        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)
        scene.render(painter)
        painter.restore()

    def closeEvent(self, event):
        """Clean up resources when closing"""
        self.cleanup_selection()
        super().closeEvent(event)


 