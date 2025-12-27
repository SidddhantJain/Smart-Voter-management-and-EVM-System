"""
Vote Visualizer Dialog for VoteGuard Pro EVM
Language: Python (PyQt5)
Shows: Candidate card added to paper chain, animated into ballot box,
       and blockchain block appears to indicate storage.
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

        box_rect = QtCore.QRectF(380, 430, 120, 100)
        self.ballot_box = self.scene.addRect(
            box_rect,
            QtGui.QPen(QtGui.QColor("#333")),
            QtGui.QBrush(QtGui.QColor("#c8e6c9")),
        )
        box_text = self.scene.addText("Ballot Box")
        box_text.setDefaultTextColor(QtGui.QColor("#333"))
        box_text.setPos(box_rect.center().x() - 40, box_rect.top() - 22)

        chain_block_rect = QtCore.QRectF(720, 240, 130, 80)
        self.blockchain_block = self.scene.addRect(
            chain_block_rect,
            QtGui.QPen(QtGui.QColor("#333")),
            QtGui.QBrush(QtGui.QColor("#bbdefb")),
        )
        self.blockchain_label = self.scene.addText("Blockchain Block")
        self.blockchain_label.setDefaultTextColor(QtGui.QColor("#1a237e"))
        self.blockchain_label.setPos(chain_block_rect.left() + 6, chain_block_rect.top() + 6)
        self.blockchain_block.setOpacity(0.0)
        self.blockchain_label.setOpacity(0.0)

    def _make_candidate_card(self, name: str, image_path: Path | None) -> QtWidgets.QGraphicsItemGroup:
        group = QtWidgets.QGraphicsItemGroup()

        card_rect = QtCore.QRectF(0, 0, 200, 120)
        card = self.scene.addRect(
            card_rect,
            QtGui.QPen(QtGui.QColor("#444")),
            QtGui.QBrush(QtGui.QColor("#fffde7")),
        )
        group.addToGroup(card)

        if image_path and Path(image_path).exists():
            pix = QtGui.QPixmap(str(image_path))
            if not pix.isNull():
                pix = pix.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                img_item = self.scene.addPixmap(pix)
                img_item.setPos(10, 10)
                group.addToGroup(img_item)
        else:
            avatar = self.scene.addEllipse(
                QtCore.QRectF(10, 10, 80, 80),
                QtGui.QPen(QtGui.QColor("#666")),
                QtGui.QBrush(QtGui.QColor("#eeeeee")),
            )
            group.addToGroup(avatar)

        name_item = self.scene.addText(name or "Candidate")
        name_item.setDefaultTextColor(QtGui.QColor("#333"))
        name_item.setPos(100, 20)
        font = name_item.font()
        font.setPointSize(12)
        font.setBold(True)
        name_item.setFont(font)
        group.addToGroup(name_item)

        status_item = self.scene.addText("Vote Prepared")
        status_item.setDefaultTextColor(QtGui.QColor("#555"))
        status_item.setPos(100, 60)
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
        end = QtCore.QPointF(target_center.x() - 100, target_center.y() - 60)

        def after_box():
            self._animate_opacity(card, 1.0, 0.0, 600)
            self.blockchain_block.setOpacity(0.0)
            self.blockchain_label.setOpacity(0.0)
            self._animate_opacity(self.blockchain_block, 0.0, 1.0, 700)
            self._animate_opacity(self.blockchain_label, 0.0, 1.0, 700)
            QtCore.QTimer.singleShot(1800, self.accept)  # auto-close

        self._animate_move(card, start, end, 1200, on_done=after_box)


def visualize_vote(parent: QtWidgets.QWidget | None, candidate_name: str, image_path: str | Path | None = None) -> None:
    dlg = VoteVisualizerDialog(parent)
    dlg.show()
    QtCore.QTimer.singleShot(50, lambda: dlg.run_flow(candidate_name, image_path))
