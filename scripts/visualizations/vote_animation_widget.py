from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
try:
    from PyQt5.QtWidgets import QOpenGLWidget  # type: ignore
except Exception:
    QOpenGLWidget = None


class VoteAnimationWidget(QtWidgets.QWidget):
    """
    A lightweight PyQt5 widget that visualizes the vote-casting flow:
    1) Candidate card (image + name) is added to a paper chain (top-left).
    2) The same card animates into a ballot box (bottom-center).
    3) A blockchain block indicator appears to show storage.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vote Casting Visualization")
        self.resize(900, 600)

        self.view = QtWidgets.QGraphicsView(self)
        self.view.setRenderHints(
            QtGui.QPainter.Antialiasing
            | QtGui.QPainter.TextAntialiasing
            | QtGui.QPainter.SmoothPixmapTransform
        )
        self.view.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.view.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        try:
            if QOpenGLWidget is not None:
                self.view.setViewport(QOpenGLWidget())
        except Exception:
            pass
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        self.scene = QtWidgets.QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setSceneRect(0, 0, 880, 560)

        self.chain_count = 0
        self._animations: set[QtCore.QVariantAnimation] = set()

        # Draw areas: paper chain (top-left), ballot box (bottom-center)
        self._draw_static_elements()

    def _draw_static_elements(self) -> None:
        # Paper chain label
        chain_label = self.scene.addText("Paper Chain")
        chain_label.setDefaultTextColor(QtGui.QColor("#333"))
        chain_label.setPos(20, 20)

        # Ballot box (intentionally smaller than the ballot envelope)
        box_rect = QtCore.QRectF(380, 440, 140, 110)
        self.ballot_box = self.scene.addRect(
            box_rect,
            QtGui.QPen(QtGui.QColor("#333")),
            QtGui.QBrush(QtGui.QColor("#c8e6c9")),
        )
        box_text = self.scene.addText("Ballot Box")
        box_text.setDefaultTextColor(QtGui.QColor("#333"))
        box_text.setPos(box_rect.center().x() - 40, box_rect.top() - 28)

        # Slot at the top of the box
        slot_width = box_rect.width() * 0.7
        slot_height = 6
        slot_left = box_rect.center().x() - slot_width / 2
        slot_top = box_rect.top() + 10
        self.box_slot = self.scene.addRect(
            QtCore.QRectF(slot_left, slot_top, slot_width, slot_height),
            QtGui.QPen(QtGui.QColor("#263238")),
            QtGui.QBrush(QtGui.QColor("#37474f")),
        )

        # No blockchain visuals (removed per request)

    def _make_candidate_card(
        self, name: str, image_path: Path | None
    ) -> QtWidgets.QGraphicsItemGroup:
        group = QtWidgets.QGraphicsItemGroup()

        # Envelope-style ballot (larger than box)
        card_rect = QtCore.QRectF(0, 0, 220, 140)
        base_grad = QtGui.QLinearGradient(card_rect.topLeft(), card_rect.bottomLeft())
        base_grad.setColorAt(0.0, QtGui.QColor("#fffde7"))
        base_grad.setColorAt(1.0, QtGui.QColor("#f8f1d2"))
        card = self.scene.addRect(
            card_rect,
            QtGui.QPen(QtGui.QColor("#444")),
            QtGui.QBrush(base_grad),
        )
        group.addToGroup(card)

        # Flap triangle at the top (like a letter)
        flap_poly = QtGui.QPolygonF(
            [
                QtCore.QPointF(0, 0),
                QtCore.QPointF(card_rect.width(), 0),
                QtCore.QPointF(card_rect.width() / 2.0, 24),
            ]
        )
        flap = self.scene.addPolygon(
            flap_poly,
            QtGui.QPen(QtGui.QColor("#6d4c41")),
            QtGui.QBrush(QtGui.QColor("#f3e7b8")),
        )
        flap.setTransformOriginPoint(card_rect.width() / 2.0, 0)
        flap.setRotation(-18.0)
        flap.setZValue(1)
        group.addToGroup(flap)

        # Candidate image (optional)
        if image_path and Path(image_path).exists():
            pix = QtGui.QPixmap(str(image_path))
            if not pix.isNull():
                pix = pix.scaled(
                    64, 64, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
                img_item = self.scene.addPixmap(pix)
                img_item.setPos(14, 18)
                group.addToGroup(img_item)
        else:
            # Placeholder avatar
            avatar = self.scene.addEllipse(
                QtCore.QRectF(14, 18, 64, 64),
                QtGui.QPen(QtGui.QColor("#666")),
                QtGui.QBrush(QtGui.QColor("#eeeeee")),
            )
            group.addToGroup(avatar)

        # Candidate name
        name_item = self.scene.addText(name or "Candidate")
        name_item.setDefaultTextColor(QtGui.QColor("#333"))
        name_item.setPos(90, 24)
        font = name_item.font()
        font.setPointSize(12)
        font.setBold(True)
        name_item.setFont(font)
        group.addToGroup(name_item)

        # Status text
        status_item = self.scene.addText("Vote Prepared")
        status_item.setDefaultTextColor(QtGui.QColor("#555"))
        status_item.setPos(90, 64)
        group.addToGroup(status_item)

        # Decorative address lines
        line_pen = QtGui.QPen(QtGui.QColor("#9e9e9e"))
        line_pen.setWidth(1)
        for i in range(3):
            y = 88 + i * 18
            line_item = self.scene.addLine(90, y, card_rect.width() - 14, y, line_pen)
            group.addToGroup(line_item)

        # Start position (top-center)
        group.setPos(340, 60)
        # Rotate the envelope around its top center for letter-like insertion
        group.setTransformOriginPoint(card_rect.width() / 2.0, 0)
        # Store flap reference for smooth closing during insertion
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
        # Basic linear animation using QVariantAnimation to drive position updates
        item.setPos(start)
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration_ms)
        easing = QtCore.QEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self._animations.add(anim)

        def _update(value: float):
            v = easing.valueForProgress(value)
            x = start.x() + (end.x() - start.x()) * v
            y = start.y() + (end.y() - start.y()) * v
            item.setPos(x, y)

        def _finish():
            try:
                self._animations.discard(anim)
            except Exception:
                pass
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
        self._animations.add(anim)

        def _update(value: float):
            p = easing.valueForProgress(value)
            item.setOpacity(start + (end - start) * p)

        def _finish():
            try:
                self._animations.discard(anim)
            except Exception:
                pass
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
        self._animations.add(anim)

        def _update(value: float):
            p = easing.valueForProgress(value)
            item.setRotation(start_deg + (end_deg - start_deg) * p)

        def _finish():
            try:
                self._animations.discard(anim)
            except Exception:
                pass
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def animate_vote(
        self, candidate_name: str, image_path: str | Path | None = None
    ) -> None:
        """
        Public API to run the full sequence for a single vote.
        """
        # 1) Add to paper chain
        self._add_to_paper_chain(candidate_name)

        # 2) Build candidate card at top-center
        card = self._make_candidate_card(
            candidate_name, Path(image_path) if image_path else None
        )

        # 3) Animate to slot: rotate like a letter and insert
        start = card.pos()
        slot_center = self.box_slot.rect().center()
        approach = QtCore.QPointF(slot_center.x() - 110, self.box_slot.rect().top() - 40)

        def after_box():
            # Rotate and insert downwards through the slot while fading out
            self._animate_rotation(card, 0.0, -18.0, 400)
            # Close the flap
            flap_item = card.data(0)
            if flap_item is not None:
                self._animate_rotation(flap_item, -18.0, 0.0, 400)
            insert_target = QtCore.QPointF(card.pos().x(), card.pos().y() + 70)
            self._animate_move(
                card,
                card.pos(),
                insert_target,
                700,
                on_done=lambda: self._animate_opacity(card, 1.0, 0.0, 900),
            )

        self._animate_move(card, start, approach, 1400, on_done=after_box)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = VoteAnimationWidget()
    w.show()
    # Demo run
    QtCore.QTimer.singleShot(600, lambda: w.animate_vote("Alice", None))
    QtCore.QTimer.singleShot(3000, lambda: w.animate_vote("Bob", None))
    sys.exit(app.exec_())
