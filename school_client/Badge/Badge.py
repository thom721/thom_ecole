import sys
import os
import numpy as np
import cv2
import mediapipe as mp

from PySide6.QtWidgets import (
    QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QLabel, QSlider, QMessageBox, QFrame
)
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QTransform, QColor, QPen, Qt, 
    QBrush, QFont, QAction
)
from PySide6.QtCore import QPointF, QRectF, Qt

# ---------------------------
# UTILS
# ---------------------------
def cv2_to_qpixmap(cv_img):
    if cv_img is None: return QPixmap()
    height, width = cv_img.shape[:2]
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    img = QImage(rgb.data, width, height, rgb.strides[0], QImage.Format_RGB888)
    return QPixmap.fromImage(img.copy())

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
        self.setTransformOriginPoint(self.boundingRect().center())
        
    def set_scale(self, scale_factor):
        self.current_scale = scale_factor
        if not self.original_pixmap.isNull():
            new_size = self.original_pixmap.size() * scale_factor
            scaled_pixmap = self.original_pixmap.scaled(
                new_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            self.setTransformOriginPoint(self.boundingRect().center())

# ---------------------------
# MAIN EDITOR
# ---------------------------
class BadgeEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Badge Editor Pro — Système Complet")
        self.resize(1200, 800)

        # Scènes
        self.recto_scene = QGraphicsScene(0, 0, 400, 600)
        self.verso_scene = QGraphicsScene(0, 0, 400, 600)
        
        # Historique simple
        self.history = []
        self.redo_stack = []

        # IA
        self.mp_face = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

        # États
        self.is_selecting = False
        self.selection_start = None
        self.temp_selection_rect = None
        self.selected_image_item = None
        
        self.setup_ui()
        self.view.setScene(self.recto_scene)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # --- GAUCHE : VUE ---
        left_layout = QVBoxLayout()
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setFixedSize(420, 620)
        self.view.setStyleSheet("border: 2px solid #333; background-color: #f0f0f0;")
        
        undo_redo_layout = QHBoxLayout()
        self.btn_undo = QPushButton("↩ Annuler")
        self.btn_undo.clicked.connect(self.action_undo)
        self.btn_redo = QPushButton("↪ Rétablir")
        self.btn_redo.clicked.connect(self.action_redo)
        undo_redo_layout.addWidget(self.btn_undo)
        undo_redo_layout.addWidget(self.btn_redo)
        
        left_layout.addWidget(QLabel("<b>APERÇU DU BADGE</b>"))
        left_layout.addWidget(self.view)
        left_layout.addLayout(undo_redo_layout)
        main_layout.addLayout(left_layout)

        # --- DROITE : PANNEAU DE CONTROLE ---
        controls = QVBoxLayout()
        scroll_frame = QFrame()
        ctrl_layout = QVBoxLayout(scroll_frame)

        # Import
        ctrl_layout.addWidget(QLabel("<b>📁 IMPORTATION</b>"))
        btn_file = QPushButton("📁 Image depuis fichier")
        btn_file.clicked.connect(self.action_import_file)
        btn_cam = QPushButton("📷 Capture Caméra")
        btn_cam.clicked.connect(self.action_camera_capture)
        ctrl_layout.addWidget(btn_file)
        ctrl_layout.addWidget(btn_cam)

        # Crop & IA
        ctrl_layout.addWidget(QLabel("<b>✂️ DÉCOUPE & IA</b>"))
        btn_face = QPushButton("👤 Auto-Crop Visage (IA)")
        btn_face.clicked.connect(self.action_auto_face_crop)
        btn_manual = QPushButton("⬜ Tracer zone de Crop")
        btn_manual.clicked.connect(self.action_start_manual_selection)
        btn_apply_crop = QPushButton("✂️ Appliquer le Crop")
        btn_apply_crop.clicked.connect(self.action_apply_manual_crop)
        ctrl_layout.addWidget(btn_face)
        ctrl_layout.addWidget(btn_manual)
        ctrl_layout.addWidget(btn_apply_crop)

        # Transformations
        ctrl_layout.addWidget(QLabel("<b>🔄 TRANSFORMATIONS</b>"))
        ctrl_layout.addWidget(QLabel("Zoom / Échelle :"))
        self.slider_scale = QSlider(Qt.Horizontal)
        self.slider_scale.setRange(5, 300)
        self.slider_scale.setValue(100)
        self.slider_scale.valueChanged.connect(self.action_scale_selected)
        ctrl_layout.addWidget(self.slider_scale)

        h_rot = QHBoxLayout()
        btn_r_left = QPushButton("⟲ -90°")
        btn_r_left.clicked.connect(lambda: self.action_rotate_selected(-90))
        btn_r_right = QPushButton("⟳ +90°")
        btn_r_right.clicked.connect(lambda: self.action_rotate_selected(90))
        h_rot.addWidget(btn_r_left)
        h_rot.addWidget(btn_r_right)
        ctrl_layout.addLayout(h_rot)

        # Calques
        ctrl_layout.addWidget(QLabel("<b>層 ORDRE DES CALQUES</b>"))
        h_layers = QHBoxLayout()
        btn_up = QPushButton("Monter au-dessus")
        btn_up.clicked.connect(self.move_layer_up)
        btn_down = QPushButton("Descendre au-dessous")
        btn_down.clicked.connect(self.move_layer_down)
        h_layers.addWidget(btn_up)
        h_layers.addWidget(btn_down)
        ctrl_layout.addLayout(h_layers)

        # Export & Nav
        ctrl_layout.addSpacing(30)
        btn_recto = QPushButton("🔄 VOIR RECTO")
        btn_recto.clicked.connect(lambda: self.view.setScene(self.recto_scene))
        btn_verso = QPushButton("🔄 VOIR VERSO")
        btn_verso.clicked.connect(lambda: self.view.setScene(self.verso_scene))
        btn_pdf = QPushButton("📄 GÉNÉRER PDF FINAL")
        btn_pdf.setStyleSheet("background-color: #2e7d32; color: white; height: 40px; font-weight: bold;")
        btn_pdf.clicked.connect(self.action_export_pdf)
        
        ctrl_layout.addWidget(btn_recto)
        ctrl_layout.addWidget(btn_verso)
        ctrl_layout.addWidget(btn_pdf)

        controls.addWidget(scroll_frame)
        main_layout.addLayout(controls)

    # --- LOGIQUE ---
    def action_import_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.add_image_item(QPixmap(path))

    def action_camera_capture(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            self.add_image_item(cv2_to_qpixmap(frame))
        cap.release()

    def add_image_item(self, pixmap):
        if pixmap.isNull(): return
        item = SimplePixmapItem(pixmap)
        self.view.scene().addItem(item)
        item.setPos(50, 50)
        self.view.scene().clearSelection()
        item.setSelected(True)

    def action_scale_selected(self, val):
        for item in self.view.scene().selectedItems():
            if isinstance(item, SimplePixmapItem):
                item.set_scale(val / 100.0)

    def action_rotate_selected(self, angle):
        for item in self.view.scene().selectedItems():
            item.setRotation(item.rotation() + angle)

    def move_layer_up(self):
        for item in self.view.scene().selectedItems():
            item.setZValue(item.zValue() + 1)

    def move_layer_down(self):
        for item in self.view.scene().selectedItems():
            item.setZValue(item.zValue() - 1)

    # --- CROP MANUEL ---
    def action_start_manual_selection(self):
        items = self.view.scene().selectedItems()
        if not items: return
        self.selected_image_item = items[0]
        self.is_selecting = True
        self.temp_selection_rect = QGraphicsRectItem()
        self.temp_selection_rect.setPen(QPen(Qt.yellow, 2, Qt.DashLine))
        self.view.scene().addItem(self.temp_selection_rect)
        self.view.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.is_selecting and obj == self.view.viewport():
            if event.type() == event.Type.MouseButtonPress:
                self.selection_start = self.view.mapToScene(event.pos())
            elif event.type() == event.Type.MouseMove and self.selection_start:
                pos = self.view.mapToScene(event.pos())
                self.temp_selection_rect.setRect(QRectF(self.selection_start, pos).normalized())
            elif event.type() == event.Type.MouseButtonRelease:
                self.is_selecting = False
                self.view.viewport().removeEventFilter(self)
        return super().eventFilter(obj, event)

    def action_apply_manual_crop(self):
        if not self.temp_selection_rect or not self.selected_image_item: return
        item = self.selected_image_item
        rect = self.temp_selection_rect.rect()
        local_rect = item.mapFromScene(rect).boundingRect()
        
        scale = 1.0 / item.current_scale
        full_img = item.original_pixmap.toImage()
        cropped = full_img.copy(
            int(local_rect.x() * scale), int(local_rect.y() * scale),
            int(local_rect.width() * scale), int(local_rect.height() * scale)
        )
        
        if not cropped.isNull():
            item.original_pixmap = QPixmap.fromImage(cropped)
            item.set_scale(item.current_scale)
        self.view.scene().removeItem(self.temp_selection_rect)
        self.temp_selection_rect = None

    # --- IA FACE CROP ---
    def action_auto_face_crop(self):
        items = self.view.scene().selectedItems()
        if not items or not isinstance(items[0], SimplePixmapItem): return
        item = items[0]
        qimg = item.original_pixmap.toImage().convertToFormat(QImage.Format_RGB888)
        w, h = qimg.width(), qimg.height()
        ptr = qimg.constBits()
        arr = np.array(ptr).reshape(h, w, 3).copy()
        
        res = self.mp_face.process(arr)
        if res.detections:
            b = res.detections[0].location_data.relative_bounding_box
            margin = 0.3
            x1 = max(0, int((b.xmin - margin*b.width)*w))
            y1 = max(0, int((b.ymin - margin*b.height)*h))
            x2 = min(w, int((b.xmin + b.width + margin*b.width)*w))
            y2 = min(h, int((b.ymin + b.height + margin*b.height)*h))
            
            crop = arr[y1:y2, x1:x2]
            item.original_pixmap = cv2_to_qpixmap(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
            item.set_scale(item.current_scale)

    # --- UNDO / REDO (SIMPLIFIÉ) ---
    def action_undo(self): 
        # Logique d'annulation à implémenter selon votre structure de données
        pass

    def action_redo(self): 
        pass

    # --- EXPORT PDF ---
    def action_export_pdf(self):
        from PySide6.QtPrintSupport import QPrinter
        path, _ = QFileDialog.getSaveFileName(self, "Exporter PDF", "badge_final.pdf", "PDF Files (*.pdf)")
        if not path: return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        
        painter = QPainter(printer)
        # Page 1: Recto
        self.recto_scene.render(painter)
        # Page 2: Verso
        printer.newPage()
        self.verso_scene.render(painter)
        painter.end()
        QMessageBox.information(self, "Export", "Badge exporté avec succès.")

    def closeEvent(self, event):
        self.mp_face.close()
        event.accept()

 