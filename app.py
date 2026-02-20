import sys
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, COMM, ID3, ID3NoHeaderError, WOAS
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


EDITABLE_FIELDS = [
    ("title", "Title"),
    ("artist", "Artist"),
    ("album", "Album"),
    ("albumartist", "Album Artist"),
    ("genre", "Genre"),
    ("date", "Year/Date"),
    ("tracknumber", "Track #"),
    ("discnumber", "Disc #"),
    ("composer", "Composer"),
]


class Mp3MetaEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Meta Editor")
        self.resize(1024, 680)

        self.current_file: Path | None = None
        self.field_inputs: dict[str, QLineEdit] = {}
        self.comment_input = QLineEdit()
        self.woas_input = QLineEdit()
        self.file_label = QLabel("No file selected")
        self.raw_text = QPlainTextEdit()
        self.cover_data: bytes | None = None
        self.cover_mime = "image/jpeg"
        self.cover_label = QLabel("No cover")
        self.cover_info_label = QLabel("")
        self.logo_label = QLabel()

        self._build_ui()
        self._apply_styles()
        self._load_logo()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        toolbar_card = QWidget()
        toolbar_card.setObjectName("glassCard")
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(10)

        open_btn = QPushButton("Open MP3")
        save_btn = QPushButton("Save Tags")
        open_btn.setProperty("variant", "primary")
        save_btn.setProperty("variant", "primary")

        open_btn.clicked.connect(self.open_file)
        save_btn.clicked.connect(self.save_tags)

        self.file_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.file_label.setObjectName("fileLabel")

        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedHeight(72)
        main_layout.addWidget(self.logo_label)

        toolbar_layout.addWidget(open_btn)
        toolbar_layout.addWidget(save_btn)
        toolbar_layout.addWidget(self.file_label, 1)

        main_layout.addWidget(toolbar_card)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(12)
        main_layout.addWidget(splitter, 1)

        left_widget = QWidget()
        left_widget.setObjectName("glassCard")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)
        form_title = QLabel("Editable tags")
        form_title.setObjectName("sectionTitle")
        left_layout.addWidget(form_title)

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignLeft)

        for key, label in EDITABLE_FIELDS:
            input_field = QLineEdit()
            self.field_inputs[key] = input_field
            form.addRow(label, input_field)

        form.addRow("Comment", self.comment_input)
        form.addRow("WOAS (Source URL)", self.woas_input)

        left_layout.addLayout(form)
        self.cover_label.setFixedSize(220, 220)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setObjectName("coverPreview")
        cover_title = QLabel("Cover")
        cover_title.setObjectName("sectionTitle")
        left_layout.addWidget(cover_title)
        left_layout.addWidget(self.cover_label, alignment=Qt.AlignLeft)

        cover_actions = QHBoxLayout()
        cover_actions.setSpacing(8)
        replace_cover_btn = QPushButton("Replace Cover")
        remove_cover_btn = QPushButton("Remove Cover")
        replace_cover_btn.setProperty("variant", "ghost")
        remove_cover_btn.setProperty("variant", "ghost")
        replace_cover_btn.clicked.connect(self.replace_cover)
        remove_cover_btn.clicked.connect(self.remove_cover)
        cover_actions.addWidget(replace_cover_btn)
        cover_actions.addWidget(remove_cover_btn)
        left_layout.addLayout(cover_actions)
        self.cover_info_label.setObjectName("hintLabel")
        left_layout.addWidget(self.cover_info_label)
        left_layout.addStretch(1)

        # Keep form usable in small window sizes: scroll instead of squeezing controls.
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.NoFrame)
        left_scroll.setWidget(left_widget)
        left_scroll.setMinimumWidth(360)

        right_widget = QWidget()
        right_widget.setObjectName("glassCard")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)
        raw_title = QLabel("All metadata (raw)")
        raw_title.setObjectName("sectionTitle")
        right_layout.addWidget(raw_title)

        self.raw_text.setReadOnly(True)
        self.raw_text.setObjectName("rawText")
        right_layout.addWidget(self.raw_text, 1)

        splitter.addWidget(left_scroll)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 640])
        self._add_blur_effect(toolbar_card)
        self._add_blur_effect(left_widget)
        self._add_blur_effect(right_widget)

    def _add_blur_effect(self, widget: QWidget):
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(48)
        effect.setOffset(0, 0)
        effect.setColor(QColor(28, 42, 66, 210))
        widget.setGraphicsEffect(effect)

    def _apply_styles(self):
        self.setStyleSheet(
            """
            #logoLabel {
                background: transparent;
            }
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(8, 11, 18, 255),
                    stop:0.45 rgba(11, 15, 23, 255),
                    stop:1 rgba(6, 8, 14, 255)
                );
            }
            #root {
                background: rgba(8, 11, 18, 255);
            }
            #glassCard {
                background: rgba(255, 255, 255, 20);
                border-radius: 18px;
            }
            QLabel {
                color: rgba(241, 247, 255, 230);
                font-size: 13px;
            }
            #sectionTitle {
                color: rgba(255, 255, 255, 245);
                font-size: 18px;
                font-weight: 700;
            }
            #fileLabel {
                color: rgba(229, 239, 255, 240);
                font-size: 12px;
                background: rgba(255, 255, 255, 24);
                border-radius: 12px;
                padding: 7px 10px;
            }
            QLineEdit, QPlainTextEdit {
                background: rgba(255, 255, 255, 20);
                border: none;
                border-radius: 11px;
                padding: 7px 10px;
                color: rgba(255, 255, 255, 245);
                selection-background-color: rgba(112, 174, 255, 180);
            }
            QLineEdit:focus, QPlainTextEdit:focus {
                background: rgba(255, 255, 255, 28);
            }
            QLineEdit::placeholder, QPlainTextEdit::placeholder {
                color: rgba(224, 235, 255, 150);
            }
            QPushButton {
                border-radius: 11px;
                border: none;
                color: rgba(248, 252, 255, 250);
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton[variant="primary"] {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(81, 182, 255, 220),
                    stop:1 rgba(37, 128, 224, 230)
                );
            }
            QPushButton[variant="primary"]:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(101, 196, 255, 235),
                    stop:1 rgba(55, 143, 235, 235)
                );
            }
            QPushButton[variant="ghost"] {
                background: rgba(255, 255, 255, 20);
            }
            QPushButton[variant="ghost"]:hover {
                background: rgba(255, 255, 255, 28);
            }
            #coverPreview {
                border-radius: 16px;
                background: rgba(255, 255, 255, 24);
                color: rgba(234, 244, 255, 220);
                font-size: 14px;
            }
            #hintLabel {
                color: rgba(222, 234, 252, 185);
                font-size: 12px;
            }
            QSplitter::handle {
                background: rgba(255, 255, 255, 20);
                border-radius: 5px;
                margin: 6px 0;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 90);
                min-height: 22px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
        )

    def _resource_path(self, name: str) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(getattr(sys, "_MEIPASS"))
            candidates = [
                base / name,
                base / "Resources" / name,
                base / "Frameworks" / name,
                base.parent / "Resources" / name,
                base.parent / "Frameworks" / name,
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate
            return candidates[0]
        return Path(__file__).resolve().parent / name

    def _load_logo(self):
        logo_path = self._resource_path("logo.png")
        if not logo_path.exists():
            self.logo_label.clear()
            return
        pixmap = QPixmap(str(logo_path))
        if pixmap.isNull():
            self.logo_label.clear()
            return
        self.logo_label.setPixmap(
            pixmap.scaledToHeight(
                58,
                Qt.SmoothTransformation,
            )
        )

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select MP3 file", "", "MP3 files (*.mp3)")
        if not path:
            return

        self.current_file = Path(path)
        self.file_label.setText(str(self.current_file))
        self._load_metadata()

    def _load_metadata(self):
        if not self.current_file:
            return

        try:
            try:
                easy_tags = EasyID3(str(self.current_file))
            except ID3NoHeaderError:
                ID3(str(self.current_file)).save(v2_version=3)
                easy_tags = EasyID3(str(self.current_file))

            for key, _ in EDITABLE_FIELDS:
                value = easy_tags.get(key, [""])
                self.field_inputs[key].setText(value[0] if value else "")

            self.comment_input.setText("")
            self.woas_input.setText("")
            id3 = ID3(str(self.current_file))
            comments = id3.getall("COMM")
            if comments and comments[0].text:
                self.comment_input.setText(str(comments[0].text[0]))
            woas_frames = id3.getall("WOAS")
            if woas_frames:
                self.woas_input.setText(getattr(woas_frames[0], "url", ""))
            self._load_cover(id3)

            self._refresh_raw_view()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Cannot read tags:\n{exc}")

    def _load_cover(self, id3: ID3):
        self.cover_data = None
        self.cover_mime = "image/jpeg"
        apics = id3.getall("APIC")
        if apics:
            frame = apics[0]
            self.cover_data = frame.data
            self.cover_mime = frame.mime or "image/jpeg"
        self._update_cover_preview()

    def _update_cover_preview(self):
        if not self.cover_data:
            self.cover_label.setText("No cover")
            self.cover_label.setPixmap(QPixmap())
            self.cover_info_label.setText("Cover is not set")
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(self.cover_data):
            self.cover_label.setText("Preview not available")
            self.cover_label.setPixmap(QPixmap())
            self.cover_info_label.setText(f"Loaded cover ({self.cover_mime})")
            return

        preview = pixmap.scaled(
            self.cover_label.width(),
            self.cover_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.cover_label.setText("")
        self.cover_label.setPixmap(preview)
        self.cover_info_label.setText(
            f"Loaded cover ({self.cover_mime}, {pixmap.width()}x{pixmap.height()})"
        )

    def replace_cover(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Open an MP3 file first.")
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select cover image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)",
        )
        if not path:
            return

        try:
            image_path = Path(path)
            data = image_path.read_bytes()
            suffix = image_path.suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
            }
            self.cover_data = data
            self.cover_mime = mime_map.get(suffix, "image/jpeg")
            self._update_cover_preview()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Cannot load image:\n{exc}")

    def remove_cover(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Open an MP3 file first.")
            return
        self.cover_data = None
        self._update_cover_preview()

    def _refresh_raw_view(self):
        if not self.current_file:
            return

        lines: list[str] = []
        try:
            id3 = ID3(str(self.current_file))
            if not id3:
                lines.append("No ID3 metadata found.")
            else:
                for key in sorted(id3.keys()):
                    frame = id3[key]
                    if hasattr(frame, "text"):
                        value = " | ".join(str(part) for part in frame.text)
                    else:
                        value = str(frame)
                    lines.append(f"{key}: {value}")
        except Exception as exc:
            lines = [f"Cannot read raw metadata: {exc}"]

        self.raw_text.setPlainText("\n".join(lines))

    def save_tags(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Open an MP3 file first.")
            return

        try:
            try:
                tags = EasyID3(str(self.current_file))
            except ID3NoHeaderError:
                ID3(str(self.current_file)).save(v2_version=3)
                tags = EasyID3(str(self.current_file))

            for key, _ in EDITABLE_FIELDS:
                value = self.field_inputs[key].text().strip()
                if value:
                    tags[key] = [value]
                elif key in tags:
                    del tags[key]
            tags.save(v2_version=3)

            id3 = ID3(str(self.current_file))
            id3.delall("COMM")
            comment = self.comment_input.text().strip()
            if comment:
                id3.add(COMM(encoding=3, lang="eng", desc="", text=[comment]))
            id3.delall("WOAS")
            woas_url = self.woas_input.text().strip()
            if woas_url:
                id3.add(WOAS(url=woas_url))
            id3.delall("APIC")
            if self.cover_data:
                id3.add(
                    APIC(
                        encoding=3,
                        mime=self.cover_mime,
                        type=3,
                        desc="Cover",
                        data=self.cover_data,
                    )
                )
            id3.save(v2_version=3)

            self._refresh_raw_view()
            QMessageBox.information(self, "Success", "Metadata saved.")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Cannot save tags:\n{exc}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Mp3MetaEditor()
    window.show()
    sys.exit(app.exec())
