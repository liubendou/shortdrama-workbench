"""以网页方式启动 JJYB（不打开 PyWebView 窗口）。在 apps/jjyb 目录下运行。"""
import os
import sys

root = r"C:\Users\Administrator\shortdrama-studio\apps\jjyb"
os.chdir(root)
sys.path.insert(0, root)
from frontend.app import app, socketio  # noqa: E402

socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
