from PySide6.QtCore import Slot
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from parallel_build.gui.build_thread import BuildThread
from parallel_build.gui.elided_label import QElidedLabel
from parallel_build.utils import OperatingSystem


class BuildDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Build in progress")
        self.resize(500, 200)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setTextVisible(False)

        self.build_step_label = QLabel("Warming up")
        self.build_step_label.setStyleSheet("font-weight: bold;")
        self.build_message_label = QElidedLabel()
        labels_layout = QHBoxLayout()
        labels_layout.addWidget(self.build_step_label, stretch=0)
        labels_layout.addWidget(self.build_message_label, stretch=1)

        self.output_text_area = QPlainTextEdit()
        self.output_text_area.setReadOnly(True)
        self.output_text_area.setFont(QFont(OperatingSystem.monospace_font))

        self.button_box = QDialogButtonBox()
        self.cancel_button = QPushButton("Cancel")
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )
        self.button_box.rejected.connect(self.cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addLayout(labels_layout)
        layout.addWidget(self.output_text_area)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.thread = BuildThread(self)
        self.thread.started.connect(self.on_build_start)
        self.thread.finished.connect(self.on_build_end)

    def start_build_process(self, continuous: bool, project_name: str):
        self.thread.configure(continuous, project_name)
        self.thread.start()

    def on_build_start(self):
        self.output_text_area.clear()

    def on_build_end(self):
        self.cancel_button.setText("Close")

    @Slot(str)
    def on_build_step(self, build_step_name: str):
        self.build_step_label.setText(build_step_name)
        self.output_text_area.appendPlainText(f"\n// {build_step_name}")

    @Slot(str)
    def on_build_progress(self, message: str):
        self.build_message_label.setText(message)
        self.output_text_area.appendPlainText(message)

    def cancel(self):
        self.close()

    def closeEvent(self, event: QCloseEvent):
        self.thread.stop()
