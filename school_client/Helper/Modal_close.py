from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsOpacityEffect 
 

def fade_out_and_close(widget, duration=400):
    # 1. On crée l'effet sur le widget passé en paramètre
    # On l'attache au widget pour éviter qu'il soit supprimé par le Garbage Collector
    widget.fade_effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(widget.fade_effect)
    
    # 2. Animation
    widget.fade_anim = QPropertyAnimation(widget.fade_effect, b"opacity")
    widget.fade_anim.setDuration(duration)
    widget.fade_anim.setStartValue(1.0)
    widget.fade_anim.setEndValue(0.0)
    widget.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
     
    widget.fade_anim.finished.connect(widget.close) 
    
    # 4. Lancement
    widget.fade_anim.start()


 