"""
Vote Visualizer Dialog for VoteGuard Pro EVM
Language: Python (PyQt5)
Shows: Candidate card added to paper chain, animated into ballot box,
    and optional blockchain indicator (removed per request).
"""

from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets


class VoteVisualizerDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Vote Visualization")
        self.setModal(False)
        self.resize(900, 600)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        # Present as a clean tool window without close/min/max buttons
        flags = self.windowFlags() | QtCore.Qt.Tool | QtCore.Qt.CustomizeWindowHint
        flags &= ~QtCore.Qt.WindowCloseButtonHint
        flags &= ~QtCore.Qt.WindowMinMaxButtonsHint
        self.setWindowFlags(flags)

        self.view = QtWidgets.QGraphicsView(self)
        self.view.setRenderHints(
            QtGui.QPainter.Antialiasing
            | QtGui.QPainter.TextAntialiasing
            | QtGui.QPainter.SmoothPixmapTransform
        )
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        self.scene = QtWidgets.QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setSceneRect(0, 0, 880, 560)

        self.chain_count = 0
        self.status_overlay = None
        self.checkmark_item = None
        self._draw_static_elements()

    def _draw_static_elements(self) -> None:
        chain_label = self.scene.addText("Paper Chain")
        chain_label.setDefaultTextColor(QtGui.QColor("#333"))
        chain_label.setPos(20, 20)

        # Ballot box sized to fit the ballot card comfortably
        box_rect = QtCore.QRectF(380, 430, 160, 120)
        self.ballot_box = self.scene.addRect(
            box_rect,
            QtGui.QPen(QtGui.QColor("#333")),
            QtGui.QBrush(QtGui.QColor("#c8e6c9")),
        )
        # Subtle drop shadow for visual depth
        try:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setOffset(2, 2)
            shadow.setColor(QtGui.QColor(0, 0, 0, 80))
            self.ballot_box.setGraphicsEffect(shadow)
        except Exception:
            pass
        box_text = self.scene.addText("Ballot Box")
        box_text.setDefaultTextColor(QtGui.QColor("#333"))
        box_text.setPos(box_rect.center().x() - 40, box_rect.top() - 22)
        # Blockchain block removed per request

        # Status overlay near the ballot box
        self.status_overlay = self.scene.addText("")
        self.status_overlay.setDefaultTextColor(QtGui.QColor("#2e7d32"))
        font = self.status_overlay.font()
        font.setPointSize(11)
        font.setBold(True)
        self.status_overlay.setFont(font)
        self.status_overlay.setPos(box_rect.left() - 10, box_rect.top() - 60)

        # Checkmark appears upon successful cast
        self.checkmark_item = self.scene.addText("✓")
        self.checkmark_item.setDefaultTextColor(QtGui.QColor("#2e7d32"))
        chk_font = self.checkmark_item.font()
        chk_font.setPointSize(28)
        chk_font.setBold(True)
        self.checkmark_item.setFont(chk_font)
        self.checkmark_item.setOpacity(0.0)
        self.checkmark_item.setPos(box_rect.center().x() - 10, box_rect.top() - 40)

    def _make_candidate_card(
        self, name: str, image_path: Path | None
    ) -> QtWidgets.QGraphicsItemGroup:
        group = QtWidgets.QGraphicsItemGroup()
        # Envelope-style ballot: base rectangle with a flap triangle
        base_rect = QtCore.QRectF(0, 0, 140, 90)
        base_grad = QtGui.QLinearGradient(base_rect.topLeft(), base_rect.bottomLeft())
        base_grad.setColorAt(0.0, QtGui.QColor("#fffde7"))
        base_grad.setColorAt(1.0, QtGui.QColor("#f8f1d2"))
        base = self.scene.addRect(
            base_rect,
            QtGui.QPen(QtGui.QColor("#6d4c41")),
            QtGui.QBrush(base_grad),
        )
        group.addToGroup(base)

        flap_poly = QtGui.QPolygonF(
            [
                QtCore.QPointF(0, 0),
                QtCore.QPointF(base_rect.width(), 0),
                QtCore.QPointF(base_rect.width() / 2.0, 22),
            ]
        )
        flap = self.scene.addPolygon(
            flap_poly,
            QtGui.QPen(QtGui.QColor("#6d4c41")),
            QtGui.QBrush(QtGui.QColor("#f3e7b8")),
        )
        flap.setTransformOriginPoint(base_rect.width() / 2.0, 0)
        flap.setRotation(-18.0)
        group.addToGroup(flap)

        # Decorative address lines
        line_pen = QtGui.QPen(QtGui.QColor("#9e9e9e"))
        line_pen.setWidth(1)
        for i in range(3):
            y = 36 + i * 14
            self.scene.addLine(60, y, base_rect.width() - 10, y, line_pen)

        if image_path and Path(image_path).exists():
            pix = QtGui.QPixmap(str(image_path))
            if not pix.isNull():
                pix = pix.scaled(
                    42, 42, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
                img_item = self.scene.addPixmap(pix)
                img_item.setPos(10, 10)
                group.addToGroup(img_item)
        else:
            avatar = self.scene.addEllipse(
                QtCore.QRectF(10, 10, 42, 42),
                QtGui.QPen(QtGui.QColor("#666")),
                QtGui.QBrush(QtGui.QColor("#eeeeee")),
            )
            group.addToGroup(avatar)

        name_item = self.scene.addText(name or "Candidate")
        name_item.setDefaultTextColor(QtGui.QColor("#4e342e"))
        name_item.setPos(60, 14)
        font = name_item.font()
        font.setPointSize(10)
        font.setBold(True)
        name_item.setFont(font)
        group.addToGroup(name_item)

        status_item = self.scene.addText("Vote Prepared")
        status_item.setDefaultTextColor(QtGui.QColor("#6d4c41"))
        status_item.setPos(60, 50)
        group.addToGroup(status_item)
        # Subtle shadow on the whole envelope
        try:
            env_shadow = QtWidgets.QGraphicsDropShadowEffect()
            env_shadow.setBlurRadius(12)
            env_shadow.setOffset(1, 2)
            env_shadow.setColor(QtGui.QColor(0, 0, 0, 60))
            group.setGraphicsEffect(env_shadow)
        except Exception:
            pass

        group.setPos(320, 60)
        group.setData(0, flap)
        self.scene.addItem(group)
        return group

    def _add_to_paper_chain(self, name: str) -> None:
        x = 20 + (self.chain_count % 5) * 110
        y = 60 + (self.chain_count // 5) * 70
        rect = self.scene.addRect(
            QtCore.QRectF(x, y, 100, 50),
            QtGui.QPen(QtGui.QColor("#888")),
            QtGui.QBrush(QtGui.QColor("#f1f8e9")),
        )
        label = self.scene.addText(name or "Candidate")
        label.setDefaultTextColor(QtGui.QColor("#2e7d32"))
        label.setPos(x + 6, y + 6)
        self.chain_count += 1

    def _animate_move(
        self,
        item: QtWidgets.QGraphicsItem,
        start: QtCore.QPointF,
        end: QtCore.QPointF,
        duration_ms: int = 1200,
        on_done=None,
    ) -> None:
        item.setPos(start)
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration_ms)
        easing = QtCore.QEasingCurve(QtCore.QEasingCurve.InOutCubic)

        def _update(value: float):
            v = easing.valueForProgress(value)
            x = start.x() + (end.x() - start.x()) * v
            y = start.y() + (end.y() - start.y()) * v
            item.setPos(x, y)

        def _finish():
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def _animate_opacity(
        self,
        item: QtWidgets.QGraphicsItem,
        start: float,
        end: float,
        duration_ms: int = 800,
        on_done=None,
    ) -> None:
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(duration_ms)
        easing = QtCore.QEasingCurve(QtCore.QEasingCurve.InOutQuad)

        def _update(value: float):
            item.setOpacity(easing.valueForProgress(value))

        def _finish():
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def _animate_scale(
        self,
        item: QtWidgets.QGraphicsItem,
        start: float,
        end: float,
        duration_ms: int = 600,
        on_done=None,
    ) -> None:
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(duration_ms)
        easing = QtCore.QEasingCurve(QtCore.QEasingCurve.OutBack)

        def _update(value: float):
            item.setScale(easing.valueForProgress(value))

        def _finish():
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def _animate_rotation(
        self,
        item: QtWidgets.QGraphicsItem,
        start_deg: float,
        end_deg: float,
        duration_ms: int = 600,
        on_done=None,
    ) -> None:
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(start_deg)
        anim.setEndValue(end_deg)
        anim.setDuration(duration_ms)
        easing = QtCore.QEasingCurve(QtCore.QEasingCurve.OutBack)

        def _update(value: float):
            item.setRotation(easing.valueForProgress(value))

        def _finish():
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def run_flow(
        self, candidate_name: str, image_path: str | Path | None = None
    ) -> None:
        self._add_to_paper_chain(candidate_name)
        # Update status
        if self.status_overlay:
            self.status_overlay.setPlainText("Casting vote…")
        card = self._make_candidate_card(
            candidate_name, Path(image_path) if image_path else None
        )
        start = card.pos()
        target_center = self.ballot_box.rect().center()
        # Center the envelope within the ballot box
        end = QtCore.QPointF(target_center.x() - 70, target_center.y() - 45)

        def after_box():
            # Gentle pulse on arrival
            self._animate_scale(
                card,
                1.0,
                1.08,
                250,
                on_done=lambda: self._animate_scale(card, 1.08, 1.0, 250),
            )
            # Close the flap, then show checkmark and update status
            flap = card.data(0)
            if flap:
                self._animate_rotation(flap, -18.0, 0.0, 500)
            # Show checkmark and update status
            if self.checkmark_item:
                self._animate_opacity(self.checkmark_item, 0.0, 1.0, 700)
            if self.status_overlay:
                self.status_overlay.setPlainText("Vote recorded")
            # Subtle glow using colorize effect
            try:
                glow = QtWidgets.QGraphicsColorizeEffect()
                glow.setColor(QtGui.QColor("#66bb6a"))
                glow.setStrength(0.3)
                self.ballot_box.setGraphicsEffect(glow)
                QtCore.QTimer.singleShot(
                    900, lambda: self.ballot_box.setGraphicsEffect(None)
                )
            except Exception:
                pass
            # Fade out the ballot card and close
            self._animate_opacity(card, 1.0, 0.0, 1200)
            QtCore.QTimer.singleShot(1500, self.accept)

        # Slow down the move animation for emphasis
        self._animate_move(card, start, end, 2500, on_done=after_box)


def visualize_vote(
    parent: QtWidgets.QWidget | None,
    candidate_name: str,
    image_path: str | Path | None = None,
    on_done=None,
) -> None:
    dlg = VoteVisualizerDialog(parent)
    if callable(on_done):
        dlg.accepted.connect(on_done)
    dlg.show()
    QtCore.QTimer.singleShot(50, lambda: dlg.run_flow(candidate_name, image_path))
