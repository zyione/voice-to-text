import tkinter as tk
import threading
import queue
import math
import ctypes
import ctypes.wintypes as wintypes
from PIL import Image, ImageDraw

# ─── Windows DPI awareness ──────────────────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ─── Win32 constants ─────────────────────────────────────────────
WS_EX_LAYERED    = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST    = 0x00000008
WS_EX_TRANSPARENT= 0x00000020
WS_POPUP         = 0x80000000
ULW_ALPHA        = 0x02
AC_SRC_OVER      = 0x00
AC_SRC_ALPHA     = 0x01
SW_SHOW          = 5
SW_HIDE          = 0
SM_CXSCREEN      = 0
SM_CYSCREEN      = 1
CS_HREDRAW       = 0x0002
CS_VREDRAW       = 0x0001
IDC_ARROW        = 32512
WM_CLOSE         = 0x0010
WM_DESTROY       = 0x0002

user32 = ctypes.windll.user32
gdi32  = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# ─── ctypes structures ───────────────────────────────────────────
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class SIZE(ctypes.Structure):
    _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ("BlendOp",             ctypes.c_byte),
        ("BlendFlags",          ctypes.c_byte),
        ("SourceConstantAlpha", ctypes.c_byte),
        ("AlphaFormat",         ctypes.c_byte),
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize",          ctypes.c_uint32),
        ("biWidth",         ctypes.c_int32),
        ("biHeight",        ctypes.c_int32),
        ("biPlanes",        ctypes.c_uint16),
        ("biBitCount",      ctypes.c_uint16),
        ("biCompression",   ctypes.c_uint32),
        ("biSizeImage",     ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed",       ctypes.c_uint32),
        ("biClrImportant",  ctypes.c_uint32),
    ]

# WNDCLASSEXW – not in ctypes.wintypes, so we define it manually
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, ctypes.c_uint,
                              wintypes.WPARAM, wintypes.LPARAM)

# HICON, HCURSOR, HBRUSH, HINSTANCE are all just HANDLE under the hood
_H = wintypes.HANDLE

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize",        ctypes.c_uint),
        ("style",         ctypes.c_uint),
        ("lpfnWndProc",   WNDPROC),
        ("cbClsExtra",    ctypes.c_int),
        ("cbWndExtra",    ctypes.c_int),
        ("hInstance",     _H),
        ("hIcon",         _H),
        ("hCursor",       _H),
        ("hbrBackground", _H),
        ("lpszMenuName",  wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm",       _H),
    ]

# ─── Strict function signatures for 64-bit safety ───────────────
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype  = _H

user32.LoadCursorW.argtypes = [_H, wintypes.LPCWSTR]
user32.LoadCursorW.restype  = _H

user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
user32.RegisterClassExW.restype  = wintypes.ATOM

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HANDLE, _H, wintypes.LPVOID,
]
user32.CreateWindowExW.restype = wintypes.HWND

user32.DefWindowProcW.argtypes = [wintypes.HWND, ctypes.c_uint,
                                   wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype  = ctypes.c_long

user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype  = wintypes.BOOL

user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype  = wintypes.BOOL

user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype  = ctypes.c_int

user32.UpdateLayeredWindow.argtypes = [
    wintypes.HWND, wintypes.HDC, ctypes.POINTER(POINT), ctypes.POINTER(SIZE),
    wintypes.HDC, ctypes.POINTER(POINT), wintypes.COLORREF,
    ctypes.POINTER(BLENDFUNCTION), wintypes.DWORD,
]
user32.UpdateLayeredWindow.restype = wintypes.BOOL

user32.GetDC.argtypes  = [wintypes.HWND]
user32.GetDC.restype   = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ReleaseDC.restype  = ctypes.c_int

gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype  = wintypes.HDC
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.DeleteDC.restype  = wintypes.BOOL
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype  = wintypes.HGDIOBJ
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteObject.restype  = wintypes.BOOL
gdi32.CreateDIBSection.argtypes = [
    wintypes.HDC, ctypes.c_void_p, wintypes.UINT,
    ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.DWORD,
]
gdi32.CreateDIBSection.restype = wintypes.HBITMAP


# ═════════════════════════════════════════════════════════════════
class OverlayUI:
    """Floating pill overlay — pure Win32 layered window (no Tkinter rendering)."""

    def __init__(self):
        self.q = queue.Queue()
        self.is_visible = False
        self._hwnd = None

        # Physics
        self._current_volume = 0.0
        self._target_volume  = 0.0
        self._velocity       = 0.0

        # Design
        self.WIDTH         = 160
        self.HEIGHT        = 50
        self.BG_COLOR      = (24, 24, 26)
        self.BORDER_COLOR  = (42, 42, 44)
        self.BAR_ON_COLOR  = (204, 255, 51)
        self.BAR_OFF_COLOR = (48, 56, 36)
        self.BAR_COUNT     = 9
        self.BAR_WIDTH     = 10
        self.BAR_SPACING   = 5
        self.MAX_BAR_HEIGHT= int(self.HEIGHT * 0.65)

        self.PAD   = 8
        self.win_w = self.WIDTH  + self.PAD * 2
        self.win_h = self.HEIGHT + self.PAD * 2

        self._wnd_proc_ref = None  # prevent GC of the callback

        self.thread = threading.Thread(target=self._run_ui, daemon=True)
        self.thread.start()

    # ─── UI thread ───────────────────────────────────────────────
    def _run_ui(self):
        # Hidden Tkinter root — used ONLY for its after() timer, never drawn
        self.root = tk.Tk()
        self.root.withdraw()

        self._create_overlay_window()
        self._process_queue()
        self.root.mainloop()

    def _create_overlay_window(self):
        """Register a window class and create a pure WS_EX_LAYERED popup."""
        hinstance = kernel32.GetModuleHandleW(None)

        def _wnd_proc(hwnd, msg, wp, lp):
            if msg == WM_DESTROY:
                return 0
            return user32.DefWindowProcW(hwnd, msg, wp, lp)

        self._wnd_proc_ref = WNDPROC(_wnd_proc)

        cls_name = "VTOverlay"
        wc = WNDCLASSEXW()
        wc.cbSize       = ctypes.sizeof(WNDCLASSEXW)
        wc.style         = CS_HREDRAW | CS_VREDRAW
        wc.lpfnWndProc   = self._wnd_proc_ref
        wc.hInstance     = hinstance
        wc.hCursor       = user32.LoadCursorW(None, ctypes.cast(IDC_ARROW, wintypes.LPCWSTR))
        wc.lpszClassName = cls_name
        user32.RegisterClassExW(ctypes.byref(wc))

        scr_w = user32.GetSystemMetrics(SM_CXSCREEN)
        scr_h = user32.GetSystemMetrics(SM_CYSCREEN)
        x = (scr_w // 2) - (self.win_w // 2)
        y = scr_h - self.win_h - 120

        ex = WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_TRANSPARENT

        self._hwnd = user32.CreateWindowExW(
            ex, cls_name, "VTOverlay", WS_POPUP,
            x, y, self.win_w, self.win_h,
            None, None, hinstance, None,
        )

    # ─── UpdateLayeredWindow helper ──────────────────────────────
    def _update_layered(self, pil_rgba):
        if not self._hwnd:
            return
        w, h = pil_rgba.size

        # Pre-multiply alpha (required by UpdateLayeredWindow)
        # Compositing RGBA over solid-black RGBA mathematically pre-multiplies RGB
        black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        premul = Image.composite(pil_rgba, black, pil_rgba.split()[3])
        pr, pg, pb, _ = premul.split()
        # Original alpha channel
        _, _, _, pa = pil_rgba.split()
        # Merge as BGRA
        bgra = Image.merge("RGBA", (pb, pg, pr, pa))
        bits = bgra.tobytes()

        hdc_scr = user32.GetDC(None)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_scr)

        bmi = BITMAPINFOHEADER()
        bmi.biSize        = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth       = w
        bmi.biHeight      = -h  # top-down
        bmi.biPlanes      = 1
        bmi.biBitCount    = 32
        bmi.biCompression = 0

        ppv = ctypes.c_void_p()
        hbm = gdi32.CreateDIBSection(
            hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(ppv), None, 0,
        )
        old = gdi32.SelectObject(hdc_mem, hbm)
        ctypes.memmove(ppv, bits, len(bits))

        pt_src = POINT(0, 0)
        sz     = SIZE(w, h)
        blend  = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)

        user32.UpdateLayeredWindow(
            self._hwnd, hdc_scr, None, ctypes.byref(sz),
            hdc_mem, ctypes.byref(pt_src), 0,
            ctypes.byref(blend), ULW_ALPHA,
        )

        gdi32.SelectObject(hdc_mem, old)
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(None, hdc_scr)

    # ─── Queue ───────────────────────────────────────────────────
    def _process_queue(self):
        while not self.q.empty():
            try:
                msg = self.q.get_nowait()
                cmd = msg.get("cmd")
                if cmd == "show":
                    self.is_visible = True
                    self._current_volume = 0.0
                    self._target_volume  = 0.0
                    self._velocity       = 0.0
                    # Draw one frame BEFORE showing, so there's no white flash
                    self._draw_frame(0.02)
                    user32.ShowWindow(self._hwnd, SW_SHOW)
                elif cmd == "hide":
                    user32.ShowWindow(self._hwnd, SW_HIDE)
                    self.is_visible = False
                elif cmd == "update" and self.is_visible:
                    self._target_volume = min(1.0, msg.get("val", 0) * 12.0)
                elif cmd == "quit":
                    if self._hwnd:
                        user32.DestroyWindow(self._hwnd)
                    self.root.quit()
                    return
            except queue.Empty:
                break

        if self.is_visible:
            self._animate()

        if self.root:
            self.root.after(16, self._process_queue)

    # ─── Animation ───────────────────────────────────────────────
    def _animate(self):
        if self._target_volume > self._current_volume:
            self._current_volume += (self._target_volume - self._current_volume) * 0.4
            self._velocity = 0
        else:
            self._velocity -= 0.005
            self._current_volume += self._velocity
            self._current_volume += (self._target_volume - self._current_volume) * 0.1

        self._current_volume = max(0.01, min(1.0, self._current_volume))
        self._draw_frame(max(0.02, self._current_volume))

    def _draw_frame(self, vol):
        ss = 2
        sw, sh = self.win_w * ss, self.win_h * ss

        img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = sw // 2, sh // 2

        # Pill
        w, h = self.WIDTH * ss, self.HEIGHT * ss
        x1, y1 = cx - w // 2, cy - h // 2
        x2, y2 = cx + w // 2, cy + h // 2
        r = h // 2
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r,
                               fill=(*self.BG_COLOR, 255),
                               outline=(*self.BORDER_COLOR, 255), width=ss)

        # Bars
        bw, bs = self.BAR_WIDTH * ss, self.BAR_SPACING * ss
        max_bh = self.MAX_BAR_HEIGHT * ss
        total = self.BAR_COUNT * bw + (self.BAR_COUNT - 1) * bs
        sx = cx - total // 2 + bw // 2
        mid = self.BAR_COUNT // 2

        for i in range(self.BAR_COUNT):
            bx = sx + i * (bw + bs)
            d = abs(i - mid)
            bh = int(max_bh * math.exp(-d * d / 8.0) * vol)
            bh = max(bw, bh)
            col = self.BAR_ON_COLOR if bh > bw else self.BAR_OFF_COLOR
            draw.rounded_rectangle(
                [bx - bw // 2, cy - bh // 2, bx + bw // 2, cy + bh // 2],
                radius=bw // 2, fill=(*col, 255),
            )

        img = img.resize((self.win_w, self.win_h), Image.Resampling.LANCZOS)
        self._update_layered(img)

    # ─── Public API ──────────────────────────────────────────────
    def show(self):
        self.q.put({"cmd": "show"})

    def hide(self):
        self.q.put({"cmd": "hide"})

    def update_volume(self, rms):
        self.q.put({"cmd": "update", "val": rms})

    def destroy(self):
        self.q.put({"cmd": "quit"})
