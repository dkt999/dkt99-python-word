# FenDoc — dkt99-python-word

Khung thử nghiệm app soạn thảo văn bản kiểu Word: **Python + PyQt6 + QWebEngineView**.

Ý tưởng dự án: tài liệu lưu dưới dạng HTML + JS (JS đóng vai trò script tự động
như VBA macro), đóng gói thành định dạng file binary riêng thay cho `.docx`.

## Chạy thử

```bash
pip install -r requirements.txt
python main.py
```

Tự kiểm tra headless (không cần màn hình):

```bash
python main.py --self-test
```

## Cấu trúc

- `main.py` — cửa sổ chính: QMainWindow + QWebEngineView, menu Tệp, cầu nối
  QWebChannel (`Backend`: `getAppInfo` / `saveFile` / `openFile`).
- `ui/index.html` — giao diện web nạp trong webview (placeholder; prototype
  ribbon 6 tab sẽ thay vào đây).

## Trạng thái

- [x] Khung app + bridge Python ↔ JS (self-test headless PASS)
- [ ] Giao diện ribbon: Định dạng / Insert / Latex / Mailing / Layout / Preview
- [ ] Định dạng file binary `.fdoc`
- [ ] Macro engine (JS sandbox)
