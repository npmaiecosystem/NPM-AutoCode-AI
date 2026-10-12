"""
Deployed version v4
"""
import sys, os, runpy, socket, subprocess, traceback
from pathlib import Path

_APP_DIR = os.path.dirname(os.path.abspath(__file__))     
_LOG_DIR = Path(_APP_DIR) / "logs"
try:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    _LOG_DIR = Path.home() / ".npmai_agent"
    try:
        _LOG_DIR.mkdir(exist_ok=True)
    except Exception:
        pass


def _log_crash(title):
    try:
        with open(_LOG_DIR / "crash.log", "a", encoding="utf-8") as f:
            f.write(f"\n=== {title} ===\n{traceback.format_exc()}\n")
    except Exception:
        pass


def _excepthook(exc_type, exc, tb):
    try:
        with open(_LOG_DIR / "crash.log", "a", encoding="utf-8") as f:
            f.write("\n=== Unhandled exception ===\n" + "".join(traceback.format_exception(exc_type, exc, tb)) + "\n")
    except Exception:
        pass


def _fatal(msg):
    """Cross-platform error popup (Qt), falling back to stderr."""
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        _qa = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "NPM-AutoCode-AI", msg)
    except Exception:
        try:
            sys.stderr.write(msg + "\n")
        except Exception:
            pass


def _attach_std():
    for name, fd in (("stdout", 1), ("stderr", 2)):
        if getattr(sys, name) is None:
            try:
                setattr(sys, name, open(fd, "w", encoding="utf-8", errors="replace", closefd=False))
            except Exception:
                setattr(sys, name, open(os.devnull, "w"))



_SYS_PKG_MGRS = {"sudo", "apt", "apt-get", "dnf", "yum", "zypper", "pacman", "snap",
                 "brew", "winget", "choco", "scoop"}
_orig_run = subprocess.run


def _called_during_import():
    f = sys._getframe(2)
    while f is not None:
        if f.f_code.co_name == "<module>" and str(f.f_globals.get("__name__", "")).startswith("npmai_agents"):
            return True
        f = f.f_back
    return False


def _guarded_run(cmd, *a, **k):
    if isinstance(cmd, (list, tuple)) and cmd:
        if len(cmd) > 2 and cmd[1] == "-m" and cmd[2] == "pip":         
            return subprocess.CompletedProcess(cmd, 0, b"", b"")
        _c0 = os.path.splitext(os.path.basename(str(cmd[0])))[0].lower()
        if _c0 in _SYS_PKG_MGRS and _called_during_import():              
            return subprocess.CompletedProcess(cmd, 0, b"", b"")
    return _orig_run(cmd, *a, **k)


if getattr(sys, "frozen", False):
    subprocess.run = _guarded_run

    if len(sys.argv) > 1:
        _a1 = sys.argv[1]
        if _a1 == "-m":                                
            _attach_std()
            if len(sys.argv) > 2 and sys.argv[2] != "pip":
                sys.argv = sys.argv[2:]
                runpy.run_module(sys.argv[0], run_name="__main__", alter_sys=True)
            sys.exit(0)     
        if _a1.lower().endswith(".py") and os.path.isfile(_a1):   
            _attach_std()
            sys.argv = sys.argv[1:]
            sys.path.insert(0, os.path.dirname(os.path.abspath(_a1)))
            runpy.run_path(_a1, run_name="__main__")
            sys.exit(0)


    for _n in ("stdout", "stderr"):
        if getattr(sys, _n) is None:
            setattr(sys, _n, open(os.devnull, "w"))

    try:
        os.makedirs(os.path.join(getattr(sys, "_MEIPASS", _APP_DIR), "npmai_agents"), exist_ok=True)
    except Exception:
        pass

    _instance_lock = socket.socket()
    try:
        _instance_lock.bind(("127.0.0.1", 47653))
    except OSError:
        sys.exit(0)

    sys.excepthook = _excepthook

import sys, os, math, random, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def resource_path(filename: str) -> str:
    """Resolve a bundled data file (icon, config) whether running from source
    or from a PyInstaller-frozen build. PyInstaller unpacks --add-data files
    next to sys.executable (onedir) or into sys._MEIPASS (onefile); neither
    is the current working directory, so a bare relative path silently fails."""
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


APP_ICON_PATH = resource_path("npmai.png")

try:
    from npmai_agents import AgentBrain, Workspace, CredStore
except Exception:
    _log_crash("npmai_agents import failed")
    _fatal(f"Startup failed.\nDetails saved in:\n{_LOG_DIR / 'crash.log'}")
    sys.exit(1)

import importlib
_pkg = AgentBrain.__module__.rsplit(".", 1)[0]
for _m in ("Tools_Developer_CLI", "Tools_business", "Tools_cloud_devops",
           "Tools_communication_extended", "Tools_creative", "Tools_data_research",
           "Tools_media", "Tools_productivity", "Tools_security_ai", "Tools_system_hardware"):
    try:
        sys.modules.setdefault(_m, importlib.import_module(f"{_pkg}.{_m}"))
    except Exception:
        _log_crash(f"alias for {_m} failed")

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton, QFrame, QScrollArea,
    QStackedWidget, QSizePolicy, QGraphicsOpacityEffect,
    QTabWidget, QDialog, QDialogButtonBox, QMessageBox,
    QGroupBox, QComboBox
)
from PySide6.QtCore import (
    QThread, Signal, Qt, QTimer, QPointF, QRectF, QRect,
    QPropertyAnimation, QEasingCurve,
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush, QPen,
    QPainterPath, QRadialGradient, QIcon
)

P = {
    # Professional light theme (matches screenshot)
    "bg":        "#F8FAFC",   # page background
    "surface":   "#FFFFFF",   # cards / sidebar
    "surface2":  "#F1F5F9",   # subtle secondary surface
    "border":    "#E2E8F0",   # soft borders
    "border2":   "#CBD5E1",   # slightly stronger border
    "text":      "#0F172A",   # primary text
    "text2":     "#334155",   # secondary text
    "muted":     "#64748B",   # muted labels
    "faint":     "#94A3B8",   # very muted
    "primary":   "#1E3A5F",   # deep navy (task pill, Run btn)
    "primary2":  "#1E40AF",   # indigo accent
    "accent":    "#3B82F6",   # blue accent
    "active_bg": "#EFF6FF",   # light blue for active nav
    "active":    "#1D4ED8",   # active nav text
    "success":   "#059669",   # Ready green
    "success_bg":"#ECFDF5",   # Ready pill bg
    "log_bg":    "#0F172A",   # execution log
    "log_text":  "#E2E8F0",
    "log_ok":    "#34D399",
    "log_warn":  "#FBBF24",
    "log_err":   "#F87171",
    # legacy aliases so old references don't crash during transition
    "void": "#F8FAFC", "deep": "#F1F5F9", "space": "#FFFFFF",
    "panel": "#FFFFFF", "lift": "#F8FAFC", "ridge": "#E2E8F0",
    "rim": "#CBD5E1", "glow": "#94A3B8",
    "mint": "#059669", "cyan": "#3B82F6", "violet": "#1E40AF",
    "rose": "#F87171", "amber": "#FBBF24", "sky": "#38BDF8",
    "bright": "#0F172A", "mid": "#64748B", "dim": "#94A3B8",
    "ghost": "#E2E8F0",
}

LLM_PROVIDERS = {
    "npmai":     {"label": "🌐 NPMAI (cloud Ollama — default)", "needs_key": False, "model_label": "Model", "model_default": "llama3.2:3b", "extra_fields": []},
    "local":     {"label": "💻 Local Ollama",                    "needs_key": False, "model_label": "Model", "model_default": "llama3.2:3b", "extra_fields": []},
    "openai":    {"label": "🟢 OpenAI",                          "needs_key": True,  "model_label": "Model", "model_default": "gpt-4o", "extra_fields": []},
    "anthropic": {"label": "🟣 Anthropic",                       "needs_key": True,  "model_label": "Model", "model_default": "claude-sonnet-4-6", "extra_fields": []},
    "gemini":    {"label": "🔵 Google Gemini",                   "needs_key": True,  "model_label": "Model", "model_default": "gemini-2.0-flash", "extra_fields": []},
    "groq":      {"label": "⚡ Groq",                            "needs_key": True,  "model_label": "Model", "model_default": "llama-3.3-70b-versatile", "extra_fields": []},
    "mistral":   {"label": "🌬 Mistral",                         "needs_key": True,  "model_label": "Model", "model_default": "mistral-large-latest", "extra_fields": []},
    "cohere":    {"label": "🔶 Cohere",                          "needs_key": True,  "model_label": "Model", "model_default": "command-r-plus", "extra_fields": []},
    "azure":     {"label": "🔷 Azure OpenAI",                    "needs_key": True,  "model_label": "Deployment", "model_default": "", "extra_fields": [("endpoint","Endpoint URL"),("api_version","API version (default 2024-08-01-preview)")]},
    "bedrock":   {"label": "🟠 AWS Bedrock",                     "needs_key": False, "model_label": "Model ID", "model_default": "anthropic.claude-3-sonnet-20240229-v1:0", "extra_fields": [("region","AWS region (default us-east-1)")]},
    "hf":        {"label": "🤗 HuggingFace",                     "needs_key": True,  "model_label": "Model", "model_default": "meta-llama/Llama-3.1-8B-Instruct", "extra_fields": []},
    "llamacpp":  {"label": "🦙 llama.cpp (local server)",        "needs_key": False, "model_label": "Base URL", "model_default": "http://localhost:8080", "extra_fields": []},
}

AGENT_STAGES = [
    ("planner",      "🧭 Planner",      "Breaks the task into atomic steps"),
    ("tool_manager", "🧰 Tool Manager", "Selects which of the 1371 tools to use"),
    ("coder",        "👨‍💻 Coder",        "Writes the Python for each step"),
    ("auditor",      "🛡 Auditor",       "Reviews code for safety before execution"),
    ("verifier",     "✅ Verifier",      "Confirms a step actually completed"),
    ("chatter",      "💬 Chatter",       "Handles plain conversation (non-task replies)"),
]

_LLM_CONFIG_PATH = Path.home() / ".npmai_agent" / "llm_roles.json"


def _load_llm_stage_config() -> dict:
    cfg = {}
    if _LLM_CONFIG_PATH.exists():
        try:
            cfg = json.loads(_LLM_CONFIG_PATH.read_text())
        except Exception:
            cfg = {}

    for stage_key, _, _ in AGENT_STAGES:
        if stage_key not in cfg:
            cfg[stage_key] = {
                "provider": "npmai", 
                "model": LLM_PROVIDERS["npmai"]["model_default"]
            }
    return cfg


def _save_llm_stage_config(cfg: dict):
    _LLM_CONFIG_PATH.parent.mkdir(exist_ok=True)
    _LLM_CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def _credstore_delete(name: str):
    """CredStore has no delete() — this mirrors its own encryption logic to remove one group."""
    from cryptography.fernet import Fernet
    if not CredStore._PATH.exists():
        return
    try:
        f = Fernet(CredStore._key())
        store = json.loads(f.decrypt(CredStore._PATH.read_bytes()))
        if name in store:
            del store[name]
            CredStore._PATH.write_bytes(f.encrypt(json.dumps(store).encode()))
    except Exception:
        pass


def _build_llm_backend(provider: str, model: str):
    """Mirrors npmai_agents.cli.build_backend — constructs a real LLMBackend from CredStore creds."""
    from npmai_agents import (Ollama_Local, OpenAIBackend, AnthropicBackend, GeminiBackend,
                               GroqBackend, MistralBackend, CohereBackend, AzureOpenAIBackend,
                               BedrockBackend, HuggingFaceBackend, LlamaCppBackend)
    from npmai import Ollama
    p = provider.lower()
    if p == "npmai":       return Ollama(model=model)
    if p == "local":       return Ollama_Local(model=model)
    if p == "openai":      return OpenAIBackend(model=model, api_key=CredStore.load("openai").get("api_key",""))
    if p == "anthropic":   return AnthropicBackend(model=model, api_key=CredStore.load("anthropic").get("api_key",""))
    if p == "gemini":      return GeminiBackend(model=model, api_key=CredStore.load("gemini").get("api_key",""))
    if p == "groq":        return GroqBackend(model=model, api_key=CredStore.load("groq").get("api_key",""))
    if p == "mistral":     return MistralBackend(model=model, api_key=CredStore.load("mistral").get("api_key",""))
    if p == "cohere":      return CohereBackend(model=model, api_key=CredStore.load("cohere").get("api_key",""))
    if p == "azure":
        c = CredStore.load("azure")
        return AzureOpenAIBackend(api_key=c.get("api_key",""), endpoint=c.get("endpoint",""),
                                   deployment=model, api_version=c.get("api_version","2024-08-01-preview"))
    if p == "bedrock":
        c = CredStore.load("bedrock")
        return BedrockBackend(model_id=model, region=c.get("region","us-east-1"))
    if p == "hf":          return HuggingFaceBackend(model=model, api_key=CredStore.load("hf").get("api_key",""))
    if p == "llamacpp":    return LlamaCppBackend(base_url=model or "http://localhost:8080")
    return Ollama(model=model)  # unknown provider -> safe fallback


_TASK_KEYWORDS = [
    "file", "folder", "git", "github", "gitlab", "docker", "kubernetes", "k8s",
    "terraform", "aws", "s3", "lambda", "cloudflare", "vercel", "netlify", "railway",
    "stripe", "razorpay", "shopify", "invoice", "crm", "inventory", "contract",
    "email", "smtp", "teams", "zoom", "twilio", "sendgrid", "webhook", "calendar",
    "notion", "linear", "asana", "trello", "clickup", "todoist", "obsidian",
    "figma", "blender", "svg", "canva", "diagram", "3d",
    "scrape", "download", "screenshot", "database", "report", "chart",
    "ffmpeg", "youtube", "audio", "video", "image", "resize", "convert", "podcast",
    "ssh", "terminal", "run command", "backup", "zip", "unzip", "schedule",
    "encrypt", "scan", "deploy", "network", "printer", "clipboard",
]


def _looks_like_task(text: str) -> bool:
    words = text.strip().split()
    if len(words) > 6:
        return True
    lower = text.lower()
    return any(kw in lower for kw in _TASK_KEYWORDS)


class AgentWorker(QThread):
    log_sig      = Signal(str)
    progress_sig = Signal(int)
    status_sig   = Signal(str)
    done_sig     = Signal(bool, str)
    bubble_sig   = Signal(str, bool)

    def __init__(self, task: str):
        super().__init__()
        self.task     = task
        self._killed  = [False]
        self._brain   = None

    def kill(self):
        self._killed[0] = True
        if self._brain and self._brain.executor:
            self._brain.executor.kill()

    def run(self):
        stage_cfg = _load_llm_stage_config()
        backends = {}
        for stage_key, _, _ in AGENT_STAGES:
            s = stage_cfg.get(stage_key, {"provider": "npmai", "model": LLM_PROVIDERS["npmai"]["model_default"]})
            try:
                backends[stage_key] = _build_llm_backend(s.get("provider","npmai"), s.get("model",""))
            except Exception as e:
                self.log_sig.emit(f'<font color="#FF6B9D">LLM config error for {stage_key} ({s.get("provider")}): {e} — falling back to default.</font>')
                backends[stage_key] = None
        self._brain = AgentBrain(
            log_cb      = self.log_sig.emit,
            progress_cb = self.progress_sig.emit,
            status_cb   = self.status_sig.emit,
            planner      = backends.get("planner"),
            tool_manager = backends.get("tool_manager"),
            coder        = backends.get("coder"),
            auditor      = backends.get("auditor"),
            verifier     = backends.get("verifier"),
            chatter      = backends.get("chatter"),
        )
        """try:
            _cls = getattr(importlib.import_module(f"{_pkg}.Tools_data_research"), "JMTx402AgentTools", None)
            if _cls is not None:
                self._brain.tool_registry.setdefault("JMTx402AgentTools", _cls)
        except Exception:
            pass""" #NEEDED THIS ABOVE THING BUT JMT is planned to deploy in next version of npmai_agents package not in the version right now NPM-AutoCode-AI uses.
        if _looks_like_task(self.task):
            ok = self._brain.run_task(self.task, killed_flag=self._killed)
            msg = "✓ Task completed!" if ok else "✗ Task failed."
            self.bubble_sig.emit(msg, True)
            self.done_sig.emit(ok, msg)
        else:
            resp = self._brain.chat(self.task)
            self.bubble_sig.emit(resp, True)
            self.progress_sig.emit(100)
            self.done_sig.emit(True, resp)


class CosmicBG(QWidget):
    """Clean light page background (name kept for compatibility)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(0, 0, self.width(), self.height(), QColor(P["bg"]))
        p.end()

class GlowCard(QWidget):
    """Clean white card with soft border (name kept for compatibility)."""
    def __init__(self, parent=None, accent=None, radius=12, alpha=255):
        super().__init__(parent)
        self._radius = radius
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self._radius, self._radius)
        p.fillPath(path, QColor(P["surface"]))
        p.setPen(QPen(QColor(P["border"]), 1))
        p.drawPath(path)
        p.end()

class PulseBtn(QPushButton):
    """Primary solid button (Run / task chip style)."""
    def __init__(self, text, accent=None, dark_text=False, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {P['primary']};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background: {P['primary2']}; }}
            QPushButton:pressed {{ background: #0F2744; }}
            QPushButton:disabled {{ background: {P['border2']}; color: {P['faint']}; }}
        """)

class GhostBtn(QPushButton):
    """Secondary outline button (Stop style)."""
    def __init__(self, text, accent=None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {P['surface']};
                color: {P['text2']};
                border: 1px solid {P['border2']};
                border-radius: 10px;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background: {P['surface2']};
                border-color: {P['muted']};
                color: {P['text']};
            }}
            QPushButton:pressed {{ background: {P['border']}; }}
        """)

class GlowInput(QLineEdit):
    """Clean input field matching the screenshot."""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(44)
        self.setFont(QFont("Segoe UI", 13))
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {P['surface']};
                border: 1px solid {P['border']};
                border-radius: 12px;
                padding: 0 16px;
                color: {P['text']};
                selection-background-color: {P['active_bg']};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {P['accent']};
            }}
            QLineEdit::placeholder {{ color: {P['faint']}; }}
        """)

class GlowProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self._val = 0.0
        self._target = 0.0
        QTimer(self, timeout=self._tick, interval=16).start()

    def set_value(self, v):
        self._target = v

    def _tick(self):
        self._val += (self._target - self._val) * 0.08
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        track = QPainterPath()
        track.addRoundedRect(QRectF(0, 0, w, h), h / 2, h / 2)
        p.fillPath(track, QColor(P["border"]))
        fw = w * self._val / 100
        if fw > 2:
            fill = QPainterPath()
            fill.addRoundedRect(QRectF(0, 0, fw, h), h / 2, h / 2)
            p.fillPath(fill, QColor(P["primary"]))
        p.end()

class ChatBubble(QWidget):
    def __init__(self, text: str, is_agent: bool, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setFont(QFont("Segoe UI", 13))
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setMaximumWidth(640)
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        if is_agent:
            bubble.setStyleSheet(f"""
                QLabel {{
                    background: {P['surface']};
                    border: 1px solid {P['border']};
                    border-radius: 14px;
                    padding: 14px 18px;
                    color: {P['text']};
                }}
            """)
            lay.addWidget(bubble)
            lay.addStretch()
        else:
            bubble.setStyleSheet(f"""
                QLabel {{
                    background: {P['active_bg']};
                    border: 1px solid #BFDBFE;
                    border-radius: 14px;
                    padding: 14px 18px;
                    color: {P['text']};
                }}
            """)
            lay.addStretch()
            lay.addWidget(bubble)
        eff = QGraphicsOpacityEffect(bubble)
        bubble.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(280)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._anim = anim

class NavBtn(QWidget):
    clicked = Signal(int)
    # Clean icons matching screenshot style
    ICONS  = ["▶", "🕐", "▦", "⚙", "👤", "📄"]
    LABELS = ["Agent", "History", "Tools", "Settings", "Founder", "Docs"]

    def __init__(self, idx, parent=None):
        super().__init__(parent)
        self._idx = idx
        self._active = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_active(self, v):
        self._active = v
        self.update()

    def mousePressEvent(self, e):
        self.clicked.emit(self._idx)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if self._active:
            path = QPainterPath()
            path.addRoundedRect(QRectF(8, 4, w - 16, h - 8), 10, 10)
            p.fillPath(path, QColor(P["active_bg"]))
            # left accent bar
            bar = QPainterPath()
            bar.addRoundedRect(QRectF(0, 10, 3, h - 20), 1.5, 1.5)
            p.fillPath(bar, QColor(P["active"]))
        # icon + label
        p.setFont(QFont("Segoe UI", 13))
        color = QColor(P["active"] if self._active else P["muted"])
        p.setPen(color)
        p.drawText(QRect(22, 0, 28, h), Qt.AlignVCenter | Qt.AlignLeft, self.ICONS[self._idx])
        p.setFont(QFont("Segoe UI", 13, QFont.DemiBold if self._active else QFont.Normal))
        p.drawText(QRect(52, 0, w - 60, h), Qt.AlignVCenter | Qt.AlignLeft, self.LABELS[self._idx])
        p.end()

class LoginDialog(QDialog):
    """Email/password only, per spec. Appears only when the user clicks
    'Get MCP Link' — never blocks any other part of the app."""

    def __init__(self, link_mgr, parent=None):
        super().__init__(parent)
        self._mgr = link_mgr
        self.setWindowTitle("Log in — MCP Link")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setFixedSize(380, 280)
        self.setStyleSheet(f"QDialog{{background:{P['surface']};}}")
        lay = QVBoxLayout(self); lay.setContentsMargins(28,24,28,24); lay.setSpacing(12)

        title = QLabel("Get your MCP Link")
        title.setFont(QFont("Segoe UI",16,QFont.Bold))
        title.setStyleSheet(f"color:{P['text']};background:transparent;")
        sub = QLabel("Login is only needed here — chat and tasks never require it.")
        sub.setFont(QFont("Segoe UI",11)); sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{P['muted']};background:transparent;")
        lay.addWidget(title); lay.addWidget(sub)

        self._email = GlowInput("Email"); lay.addWidget(self._email)
        self._pw = GlowInput("Password"); self._pw.setEchoMode(QLineEdit.Password)
        lay.addWidget(self._pw)

        row = QHBoxLayout(); row.setSpacing(10)
        login_btn = PulseBtn("Log in")
        signup_btn = GhostBtn("Sign up")
        login_btn.clicked.connect(self._do_login)
        signup_btn.clicked.connect(self._do_signup)
        row.addWidget(login_btn); row.addWidget(signup_btn)
        lay.addLayout(row)

        self._status = QLabel(""); self._status.setWordWrap(True)
        self._status.setFont(QFont("Segoe UI",10))
        self._status.setStyleSheet(f"color:{P['log_err']};background:transparent;")
        lay.addWidget(self._status)

    def _do_login(self):
        try:
            self._mgr.log_in(self._email.text().strip(), self._pw.text())
            self.accept()
        except Exception as e:
            self._status.setText(str(e))

    def _do_signup(self):
        try:
            self._mgr.sign_up(self._email.text().strip(), self._pw.text())
            self.accept()
        except Exception as e:
            self._status.setText(str(e))

class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._btns = []
        self._link_mgr = None
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Logo header (npmai.png + product name) ──
        header = QWidget()
        header.setFixedHeight(72)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 16, 16, 12)
        hl.setSpacing(10)

        logo = QLabel()
        logo.setFixedSize(36, 36)
        logo.setScaledContents(True)
        if os.path.exists(APP_ICON_PATH):
            logo.setPixmap(QIcon(APP_ICON_PATH).pixmap(36, 36))
        else:
            logo.setStyleSheet(f"background:{P['primary']};border-radius:8px;")
            logo.setText("n")
            logo.setAlignment(Qt.AlignCenter)
            logo.setStyleSheet(f"background:{P['primary']};color:white;border-radius:8px;font-weight:bold;")
        hl.addWidget(logo)

        titles = QVBoxLayout()
        titles.setSpacing(1)
        name = QLabel("NPM-AutoCode-AI")
        name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name.setStyleSheet(f"color:{P['text']};background:transparent;")
        ver = QLabel("v3.0 · npmai_agents")
        ver.setFont(QFont("Segoe UI", 10))
        ver.setStyleSheet(f"color:{P['muted']};background:transparent;")
        titles.addWidget(name)
        titles.addWidget(ver)
        hl.addLayout(titles)
        hl.addStretch()
        lay.addWidget(header)

        self._sep(lay)
        lay.addSpacing(8)

        # ── Nav buttons ──
        for i in range(6):
            b = NavBtn(i)
            b.set_active(i == 0)
            b.clicked.connect(self._on_nav)
            self._btns.append(b)
            lay.addWidget(b)

        lay.addStretch()
        self._sep(lay)

        # ── Bottom MCP section ──
        footer = QWidget()
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(14, 12, 14, 16)
        fl.setSpacing(8)

        self._mcp_lbl = QLabel("●  MCP not connected")
        self._mcp_lbl.setFont(QFont("Segoe UI", 11))
        self._mcp_lbl.setStyleSheet(f"""
            color:{P['muted']};
            background:{P['surface2']};
            border-radius:8px;
            padding:8px 12px;
        """)
        fl.addWidget(self._mcp_lbl)

        self._mcp_btn = QPushButton("Get MCP link")
        self._mcp_btn.setCursor(Qt.PointingHandCursor)
        self._mcp_btn.setFixedHeight(36)
        self._mcp_btn.setStyleSheet(f"""
            QPushButton {{
                background:{P['surface']};
                border:1px solid {P['border2']};
                border-radius:8px;
                color:{P['text2']};
                font-size:12px;
                font-family:'Segoe UI';
            }}
            QPushButton:hover {{
                background:{P['surface2']};
                border-color:{P['muted']};
                color:{P['text']};
            }}
        """)
        self._mcp_btn.clicked.connect(self._get_mcp_link)
        fl.addWidget(self._mcp_btn)

        links = QLabel('<a href="https://pypi.org/project/npmai" style="color:#64748B;text-decoration:none;">PyPI</a>  ·  <a href="https://github.com/npmaiecosystem" style="color:#64748B;text-decoration:none;">GitHub</a>')
        links.setFont(QFont("Segoe UI", 10))
        links.setOpenExternalLinks(True)
        links.setAlignment(Qt.AlignCenter)
        links.setStyleSheet("background:transparent;")
        fl.addWidget(links)

        lay.addWidget(footer)

    def _sep(self, lay):
        s = QFrame()
        s.setFixedHeight(1)
        s.setStyleSheet(f"background:{P['border']};border:none;")
        lay.addWidget(s)

    def _on_nav(self, idx):
        for i, b in enumerate(self._btns):
            b.set_active(i == idx)
        self.page_changed.emit(idx)

    def _get_mcp_link(self):
        try:
            from mcp_link import MCPLinkManager, SupabaseAuthError
        except ImportError as e:
            QMessageBox.warning(self, "Missing dependency",
                f"MCP link needs the 'supabase' package.\nRun: pip install supabase\n\n{e}")
            return

        if self._link_mgr is None:
            self._link_mgr = MCPLinkManager(
                log_cb=lambda s: self._mcp_lbl.setText(f"●  {s[:32]}")
            )

        if not self._link_mgr.is_logged_in:
            dlg = LoginDialog(self._link_mgr, self)
            if dlg.exec() != QDialog.Accepted:
                return

        try:
            link = self._link_mgr.get_or_create_link()
            self._link_mgr.start_listener()
            self._mcp_lbl.setText("●  MCP connected")
            self._mcp_lbl.setStyleSheet(f"""
                color:{P['success']};
                background:{P['success_bg']};
                border-radius:8px;
                padding:8px 12px;
            """)
            QMessageBox.information(self, "Your MCP Link",
                f"Paste this into Claude or Grok custom connector settings:\n\n{link}")
        except Exception as e:
            QMessageBox.warning(self, "Couldn't get MCP link", str(e))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(P["surface"]))
        p.setPen(QPen(QColor(P["border"]), 1))
        p.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        p.end()

class LLMConfigDialog(QDialog):
    """'Configure LLMs' — Part ① sets up credentials/args per provider (only the
    fields that provider's backend class actually needs). Part ② assigns a
    provider+model to each of the 6 AgentBrain stages. Saved locally so the
    Agent tab uses it automatically on every run without repeating setup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure LLMs")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.resize(640, 720)
        self.setStyleSheet(f"QDialog{{background:{P['surface']};}}")

        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page=QWidget(); page.setAttribute(Qt.WA_TranslucentBackground)
        lay=QVBoxLayout(page); lay.setContentsMargins(26,22,26,22); lay.setSpacing(16)

        t=QLabel("Configure LLMs"); t.setFont(QFont("Segoe UI",18,QFont.Bold))
        t.setStyleSheet(f"color:{P['text']};background:transparent;"); lay.addWidget(t)
        sub=QLabel("① Add credentials for any provider you plan to use — only the fields that provider "
                    "actually needs are shown. ② Then assign which provider+model handles each of the 6 "
                    "pipeline stages. Everything is saved locally and reused automatically on every run.")
        sub.setFont(QFont("Segoe UI",12)); sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{P['muted']};background:transparent;"); lay.addWidget(sub)

        h1=QLabel("① Provider Credentials"); h1.setFont(QFont("Segoe UI",13,QFont.Bold))
        h1.setStyleSheet(f"color:{P['bright']};background:transparent;"); lay.addWidget(h1)

        self._provider_fields={}
        for pkey,meta in LLM_PROVIDERS.items():
            card=GlowCard(accent=P["cyan"],radius=16,alpha=200)
            cl=QVBoxLayout(card); cl.setContentsMargins(22,16,22,16); cl.setSpacing(8)
            hl=QLabel(meta["label"]); hl.setFont(QFont("Segoe UI",12,QFont.Bold))
            hl.setStyleSheet(f"color:{P['bright']};background:transparent;"); cl.addWidget(hl)
            existing=CredStore.load(pkey)
            fields={}
            if meta["needs_key"]:
                lbl=QLabel("API key"); lbl.setFont(QFont("Segoe UI",9))
                lbl.setStyleSheet(f"color:{P['mid']};background:transparent;"); cl.addWidget(lbl)
                api_in=GlowInput(f"{pkey} API key"); api_in.setEchoMode(QLineEdit.Password)
                if existing.get("api_key"): api_in.setText("●"*8)
                cl.addWidget(api_in); fields["api_key"]=api_in
            for fkey,flabel in meta["extra_fields"]:
                lbl=QLabel(flabel); lbl.setFont(QFont("Segoe UI",9))
                lbl.setStyleSheet(f"color:{P['mid']};background:transparent;"); cl.addWidget(lbl)
                inp=GlowInput(flabel)
                if existing.get(fkey): inp.setText(existing.get(fkey))
                cl.addWidget(inp); fields[fkey]=inp
            if not fields:
                nolbl=QLabel("No credentials needed — runs without an API key.")
                nolbl.setFont(QFont("Segoe UI",9)); nolbl.setStyleSheet(f"color:{P['dim']};background:transparent;")
                cl.addWidget(nolbl)
            else:
                save_btn = PulseBtn(f"💾  Save {pkey}", P["cyan"], True)
                save_btn.setFixedHeight(36)

                def make_save_handler(provider_key, field_widgets):
                    def _save():
                        data = {}
                        for k, w in field_widgets.items():
                            v = w.text().strip()
                            if v and v != "●" * 8:
                                data[k] = v
                        if data:
                            ex = CredStore.load(provider_key)
                            ex.update(data)
                            CredStore.save(provider_key, ex)
                            QMessageBox.information(self, "Saved", f"'{provider_key}' configuration saved.")
                        else:
                            QMessageBox.warning(self, "Nothing to save", "Please enter a real API key (don't leave the masked ●●●●●●●●).")
                    return _save

                save_btn.clicked.connect(make_save_handler(pkey, fields))
                cl.addWidget(save_btn)
            lay.addWidget(card)
            self._provider_fields[pkey]=fields

        sep=QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{P['ghost']};border:none;")
        lay.addWidget(sep)

        h2=QLabel("② Assign Provider + Model per Stage"); h2.setFont(QFont("Segoe UI",13,QFont.Bold))
        h2.setStyleSheet(f"color:{P['bright']};background:transparent;"); lay.addWidget(h2)

        stage_cfg=_load_llm_stage_config()
        self._stage_combo={}; self._stage_model={}
        for skey,slabel,sdesc in AGENT_STAGES:
            card=GlowCard(accent=P["violet"],radius=16,alpha=200)
            cl=QVBoxLayout(card); cl.setContentsMargins(22,16,22,16); cl.setSpacing(8)
            hl=QLabel(slabel); hl.setFont(QFont("Segoe UI",12,QFont.Bold))
            hl.setStyleSheet(f"color:{P['bright']};background:transparent;"); cl.addWidget(hl)
            dl=QLabel(sdesc); dl.setFont(QFont("Segoe UI",9))
            dl.setStyleSheet(f"color:{P['mid']};background:transparent;"); cl.addWidget(dl)
            combo=QComboBox()
            for pkey,meta in LLM_PROVIDERS.items():
                combo.addItem(meta["label"], pkey)
            cur=stage_cfg.get(skey,{}).get("provider","npmai")
            idx=combo.findData(cur)
            if idx>=0: combo.setCurrentIndex(idx)
            combo.setStyleSheet(f"QComboBox{{background:rgba(255,255,255,8);border:1px solid {P['ghost']};"
                                 f"border-radius:8px;color:{P['bright']};padding:6px 10px;}}")
            model_in=GlowInput("model name")
            saved_model=stage_cfg.get(skey,{}).get("model","")
            model_in.setText(saved_model or LLM_PROVIDERS[cur]["model_default"])
            def _provider_changed(i, combo=combo, model_in=model_in):
                pkey=combo.itemData(i)
                if not model_in.text().strip():
                    model_in.setText(LLM_PROVIDERS[pkey]["model_default"])
            combo.currentIndexChanged.connect(_provider_changed)
            cl.addWidget(combo); cl.addWidget(model_in)
            lay.addWidget(card)
            self._stage_combo[skey]=combo; self._stage_model[skey]=model_in

        save_all_btn=PulseBtn("💾  Save Stage Assignments",P["mint"],True); save_all_btn.setFixedHeight(44)
        save_all_btn.clicked.connect(self._save_all_stages)
        lay.addWidget(save_all_btn)

        close_btn=GhostBtn("Close",P["rose"]); close_btn.clicked.connect(self.accept)
        lay.addWidget(close_btn)

        lay.addStretch(); scroll.setWidget(page); outer.addWidget(scroll)

    def _save_all_stages(self):
        cfg=_load_llm_stage_config()
        missing=[]
        for skey,slabel,_ in AGENT_STAGES:
            combo=self._stage_combo[skey]; pkey=combo.currentData()
            model_val=self._stage_model[skey].text().strip() or LLM_PROVIDERS[pkey]["model_default"]
            meta=LLM_PROVIDERS[pkey]
            if meta["needs_key"] and not CredStore.load(pkey).get("api_key"):
                missing.append(f"{slabel} → {meta['label']}")
            cfg[skey]={"provider":pkey,"model":model_val}
        _save_llm_stage_config(cfg)
        if missing:
            QMessageBox.warning(self,"Missing API keys",
                "Stage assignments saved, but these still need an API key added in section ① above "
                "before they'll actually run:\n\n" + "\n".join(f"- {m}" for m in missing))
        else:
            QMessageBox.information(self,"Saved","LLM configuration saved — used automatically on every run.")


class AgentPage(QWidget):
    STAGES = ["Planner", "Tool manager", "Coder", "Auditor", "Verifier"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._worker = None
        self._killed = [False]
        self._stage_idx = -1
        self._type_timer = None
        self._type_text = ""
        self._type_pos = 0
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 20, 28, 20)
        outer.setSpacing(16)

        # Header: title + Ready pill
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Agent")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color:{P['text']};background:transparent;")
        sub = QLabel("Describe a task. It plans, codes, audits, runs and verifies.")
        sub.setFont(QFont("Segoe UI", 13))
        sub.setStyleSheet(f"color:{P['muted']};background:transparent;")
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        # Configure LLMs button
        llm_btn = GhostBtn("Configure LLMs")
        llm_btn.setFixedHeight(36)
        llm_btn.clicked.connect(self._open_llm_config)
        header.addWidget(llm_btn)

        self._ready_pill = QLabel("●  Ready")
        self._ready_pill.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._ready_pill.setStyleSheet(f"""
            color:{P['success']};
            background:{P['success_bg']};
            border-radius:14px;
            padding:6px 14px;
        """)
        header.addWidget(self._ready_pill)
        outer.addLayout(header)

        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"background:{P['primary']};border:none;")
        outer.addWidget(line)

        # Progress stepper
        stepper_row = QHBoxLayout()
        stepper_row.setSpacing(0)
        self._stage_labels = []
        self._stage_dots = []
        for i, name in enumerate(self.STAGES):
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignCenter)
            col.setSpacing(6)
            dot = QLabel("○")
            dot.setFont(QFont("Segoe UI", 16))
            dot.setAlignment(Qt.AlignCenter)
            dot.setStyleSheet(f"color:{P['border2']};background:transparent;")
            lbl = QLabel(name)
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color:{P['faint']};background:transparent;")
            col.addWidget(dot)
            col.addWidget(lbl)
            self._stage_dots.append(dot)
            self._stage_labels.append(lbl)
            stepper_row.addLayout(col, 1)
            if i < len(self.STAGES) - 1:
                conn = QFrame()
                conn.setFixedHeight(2)
                conn.setStyleSheet(f"background:{P['border']};border:none;margin-top:10px;")
                stepper_row.addWidget(conn, 1)
        outer.addLayout(stepper_row)
        outer.addSpacing(4)

        # Task chip
        chip_row = QHBoxLayout()
        chip_row.addStretch()
        self._task_chip = QLabel("")
        self._task_chip.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._task_chip.setStyleSheet(f"""
            color:white;
            background:{P['primary']};
            border-radius:16px;
            padding:8px 18px;
        """)
        self._task_chip.hide()
        chip_row.addWidget(self._task_chip)
        outer.addLayout(chip_row)

        # Agent status card
        self._status_card = QFrame()
        self._status_card.setStyleSheet(f"""
            QFrame {{
                background:{P['surface']};
                border:1px solid {P['border']};
                border-radius:14px;
            }}
        """)
        sc_lay = QVBoxLayout(self._status_card)
        sc_lay.setContentsMargins(18, 14, 18, 14)
        sc_lay.setSpacing(6)
        agent_tag = QLabel("Agent")
        agent_tag.setFont(QFont("Segoe UI", 11))
        agent_tag.setStyleSheet(f"color:{P['faint']};background:transparent;")
        self._status_body = QLabel("Ready. Describe a task below.")
        self._status_body.setFont(QFont("Segoe UI", 14))
        self._status_body.setWordWrap(True)
        self._status_body.setStyleSheet(f"color:{P['text']};background:transparent;")
        self._step_lbl = QLabel("")
        self._step_lbl.setFont(QFont("Segoe UI", 11))
        self._step_lbl.setStyleSheet(f"color:{P['muted']};background:transparent;")
        sc_lay.addWidget(agent_tag)
        sc_lay.addWidget(self._status_body)
        sc_lay.addWidget(self._step_lbl)
        outer.addWidget(self._status_card)

        # Execution log
        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setFont(QFont("Cascadia Code", 11))
        self._log_box.setMinimumHeight(180)
        self._log_box.setStyleSheet(f"""
            QTextEdit {{
                background:{P['log_bg']};
                border:none;
                border-radius:12px;
                padding:14px;
                color:{P['log_text']};
            }}
        """)
        self._log_box.setHtml('<span style="color:#64748B">Execution log</span>')
        outer.addWidget(self._log_box, 1)

        # Input row
        irow = QHBoxLayout()
        irow.setSpacing(10)
        self._input = GlowInput("Describe a task in plain English")
        self._input.returnPressed.connect(self._send)
        self._kill_btn = GhostBtn("Stop")
        self._kill_btn.setFixedWidth(80)
        self._kill_btn.clicked.connect(self._kill)
        self._kill_btn.setEnabled(False)
        self._run_btn = PulseBtn("Run")
        self._run_btn.setFixedWidth(90)
        self._run_btn.clicked.connect(self._send)
        irow.addWidget(self._input, 1)
        irow.addWidget(self._kill_btn)
        irow.addWidget(self._run_btn)
        outer.addLayout(irow)

        # Hidden helpers kept for worker signals
        self._prog = GlowProgress()
        self._prog.hide()
        self._pct_lbl = QLabel("")
        self._pct_lbl.hide()
        self._status_lbl = QLabel("Ready")
        self._status_lbl.hide()

    def _set_stage(self, idx: int):
        self._stage_idx = idx
        for i, (dot, lbl) in enumerate(zip(self._stage_dots, self._stage_labels)):
            if i < idx:
                dot.setText("✓")
                dot.setStyleSheet(f"color:{P['primary']};background:transparent;")
                lbl.setStyleSheet(f"color:{P['primary']};background:transparent;")
            elif i == idx:
                dot.setText("◉")
                dot.setStyleSheet(f"color:{P['primary']};background:transparent;")
                lbl.setStyleSheet(f"color:{P['primary']};background:transparent;font-weight:600;")
            else:
                dot.setText("○")
                dot.setStyleSheet(f"color:{P['border2']};background:transparent;")
                lbl.setStyleSheet(f"color:{P['faint']};background:transparent;")

    def _type_status(self, text: str):
        if self._type_timer:
            self._type_timer.stop()
        self._type_text = text
        self._type_pos = 0
        self._status_body.setText("")
        self._type_timer = QTimer(self)
        self._type_timer.timeout.connect(self._type_tick)
        self._type_timer.start(18)

    def _type_tick(self):
        self._type_pos += 1
        if self._type_pos >= len(self._type_text):
            self._status_body.setText(self._type_text)
            self._type_timer.stop()
        else:
            self._status_body.setText(self._type_text[:self._type_pos] + "▋")

    def _open_llm_config(self):
        dlg = LLMConfigDialog(self)
        dlg.exec()

    def _add_bubble(self, text: str, is_agent: bool):
        if is_agent:
            self._type_status(text)

    def _log(self, html: str):
        self._log_box.append(html)
        self._log_box.verticalScrollBar().setValue(self._log_box.verticalScrollBar().maximum())
        low = html.lower()
        if "planner" in low:
            self._set_stage(0)
        elif "tool" in low and "manager" in low:
            self._set_stage(1)
        elif "coder" in low or "writing" in low:
            self._set_stage(2)
        elif "auditor" in low or "audit" in low:
            self._set_stage(3)
        elif "verifier" in low or "verify" in low:
            self._set_stage(4)

    def _voice_input(self):
        from npmai_agents.Tools_security_ai import SpeechAITool
        r = SpeechAITool.transcribe_realtime(duration=5)
        if r.success and r.data:
            self._input.setText(r.data.get("text", ""))

    def _kill(self):
        if self._worker:
            self._worker.kill()
        self._kill_btn.setEnabled(False)
        self._run_btn.setEnabled(True)
        self._run_btn.setText("Run")
        self._ready_pill.setText("●  Ready")
        self._ready_pill.setStyleSheet(f"""
            color:{P['success']};background:{P['success_bg']};
            border-radius:14px;padding:6px 14px;
        """)

    def _send(self):
        task = self._input.text().strip()
        if not task:
            return
        self._input.clear()
        self._task_chip.setText(task[:60] + ("…" if len(task) > 60 else ""))
        self._task_chip.show()
        self._type_status("Planning your task…")
        self._step_lbl.setText("")
        self._set_stage(0)
        self._run_btn.setEnabled(False)
        self._run_btn.setText("…")
        self._kill_btn.setEnabled(True)
        self._ready_pill.setText("●  Running")
        self._ready_pill.setStyleSheet("""
            color:#B45309;background:#FFFBEB;
            border-radius:14px;padding:6px 14px;
        """)
        self._prog.set_value(3)
        self._log_box.clear()
        self._log_box.setHtml('<span style="color:#64748B">Execution log</span>')
        self._worker = AgentWorker(task)
        self._worker.log_sig.connect(self._log)
        self._worker.progress_sig.connect(self._prog.set_value)
        self._worker.status_sig.connect(lambda s: self._step_lbl.setText(s))
        self._worker.bubble_sig.connect(self._add_bubble)
        self._worker.done_sig.connect(self._done)
        self._worker.start()

    def _done(self, ok: bool, msg: str):
        self._run_btn.setEnabled(True)
        self._run_btn.setText("Run")
        self._kill_btn.setEnabled(False)
        if ok:
            self._set_stage(5)
            self._type_status(msg if msg else "Task completed successfully.")
            self._ready_pill.setText("●  Ready")
            self._ready_pill.setStyleSheet(f"""
                color:{P['success']};background:{P['success_bg']};
                border-radius:14px;padding:6px 14px;
            """)
        else:
            self._type_status(msg if msg else "Task failed.")
            self._ready_pill.setText("●  Failed")
            self._ready_pill.setStyleSheet("""
                color:#B91C1C;background:#FEF2F2;
                border-radius:14px;padding:6px 14px;
            """)


class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page = QWidget()
        page.setAttribute(Qt.WA_TranslucentBackground)
        self._lay = QVBoxLayout(page)
        self._lay.setContentsMargins(36, 36, 36, 36)
        self._lay.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel("Task History")
        t.setFont(QFont("Segoe UI", 22, QFont.Bold))
        t.setStyleSheet(f"color:{P['text']};background:transparent;")
        refresh = GhostBtn("Refresh")
        refresh.setFixedSize(100, 36)
        refresh.clicked.connect(self.load)
        header.addWidget(t)
        header.addStretch()
        header.addWidget(refresh)
        self._lay.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{P['border']};border:none;")
        self._lay.addWidget(sep)
        self._lay.addSpacing(8)

        self._items_layout = QVBoxLayout()
        self._items_layout.setSpacing(8)
        self._lay.addLayout(self._items_layout)
        self._lay.addStretch()
        scroll.setWidget(page)
        outer.addWidget(scroll)
        self.load()

    def load(self):
        while self._items_layout.count():
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        history = AgentBrain.load_task_history()
        if not history:
            lbl = QLabel("No tasks run yet. Go to Agent tab and run your first task.")
            lbl.setFont(QFont("Segoe UI", 13))
            lbl.setStyleSheet(f"color:{P['muted']};background:transparent;")
            self._items_layout.addWidget(lbl)
            return
        for entry in history:
            row = GlowCard(radius=12)
            row.setFixedHeight(68)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(18, 12, 18, 12)
            rl.setSpacing(14)
            ok = entry.get("success", False)
            badge = QLabel("✓" if ok else "✗")
            badge.setFont(QFont("Segoe UI", 14, QFont.Bold))
            badge.setFixedSize(28, 28)
            badge.setAlignment(Qt.AlignCenter)
            if ok:
                badge.setStyleSheet(f"color:{P['success']};background:{P['success_bg']};border-radius:14px;")
            else:
                badge.setStyleSheet("color:#B91C1C;background:#FEF2F2;border-radius:14px;")
            tc = QVBoxLayout()
            tc.setSpacing(2)
            task_lbl = QLabel(entry["task"][:90] + ("…" if len(entry["task"]) > 90 else ""))
            task_lbl.setFont(QFont("Segoe UI", 13))
            task_lbl.setStyleSheet(f"color:{P['text']};background:transparent;")
            time_lbl = QLabel(entry.get("time", "")[:19].replace("T", " "))
            time_lbl.setFont(QFont("Segoe UI", 11))
            time_lbl.setStyleSheet(f"color:{P['muted']};background:transparent;")
            tc.addWidget(task_lbl)
            tc.addWidget(time_lbl)
            rl.addWidget(badge)
            rl.addLayout(tc)
            rl.addStretch()
            self._items_layout.addWidget(row)


def _discover_real_tools():
    import npmai_agents as pkg
    tools = []
    for attr_name in dir(pkg):
        obj = getattr(pkg, attr_name)
        if isinstance(obj, type) and hasattr(obj, "name") and hasattr(obj, "description"):
            tools.append((getattr(obj, "name"), attr_name, getattr(obj, "description")))
    return sorted(tools, key=lambda t: t[1])


class ToolsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page = QWidget()
        page.setAttribute(Qt.WA_TranslucentBackground)
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(16)

        tools = _discover_real_tools()
        t = QLabel(f"Tool Registry — {len(tools)} Integrated Tools")
        t.setFont(QFont("Segoe UI", 22, QFont.Bold))
        t.setStyleSheet(f"color:{P['text']};background:transparent;")
        lay.addWidget(t)

        desc = QLabel(
            "Read directly from npmai_agents — always matches what's installed. "
            "All tools are available to the agent automatically; just describe your task."
        )
        desc.setFont(QFont("Segoe UI", 13))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{P['muted']};background:transparent;")
        lay.addWidget(desc)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{P['border']};border:none;")
        lay.addWidget(sep)
        lay.addSpacing(6)

        grid_cols = 2
        grid_row = None
        for i, (tool_name, cls_name, description) in enumerate(tools):
            if i % grid_cols == 0:
                grid_row = QHBoxLayout()
                grid_row.setSpacing(14)
                lay.addLayout(grid_row)
            card = GlowCard(radius=12)
            card.setFixedHeight(100)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(4)
            n = QLabel(cls_name)
            n.setFont(QFont("Segoe UI", 13, QFont.Bold))
            n.setStyleSheet(f"color:{P['text']};background:transparent;")
            c2 = QLabel(tool_name)
            c2.setFont(QFont("Cascadia Code", 10))
            c2.setStyleSheet(f"color:{P['primary2']};background:transparent;")
            d = QLabel(description[:130] + ("…" if len(description) > 130 else ""))
            d.setFont(QFont("Segoe UI", 11))
            d.setWordWrap(True)
            d.setStyleSheet(f"color:{P['muted']};background:transparent;")
            cl.addWidget(n)
            cl.addWidget(c2)
            cl.addWidget(d)
            grid_row.addWidget(card)
        if len(tools) % grid_cols != 0 and grid_row is not None:
            grid_row.addStretch()

        lay.addStretch()
        scroll.setWidget(page)
        outer.addWidget(scroll)


class CredKeyValueDialog(QDialog):
    """Generic credential-group editor — user names the group (cred_key) and adds
    any number of key/value pairs. Used by '+ Add Credential Group' in Settings
    and by the per-provider forms inside Configure LLMs on the Agent page."""

    def __init__(self, parent=None, group_name="", existing_data=None, lock_name=False,
                 title="🔑  Credential Group", subtitle=None):
        super().__init__(parent)
        self.setWindowTitle(title.replace("🔑","").strip() or "Credential Group")
        self.setMinimumWidth(440)
        self.setStyleSheet(f"QDialog{{background:{P['surface']};}}")
        self._row_widgets = []

        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))
        else:
            print(f"Warning: npmai.png not found at {APP_ICON_PATH}")

        lay = QVBoxLayout(self); lay.setContentsMargins(26,22,26,22); lay.setSpacing(12)

        t = QLabel(title); t.setFont(QFont("Segoe UI",15,QFont.Bold))
        t.setStyleSheet(f"color:{P['mint']};background:transparent;"); lay.addWidget(t)

        sub = QLabel(subtitle or ("Give this group a name (e.g. 'twilio', 'mailchimp') — check Docs for "
                     "the exact keys a tool expects — then add each key/value pair below."))
        sub.setFont(QFont("Segoe UI",9)); sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{P['mid']};background:transparent;"); lay.addWidget(sub)

        self._name_input = GlowInput("Group name, e.g. twilio")
        if group_name: self._name_input.setText(group_name)
        self._name_input.setEnabled(not lock_name)
        lay.addWidget(self._name_input)

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{P['ghost']};border:none;")
        lay.addWidget(sep)

        self._rows_container = QWidget(); self._rows_container.setAttribute(Qt.WA_TranslucentBackground)
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0,0,0,0); self._rows_layout.setSpacing(8)
        lay.addWidget(self._rows_container)

        add_row_btn = GhostBtn("+  Add Key", P["cyan"])
        add_row_btn.clicked.connect(self._add_row)   # Removed unnecessary lambda
        lay.addWidget(add_row_btn)

        existing_data = existing_data or {}
        if existing_data:
            for k, v in existing_data.items(): self._add_row(k, v)
        else:
            self._add_row()

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _add_row(self, key="", value=""):
        row = QWidget(); row.setAttribute(Qt.WA_TranslucentBackground)
        rl = QHBoxLayout(row); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)
        key_in = GlowInput("key name, e.g. token"); key_in.setText(key)
        val_in = GlowInput("value"); val_in.setText(value)
        rm_btn = GhostBtn("✕", P["rose"]); rm_btn.setFixedWidth(36)
        
        def _remove():
            self._rows_layout.removeWidget(row); row.deleteLater()
            self._row_widgets[:] = [r for r in self._row_widgets if r[2] is not row]
        
        rm_btn.clicked.connect(_remove)
        rl.addWidget(key_in,1); rl.addWidget(val_in,2); rl.addWidget(rm_btn)
        self._rows_layout.addWidget(row)
        self._row_widgets.append((key_in, val_in, row))

    def get_data(self):
        """Returns (group_name:str, data:dict) — rows with an empty key are skipped."""
        name = self._name_input.text().strip()
        data = {}
        for key_in, val_in, _ in self._row_widgets:
            k = key_in.text().strip(); v = val_in.text().strip()
            if k: data[k] = v
        return name, data



class SettingsPage(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.setAttribute(Qt.WA_TranslucentBackground); self._build()

    def _section(self, lay, title, fields, cred_key, accent=None):
        card=GlowCard(radius=12)
        cl=QVBoxLayout(card); cl.setContentsMargins(24,20,24,20); cl.setSpacing(12)
        h=QLabel(title); h.setFont(QFont("Segoe UI",14,QFont.Bold))
        h.setStyleSheet(f"color:{P['text']};background:transparent;"); cl.addWidget(h)
        sep=QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{P['border']};border:none;")
        cl.addWidget(sep)
        inputs={}
        for field_key,label,placeholder,is_pw in fields:
            lbl=QLabel(label); lbl.setFont(QFont("Segoe UI",11))
            lbl.setStyleSheet(f"color:{P['muted']};background:transparent;"); cl.addWidget(lbl)
            inp=GlowInput(placeholder)
            if is_pw: inp.setEchoMode(QLineEdit.Password)
            existing=CredStore.load(cred_key).get(field_key,"")
            if existing: inp.setText("●"*8 if is_pw else existing)
            inputs[field_key]=inp; cl.addWidget(inp)
        save_btn=PulseBtn(f"Save {title.split()[0]} Credentials")
        save_btn.setFixedHeight(40)
        def _save(ck=cred_key,inp_ref=inputs):
            data={}
            for k,w in inp_ref.items():
                v=w.text().strip()
                if v and v!="●"*8: data[k]=v
            existing=CredStore.load(ck)
            existing.update(data); CredStore.save(ck,existing)
            QMessageBox.information(self,"Saved",f"{ck} credentials saved securely.")
        save_btn.clicked.connect(_save); cl.addWidget(save_btn)
        lay.addWidget(card)

    def _build(self):
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page=QWidget(); page.setAttribute(Qt.WA_TranslucentBackground)
        lay=QVBoxLayout(page); lay.setContentsMargins(36,36,36,36); lay.setSpacing(20)
        t=QLabel("Settings & Credentials"); t.setFont(QFont("Segoe UI",22,QFont.Bold))
        t.setStyleSheet(f"color:{P['text']};background:transparent;"); lay.addWidget(t)
        sub=QLabel("All credentials are encrypted with a machine-specific key (CredStore) and stored "
                    "locally. Never sent anywhere. No login needed for anything on this page.")
        sub.setFont(QFont("Segoe UI",13)); sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{P['muted']};background:transparent;"); lay.addWidget(sub)
        sep=QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{P['border']};border:none;")
        lay.addWidget(sep); lay.addSpacing(6)

        ws_card=GlowCard(radius=12)
        wl=QHBoxLayout(ws_card); wl.setContentsMargins(22,16,22,16); wl.setSpacing(16)
        wl_v=QVBoxLayout(); wl_v.setSpacing(4)
        wl_t=QLabel("Workspace Scanner"); wl_t.setFont(QFont("Segoe UI",14,QFont.Bold))
        wl_t.setStyleSheet(f"color:{P['text']};background:transparent;")
        wl_d=QLabel("Scans your Desktop, Downloads, Documents, Pictures, Videos, Music — agent uses this to understand your file system")
        wl_d.setFont(QFont("Segoe UI",12)); wl_d.setWordWrap(True)
        wl_d.setStyleSheet(f"color:{P['muted']};background:transparent;")
        wl_v.addWidget(wl_t); wl_v.addWidget(wl_d)
        scan_btn=PulseBtn("Scan Now"); scan_btn.setFixedSize(120,38)
        def _scan():
            ws=Workspace(); ws.scan()
            QMessageBox.information(self,"Scanned","Workspace scanned successfully!")
        scan_btn.clicked.connect(_scan); wl.addLayout(wl_v); wl.addStretch(); wl.addWidget(scan_btn)
        lay.addWidget(ws_card)

        # Configure LLMs entry
        llm_card = GlowCard(radius=12)
        ll = QHBoxLayout(llm_card)
        ll.setContentsMargins(22, 16, 22, 16)
        ll.setSpacing(16)
        ll_v = QVBoxLayout()
        ll_v.setSpacing(4)
        ll_t = QLabel("Configure LLMs")
        ll_t.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ll_t.setStyleSheet(f"color:{P['text']};background:transparent;")
        ll_d = QLabel("Assign which provider + model handles each pipeline stage (Planner, Tool Manager, Coder, Auditor, Verifier, Chatter). Credentials are saved locally.")
        ll_d.setFont(QFont("Segoe UI", 12))
        ll_d.setWordWrap(True)
        ll_d.setStyleSheet(f"color:{P['muted']};background:transparent;")
        ll_v.addWidget(ll_t)
        ll_v.addWidget(ll_d)
        llm_open = PulseBtn("Open")
        llm_open.setFixedSize(100, 38)
        llm_open.clicked.connect(lambda: LLMConfigDialog(self).exec())
        ll.addLayout(ll_v)
        ll.addStretch()
        ll.addWidget(llm_open)
        lay.addWidget(llm_card)

        # ── Credential sections — cred_key + fields verified against source ──
        self._section(lay,"⭐ GitHub",[
            ("token","Personal access token (repo + issues scope)","ghp_xxxxxxxxxxxx",True),
        ],"github",P["cyan"])

        self._section(lay,"📧 Email (SMTP)",[
            ("email","Email address","your@gmail.com",False),
            ("password","App password","Gmail app password",True),
            ("smtp_host","SMTP host","smtp.gmail.com",False),
            ("smtp_port","SMTP port","587",False),
        ],"smtp",P["mint"])

        self._section(lay,"📓 Notion",[
            ("token","Integration token","secret_xxxxxxxxxxxx",True),
        ],"notion",P["amber"])

        self._section(lay,"💳 Stripe",[
            ("secret_key","Secret key","sk_live_xxxxxxxxxxxx",True),
        ],"stripe",P["violet"])

        self._section(lay,"☁ AWS",[
            ("access_key_id","Access key ID","AKIA...",False),
            ("secret_access_key","Secret access key","",True),
            ("region","Region","us-east-1",False),
        ],"aws",P["sky"])

        note=QLabel("Need a tool that isn't listed above (Twilio, GitLab, Stripe alternatives, Mailchimp, "
                     "Notion, Zoom, Cloudflare, and 30+ more)? Use '+ Add Credential Group' below — see the "
                     "Docs tab for the exact cred_key and field names each tool expects.")
        note.setFont(QFont("Segoe UI",9)); note.setWordWrap(True)
        note.setStyleSheet(f"color:{P['dim']};background:transparent;"); lay.addWidget(note)

        # ── Generic custom credential groups — for any tool not hardcoded above ──
        custom_hdr=QHBoxLayout(); custom_hdr.setSpacing(12)
        custom_t=QLabel("🗂  Custom Credential Groups"); custom_t.setFont(QFont("Segoe UI",13,QFont.Bold))
        custom_t.setStyleSheet(f"color:{P['bright']};background:transparent;")
        custom_hdr.addWidget(custom_t); custom_hdr.addStretch()
        add_group_btn=PulseBtn("➕  Add Credential Group",P["violet"],True); add_group_btn.setFixedHeight(38)
        add_group_btn.clicked.connect(self._open_add_dialog)
        custom_hdr.addWidget(add_group_btn)
        lay.addLayout(custom_hdr)

        self._custom_creds_container=QWidget(); self._custom_creds_container.setAttribute(Qt.WA_TranslucentBackground)
        self._custom_creds_layout=QVBoxLayout(self._custom_creds_container)
        self._custom_creds_layout.setContentsMargins(0,0,0,0); self._custom_creds_layout.setSpacing(10)
        lay.addWidget(self._custom_creds_container)
        self._refresh_custom_creds()

        mcp_card=GlowCard(accent=P["mint"],radius=16,alpha=195)
        ml=QVBoxLayout(mcp_card); ml.setContentsMargins(24,18,24,18); ml.setSpacing(8)
        mt=QLabel("🔗  MCP Link"); mt.setFont(QFont("Segoe UI",13,QFont.Bold))
        mt.setStyleSheet(f"color:{P['bright']};background:transparent;"); ml.addWidget(mt)
        md=QLabel(
            "Click 'Get MCP Link' in the sidebar to log in and receive your personal link. "
            "Paste it into Claude/Grok's custom connector settings — this app then executes "
            "already-audited code sent by the hosted MCP server and reports results back.\n"
            "This is the ONLY feature in the app that requires login."
        )
        md.setFont(QFont("Segoe UI",10)); md.setWordWrap(True)
        md.setStyleSheet(f"color:{P['mid']};background:transparent;"); ml.addWidget(md)
        lay.addWidget(mcp_card)
        lay.addStretch(); scroll.setWidget(page); outer.addWidget(scroll)

    _HARDCODED_KEYS = {"github","smtp","notion","stripe","aws"}

    def _refresh_custom_creds(self):
        while self._custom_creds_layout.count():
            item=self._custom_creds_layout.takeAt(0)
            w=item.widget()
            if w: w.deleteLater()
        hidden=self._HARDCODED_KEYS | set(LLM_PROVIDERS.keys())
        try: names=[n for n in CredStore.all_keys() if n not in hidden]
        except Exception: names=[]
        if not names:
            empty=QLabel("No custom credential groups yet — click '➕ Add Credential Group' above.")
            empty.setFont(QFont("Segoe UI",9)); empty.setStyleSheet(f"color:{P['dim']};background:transparent;")
            self._custom_creds_layout.addWidget(empty); return
        for name in names:
            data=CredStore.load(name)
            card=GlowCard(accent=P["sky"],radius=14,alpha=195)
            cl=QHBoxLayout(card); cl.setContentsMargins(20,14,20,14); cl.setSpacing(12)
            info=QVBoxLayout(); info.setSpacing(2)
            nl=QLabel(f"🔑 {name}"); nl.setFont(QFont("Segoe UI",11,QFont.Bold))
            nl.setStyleSheet(f"color:{P['bright']};background:transparent;")
            kl=QLabel(", ".join(data.keys()) if data else "no keys saved")
            kl.setFont(QFont("Segoe UI",9)); kl.setStyleSheet(f"color:{P['mid']};background:transparent;")
            info.addWidget(nl); info.addWidget(kl)
            cl.addLayout(info); cl.addStretch()
            edit_btn=GhostBtn("Edit",P["cyan"]); edit_btn.setFixedWidth(70)
            edit_btn.clicked.connect(lambda _,n=name: self._open_edit_dialog(n))
            del_btn=GhostBtn("Delete",P["rose"]); del_btn.setFixedWidth(70)
            del_btn.clicked.connect(lambda _,n=name: self._delete_group(n))
            cl.addWidget(edit_btn); cl.addWidget(del_btn)
            self._custom_creds_layout.addWidget(card)

    def _open_add_dialog(self):
        dlg=CredKeyValueDialog(self)
        if dlg.exec():
            name,data=dlg.get_data()
        if not name:
            QMessageBox.warning(self,"Missing name","Please enter a group name."); return
        if not data:
            QMessageBox.warning(self,"No keys","Add at least one key/value pair."); return
        existing=CredStore.load(name); existing.update(data); CredStore.save(name,existing)
        QMessageBox.information(self,"Saved",f"'{name}' credentials saved securely.")
        self._refresh_custom_creds()

    def _open_edit_dialog(self, name):
        data=CredStore.load(name)
        dlg=CredKeyValueDialog(self, group_name=name, existing_data=data, lock_name=True,
                                title=f"🔑  Edit '{name}'")
        if dlg.exec():
            _,new_data=dlg.get_data(); CredStore.save(name,new_data)
            QMessageBox.information(self,"Updated",f"'{name}' credentials updated.")
            self._refresh_custom_creds()

    def _delete_group(self, name):
        reply=QMessageBox.question(self,"Delete",f"Delete all credentials saved under '{name}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.Yes:
            _credstore_delete(name); self._refresh_custom_creds()


class FounderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page = QWidget()
        page.setAttribute(Qt.WA_TranslucentBackground)
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        import webbrowser
        t = QLabel("The Founder")
        t.setFont(QFont("Segoe UI", 22, QFont.Bold))
        t.setStyleSheet(f"color:{P['text']};background:transparent;")
        lay.addWidget(t)

        hero = GlowCard(radius=16)
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(28, 24, 28, 24)
        hl.setSpacing(10)

        name = QLabel("Sonu Kumar  🇮🇳")
        name.setFont(QFont("Segoe UI", 22, QFont.Bold))
        name.setStyleSheet(f"color:{P['text']};background:transparent;")
        hl.addWidget(name)

        tag = QLabel("Founder · NPMAI ECOSYSTEM · Bihar Viral Boy · TEDx Speaker")
        tag.setFont(QFont("Segoe UI", 13))
        tag.setStyleSheet(f"color:{P['primary2']};background:transparent;")
        hl.addWidget(tag)

        bio = QLabel(
            "Age 15 · Bihar, India · Based in Kota, Rajasthan\n"
            "Self-taught AI developer. No CS degree. Built the entire NPMAI ecosystem on free cloud infrastructure.\n"
            "Student at Allen Career Institute & Disha Delphi Public School (100% scholarship since 2022).\n\n"
            "Age 9 — started teaching nursery kids while in 4th grade.\n"
            "Age 11 — \"Bihar Viral Boy\": challenged the Chief Minister on education & liquor ban; went viral nationally.\n"
            "Age 13 — one of India's youngest TEDx speakers (rural education & tech divide).\n"
            "Age 13–15 — founded NPMAI ECOSYSTEM. 10 research papers spanning AI, chemistry, mathematics & constitutional law."
        )
        bio.setFont(QFont("Segoe UI", 12))
        bio.setWordWrap(True)
        bio.setStyleSheet(f"color:{P['text2']};background:transparent;line-height:1.5;")
        hl.addWidget(bio)

        stats = QHBoxLayout()
        stats.setSpacing(12)
        for val, label in [
            ("4M+", "npmai downloads"),
            ("900K+", "npmai_agents"),
            ("440K+", "followers"),
            ("10", "research papers"),
            ("TEDx", "Speaker at 13"),
        ]:
            box = QFrame()
            box.setStyleSheet(f"background:{P['surface2']};border-radius:10px;padding:8px;")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(12, 8, 12, 8)
            bl.setSpacing(2)
            v = QLabel(val)
            v.setFont(QFont("Segoe UI", 16, QFont.Bold))
            v.setStyleSheet(f"color:{P['primary']};background:transparent;")
            v.setAlignment(Qt.AlignCenter)
            l = QLabel(label)
            l.setFont(QFont("Segoe UI", 10))
            l.setStyleSheet(f"color:{P['muted']};background:transparent;")
            l.setAlignment(Qt.AlignCenter)
            bl.addWidget(v)
            bl.addWidget(l)
            stats.addWidget(box)
        hl.addLayout(stats)

        links = QHBoxLayout()
        links.setSpacing(10)
        for lbl2, url in [
            ("GitHub", "https://github.com/sonuramashishnpm"),
            ("PyPI", "https://pypi.org/project/npmai"),
            ("Website", "https://npmai.netlify.app"),
        ]:
            b2 = QPushButton(lbl2)
            b2.setCursor(Qt.PointingHandCursor)
            b2.setFixedHeight(34)
            b2.setStyleSheet(f"""
                QPushButton {{
                    background:{P['surface']};
                    border:1px solid {P['border2']};
                    border-radius:8px;
                    color:{P['text2']};
                    font-size:12px;
                    padding:0 14px;
                }}
                QPushButton:hover {{
                    background:{P['active_bg']};
                    border-color:{P['accent']};
                    color:{P['active']};
                }}
            """)
            b2.clicked.connect(lambda _, u=url: webbrowser.open(u))
            links.addWidget(b2)
        links.addStretch()
        hl.addLayout(links)
        lay.addWidget(hero)
        lay.addStretch()
        scroll.setWidget(page)
        outer.addWidget(scroll)


class DocsPage(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.setAttribute(Qt.WA_TranslucentBackground); self._build()

    def _sec(self,lay,icon,title,col,items):
        card=GlowCard(accent=col,radius=18,alpha=195)
        cl=QVBoxLayout(card); cl.setContentsMargins(28,22,28,22); cl.setSpacing(14)
        h=QHBoxLayout()
        ic=QLabel(icon); ic.setFont(QFont("Segoe UI",16)); ic.setStyleSheet("background:transparent;"); ic.setFixedWidth(28)
        tt=QLabel(title); tt.setFont(QFont("Segoe UI",13,QFont.Bold))
        tt.setStyleSheet(f"color:{P['text']};background:transparent;")
        h.addWidget(ic); h.addWidget(tt); h.addStretch(); cl.addLayout(h)
        sep=QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{P['border']};border:none;")
        cl.addWidget(sep)
        for it,ib in items:
            row=QHBoxLayout(); row.setSpacing(12)
            dot=QLabel("▸"); dot.setFont(QFont("Segoe UI",11,QFont.Bold))
            dot.setStyleSheet(f"color:{P['primary']};background:transparent;"); dot.setFixedWidth(16); dot.setAlignment(Qt.AlignTop)
            cv=QVBoxLayout(); cv.setSpacing(1)
            it_l=QLabel(it); it_l.setFont(QFont("Segoe UI",11,QFont.Bold))
            it_l.setStyleSheet(f"color:{P['text']};background:transparent;")
            ib_l=QLabel(ib); ib_l.setFont(QFont("Segoe UI",11)); ib_l.setWordWrap(True)
            ib_l.setStyleSheet(f"color:{P['muted']};background:transparent;")
            cv.addWidget(it_l); cv.addWidget(ib_l)
            row.addWidget(dot); row.addLayout(cv); cl.addLayout(row)
        lay.addWidget(card)

    def _build(self):
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        page=QWidget(); page.setAttribute(Qt.WA_TranslucentBackground)
        lay=QVBoxLayout(page); lay.setContentsMargins(36,36,36,36); lay.setSpacing(20)

        t=QLabel("Documentation"); t.setFont(QFont("Segoe UI",22,QFont.Bold))
        t.setStyleSheet(f"color:{P['text']};background:transparent;"); lay.addWidget(t)
        sep=QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{P['border']};border:none;")
        lay.addWidget(sep); lay.addSpacing(4)

        self._sec(lay,"🚀","Getting Started",P["primary"],[
            ("Install","pip install npmai_agents, then run this app."),
            ("First scan","Go to Settings and click 'Scan Now' — agent learns your folder structure."),
            ("Add credentials","Add GitHub/Notion/Stripe/AWS/SMTP creds in Settings. Encrypted locally."),
            ("Type a task","In the Agent tab, describe any task in plain English and press Run. No login needed."),
        ])

        self._sec(lay,"🔗","MCP Architecture — Control your PC from Grok or Claude",P["primary"],[
            ("What is MCP?","NPM-AutoCode-AI hosts its own MCP endpoint. Link it once, paste the link into Claude or Grok connector settings, and the LLM you already talk to becomes the brain — while this app is the hands that execute on your machine."),
            ("01 · Get your link","Click 'Get MCP link' in the sidebar. Log in once — that is the only time you need an account. Everything else in the app stays account-free."),
            ("02 · Paste into connector","Drop the link into Claude (claude.com) or Grok (grok.com) custom connector settings. From then on just talk to your normal LLM chat."),
            ("03 · Ask for anything","'Clear my Downloads folder', 'email my team the report' — the LLM detects it needs a real action and calls into your link automatically."),
            ("04 · Audited before it runs","Every generated script passes an Auditor review plus a separate safety check before it is ever sent to your desktop."),
            ("05 · Runs on your machine","Execution happens locally — your files, your credentials, your machine. The MCP server only relays code and results."),
            ("06 · Verified, not just exit code","A Verifier role checks the actual output against the task — not only whether the script ran without crashing."),
            ("Learn more","Full architecture diagrams and live demo: https://npmcodeai.netlify.app"),
        ])

        self._sec(lay,"🤖","How the Agent Works (Standalone)",P["cyan"],[
            ("Detect intent","Local heuristic decides: conversation, or a task to execute?"),
            ("Plan","Planner LLM breaks the task into atomic steps."),
            ("Select tools","Tool Manager picks from the real 100-tool registry."),
            ("Generate","Coder LLM writes Python for each step."),
            ("Audit","Auditor LLM reviews the code before anything runs."),
            ("Execute","Executor runs it as a real child process — streams to the log panel."),
            ("Verify","Verifier LLM confirms the step actually completed."),
            ("Retry","On failure, agent auto-debugs up to 12 times with prior error context."),
        ])
        self._sec(lay,"🔗","MCP Link (opt-in, login required)",P["violet"],[
            ("Get a link","Sidebar → 'Get MCP Link' → log in (or sign up) → link issued for your account."),
            ("Connect","Paste the link into Claude/Grok's custom connector settings."),
            ("What runs here","Only the execution step — the LLM you connected does the planning/coding, "
                              "already audited before it reaches this app."),
            ("Everything else stays local","Chat, tasks, and credentials never touch this — login is scoped "
                              "to this one feature only."),
        ])
        self._sec(lay,"🗂","Credential Key Reference (for '+ Add Credential Group')",P["sky"],[
            ("github","{ token }"),
            ("gitlab","{ token, url }"),
            ("stripe","{ secret_key }"),
            ("razorpay","{ key_id, key_secret }"),
            ("shopify","{ store, access_token }"),
            ("mailchimp","{ api_key, server_prefix }"),
            ("aws","{ access_key_id, secret_access_key, region }"),
            ("cloudflare","{ token }  or  { api_key, email }"),
            ("vercel","{ token }"),
            ("netlify","{ token }"),
            ("railway","{ token }"),
            ("twilio","{ account_sid, auth_token, from_number, whatsapp_from, verify_service_sid }"),
            ("sendgrid","{ api_key }"),
            ("zoom","{ account_id, client_id, client_secret }"),
            ("smtp / gmail","{ email, password, smtp_host, smtp_port }"),
            ("notion","{ token }"),
            ("linear / asana / clickup / todoist / trello","{ token }  (trello also needs { key } )"),
            ("figma / canva / elevenlabs / stability","{ token }  or  { api_key }"),
            ("googlemaps / openweather / virustotal / shodan / hibp","{ api_key }"),
            ("google_analytics / google_calendar / google","{ ...service account or OAuth JSON... }"),
            ("postgres / mysql / mongodb / redis","{ host, port, user, password, database } (varies)"),
            ("ssh","{ host, user, key_path or password }"),
            ("docker","usually no creds needed for local Docker"),
        ])
        self._sec(lay,"🔒","Security",P["rose"],[
            ("Dual-role audit","Every script is reviewed by a separate Auditor role before execution."),
            ("Subprocess isolation","Code runs as a child process — a broken script cannot crash the app."),
            ("Kill button","Click ■ Kill at any time to terminate the running script immediately."),
            ("Credential encryption","Fernet symmetric encryption, machine-specific key, local only. Never uploaded."),
        ])
        lay.addStretch(); scroll.setWidget(page); outer.addWidget(scroll)


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPM-AutoCode-AI  —  NPMAI Ecosystem  v3.0")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.resize(1220,780); self.setMinimumSize(920,640)
        self._build()

    def _build(self):
        self.bg=CosmicBG(self); self.bg.lower()
        root=QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        self.sidebar=Sidebar(); self.sidebar.page_changed.connect(self._switch)
        root.addWidget(self.sidebar)
        content=QWidget(); content.setAttribute(Qt.WA_TranslucentBackground)
        cl=QVBoxLayout(content); cl.setContentsMargins(0,0,0,0)
        self.stack=QStackedWidget(); self.stack.setAttribute(Qt.WA_TranslucentBackground)
        self.stack.setStyleSheet("background:transparent;")
        self.stack.addWidget(AgentPage())
        self.stack.addWidget(HistoryPage())
        self.stack.addWidget(ToolsPage())
        self.stack.addWidget(SettingsPage())
        self.stack.addWidget(FounderPage())
        self.stack.addWidget(DocsPage())
        cl.addWidget(self.stack); root.addWidget(content)

    def resizeEvent(self,e):
        super().resizeEvent(e); self.bg.setGeometry(0,0,self.width(),self.height())

    def _switch(self,idx):
        if idx==1:
            self.stack.widget(1).load()
        widget=self.stack.widget(idx)
        eff=QGraphicsOpacityEffect(widget); widget.setGraphicsEffect(eff)
        anim=QPropertyAnimation(eff,b"opacity",self)
        anim.setDuration(280); anim.setStartValue(0); anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        self.stack.setCurrentIndex(idx); anim.start()
        self._anim=anim

    def closeEvent(self,e):
        if hasattr(self.sidebar, "_link_mgr") and self.sidebar._link_mgr:
            self.sidebar._link_mgr.stop_listener()
        super().closeEvent(e)


if __name__=="__main__":
    app=QApplication(sys.argv); app.setStyle("Fusion")
    pal=QPalette()
    pal.setColor(QPalette.Window,           QColor(P["bg"]))
    pal.setColor(QPalette.WindowText,       QColor(P["text"]))
    pal.setColor(QPalette.Base,             QColor(P["surface"]))
    pal.setColor(QPalette.AlternateBase,    QColor(P["surface2"]))
    pal.setColor(QPalette.Text,             QColor(P["text"]))
    pal.setColor(QPalette.Button,           QColor(P["surface"]))
    pal.setColor(QPalette.ButtonText,       QColor(P["text"]))
    pal.setColor(QPalette.Highlight,        QColor(P["primary"]))
    pal.setColor(QPalette.HighlightedText,  QColor("#FFFFFF"))
    app.setPalette(pal)
    win=AppWindow(); win.show(); sys.exit(app.exec())
