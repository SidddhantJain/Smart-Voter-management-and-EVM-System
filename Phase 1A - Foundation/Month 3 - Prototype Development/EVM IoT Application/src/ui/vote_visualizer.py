"""
Vote Visualizer Dialog for VoteGuard Pro EVM
Language: Python (PyQt5)
Shows: Candidate card added to paper chain, animated into ballot box,
    and optional blockchain indicator (removed per request).
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from pathlib import Path


class VoteVisualizerDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Vote Visualization")
        self.setModal(False)
        self.resize(900, 600)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

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
        box_text = self.scene.addText("Ballot Box")
        box_text.setDefaultTextColor(QtGui.QColor("#333"))
        box_text.setPos(box_rect.center().x() - 40, box_rect.top() - 22)
        # Blockchain block removed per request

    def _make_candidate_card(self, name: str, image_path: Path | None) -> QtWidgets.QGraphicsItemGroup:
        group = QtWidgets.QGraphicsItemGroup()

        # Ballot card sized smaller than ballot box
        card_rect = QtCore.QRectF(0, 0, 120, 80)
        card = self.scene.addRect(
            card_rect,
            QtGui.QPen(QtGui.QColor("#444")),
            QtGui.QBrush(QtGui.QColor("#fffde7")),
        )
        group.addToGroup(card)

        if image_path and Path(image_path).exists():
            pix = QtGui.QPixmap(str(image_path))
            if not pix.isNull():
                pix = pix.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                img_item = self.scene.addPixmap(pix)
                img_item.setPos(8, 8)
                group.addToGroup(img_item)
        else:
            avatar = self.scene.addEllipse(
                QtCore.QRectF(8, 8, 50, 50),
                QtGui.QPen(QtGui.QColor("#666")),
                QtGui.QBrush(QtGui.QColor("#eeeeee")),
            )
            group.addToGroup(avatar)

        name_item = self.scene.addText(name or "Candidate")
        name_item.setDefaultTextColor(QtGui.QColor("#333"))
        name_item.setPos(65, 12)
        font = name_item.font()
        font.setPointSize(10)
        font.setBold(True)
        name_item.setFont(font)
        group.addToGroup(name_item)

        status_item = self.scene.addText("Vote Prepared")
        status_item.setDefaultTextColor(QtGui.QColor("#555"))
        status_item.setPos(65, 40)
        group.addToGroup(status_item)

        group.setPos(340, 60)
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

    def _animate_move(self, item: QtWidgets.QGraphicsItem, start: QtCore.QPointF, end: QtCore.QPointF, duration_ms: int = 1200, on_done=None) -> None:
        item.setPos(start)
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration_ms)

        def _update(value: float):
            x = start.x() + (end.x() - start.x()) * value
            y = start.y() + (end.y() - start.y()) * value
            item.setPos(x, y)

        def _finish():
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def _animate_opacity(self, item: QtWidgets.QGraphicsItem, start: float, end: float, duration_ms: int = 800, on_done=None) -> None:
        anim = QtCore.QVariantAnimation(self)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(duration_ms)

        def _update(value: float):
            item.setOpacity(value)

        def _finish():
            if callable(on_done):
                on_done()

        anim.valueChanged.connect(_update)
        anim.finished.connect(_finish)
        anim.start()

    def run_flow(self, candidate_name: str, image_path: str | Path | None = None) -> None:
        self._add_to_paper_chain(candidate_name)
        card = self._make_candidate_card(candidate_name, Path(image_path) if image_path else None)
        start = card.pos()
        target_center = self.ballot_box.rect().center()
        # Center the smaller ballot card within the ballot box
        end = QtCore.QPointF(target_center.x() - 60, target_center.y() - 40)

        def after_box():
            # Fade out the ballot card and close
            self._animate_opacity(card, 1.0, 0.0, 1200)
            QtCore.QTimer.singleShot(1500, self.accept)

        # Slow down the move animation for emphasis
        self._animate_move(card, start, end, 2500, on_done=after_box)


def visualize_vote(parent: QtWidgets.QWidget | None, candidate_name: str, image_path: str | Path | None = None, on_done=None) -> None:
    dlg = VoteVisualizerDialog(parent)
    if callable(on_done):
        dlg.accepted.connect(on_done)
    dlg.show()
    QtCore.QTimer.singleShot(50, lambda: dlg.run_flow(candidate_name, image_path))
