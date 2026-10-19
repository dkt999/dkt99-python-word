#!/usr/bin/env python3
"""FenDoc 0.1.0 - khung app desktop thu nghiem: PyQt6 + QWebEngineView.

Chay thuong:  python main.py
Tu kiem tra:  python main.py --self-test   (headless, khong can man hinh)
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_INDEX = os.path.join(BASE_DIR, "ui", "index.html")

# Co GPU/sandbox day du thi van chay; thieu thi Chromium tu fallback.
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-dev-shm-usage",
)


def _qt_imports():
    from PyQt6.QtCore import QObject, pyqtSlot, QUrl, QTimer
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QFileDialog, QMessageBox,
    )
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebChannel import QWebChannel
    return QObject, pyqtSlot, QUrl, QTimer, QApplication, QMainWindow, \
        QFileDialog, QMessageBox, QWebEngineView, QWebChannel


class Backend:  # duoc tao that sau khi import (can QObject)
    pass


def build_classes():
    (QObject, pyqtSlot, QUrl, QTimer, QApplication, QMainWindow,
     QFileDialog, QMessageBox, QWebEngineView, QWebChannel) = _qt_imports()

    class Backend(QObject):
        """Cau noi Python <-> JS. Giai doan thu nghiem: API toi gian."""

        def __init__(self, window=None):
            super().__init__()
            self._window = window

        @pyqtSlot(result=str)
        def getAppInfo(self):
            return json.dumps(
                {"name": "FenDoc", "version": "0.1.0",
                 "engine": "QWebEngineView"},
                ensure_ascii=False)

        @pyqtSlot(str, result=str)
        def saveFile(self, html):
            dlg_parent = self._window
            path, _ = QFileDialog.getSaveFileName(
                dlg_parent, "Luu tai lieu", "",
                "FenDoc (*.fdoc.html);;HTML (*.html)")
            if not path:
                return json.dumps({"ok": False, "reason": "cancelled"})
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                return json.dumps({"ok": True, "path": path},
                                  ensure_ascii=False)
            except Exception as e:  # noqa: BLE001
                return json.dumps({"ok": False, "reason": str(e)})

        @pyqtSlot(result=str)
        def openFile(self):
            path, _ = QFileDialog.getOpenFileName(
                self._window, "Mo tai lieu", "", "HTML (*.html);;All (*)")
            if not path:
                return json.dumps({"ok": False, "reason": "cancelled"})
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                return json.dumps({"ok": True, "path": path, "html": content},
                                  ensure_ascii=False)
            except Exception as e:  # noqa: BLE001
                return json.dumps({"ok": False, "reason": str(e)})

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("FenDoc 0.1.0 - thu nghiem")
            self.resize(1280, 800)

            self.view = QWebEngineView(self)
            self.setCentralWidget(self.view)

            self.channel = QWebChannel(self.view.page())
            self.backend = Backend(self)
            self.channel.registerObject("backend", self.backend)
            self.view.page().setWebChannel(self.channel)

            self.view.load(QUrl.fromLocalFile(UI_INDEX))
            self._build_menu()

        def _build_menu(self):
            m = self.menuBar()
            f = m.addMenu("Tep")
            f.addAction("Mo...", lambda: self.view.page().runJavaScript(
                "window.__fendocOpen && window.__fendocOpen()"))
            f.addAction("Luu...", lambda: self.view.page().runJavaScript(
                "window.__fendocSave && window.__fendocSave()"))
            f.addSeparator()
            f.addAction("Thoat", self.close)
            h = m.addMenu("Tro giup")
            h.addAction("Gioi thieu", lambda: QMessageBox.information(
                self, "FenDoc",
                "FenDoc 0.1.0 - khung thu nghiem PyQt6 + QWebEngineView."))

    return (Backend, MainWindow, QUrl, QTimer, QApplication,
            QWebEngineView, QWebChannel)


def run_self_test():
    """Kiem tra headless: nap trang + goi bridge Python tu JS."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu --no-sandbox --disable-dev-shm-usage")
    (Backend, _Main, QUrl, QTimer, QApplication,
     QWebEngineView, QWebChannel) = build_classes()

    app = QApplication(sys.argv)
    view = QWebEngineView()
    channel = QWebChannel(view.page())
    backend = Backend(None)
    channel.registerObject("backend", backend)
    view.page().setWebChannel(channel)

    def poll(n=0):
        def cb(text):
            if text and text.startswith("BRIDGE-OK"):
                print("SELFTEST OK:", text, flush=True)
                app.quit()
            elif n < 40:
                QTimer.singleShot(250, lambda: poll(n + 1))
            else:
                print("SELFTEST FAIL: bridge not ready, last=",
                      repr(text), flush=True)
                app.quit()
        view.page().runJavaScript(
            "document.getElementById('bridge-status').textContent", cb)

    def on_load(ok):
        if not ok:
            print("SELFTEST FAIL: page did not load", flush=True)
            app.quit()
            return
        QTimer.singleShot(500, lambda: poll())

    view.loadFinished.connect(on_load)
    QTimer.singleShot(45000, app.quit)  # timeout cuoi
    view.load(QUrl.fromLocalFile(UI_INDEX))
    app.exec()


def main():
    (_Backend, MainWindow, _QUrl, _QTimer, QApplication,
     _View, _Channel) = build_classes()
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        main()
