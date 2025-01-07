# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from PySide6.QtQml import qmlRegisterType, QQmlDebuggingEnabler

import sys
sys.path.append('./qml_components')
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

import CourtSetupView
from CourtVideo import VideoController
import PlotView
import os

if __name__ == "__main__":
    argument_parser = ArgumentParser(description="Scene Graph Painted Item Example",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("-qmljsdebugger", action="store",
                                 help="Enable QML debugging")
    options = argument_parser.parse_args()
    if options.qmljsdebugger:
        QQmlDebuggingEnabler.enableDebugging(True)

    video_controller = VideoController()

    app = QGuiApplication(sys.argv)

    QQuickStyle.setStyle("Material")
    app.setOrganizationName("Manhattan")
    app.setOrganizationDomain("manhattan.vn")
    app.setApplicationName("CourtView")

    engine = QQmlApplicationEngine()

    engine.rootContext().setContextProperty("video_controller", video_controller)
    engine.addImportPath(sys.path[0])
    engine.loadFromModule("QML", "CourtViewMain")
    if not engine.rootObjects():
        sys.exit(-1)
    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
