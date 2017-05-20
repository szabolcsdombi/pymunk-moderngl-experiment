from PyQt5 import QtOpenGL, QtWidgets, QtCore
import GLWindow

from app import App


wnd = GLWindow.create_window()
app = App()

while wnd.update():
    if wnd.key_pressed(' '):
        app.shoot()

    app.render(wnd.viewport, wnd.time)
