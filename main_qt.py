from PyQt5 import QtOpenGL, QtWidgets, QtCore

from app import App


class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        fmt.setSwapInterval(1)

        super(QGLControllerWidget, self).__init__(fmt, None)

        self.app = None
        self.timer = QtCore.QElapsedTimer()
        self.timer.start()
    
    def keyPressEvent(self, evt):
        self.app.shoot()

    def initializeGL(self):
        self.app = App()

    def paintGL(self):
        if self.app is not None:
            self.app.render((0, 0, self.width(), self.height()), self.timer.elapsed() / 1000)
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = QGLControllerWidget()
    screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
    window.move((screen.width() - 1280) // 2, (screen.height() - 720) // 2)
    window.resize(1280, 720)
    window.show()
    app.exec_()
