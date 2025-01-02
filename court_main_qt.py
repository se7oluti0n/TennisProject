# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import sys

from PySide6.QtQml import qmlRegisterType, QQmlDebuggingEnabler

import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

import CourtSetupView
import CourtVideo
import PlotView
import rc_style

if __name__ == "__main__":

    argument_parser = ArgumentParser(description="Scene Graph Painted Item Example",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("-qmljsdebugger", action="store",
                                 help="Enable QML debugging")
    options = argument_parser.parse_args()
    if options.qmljsdebugger:
        QQmlDebuggingEnabler.enableDebugging(True)

    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Material")
    app.setOrganizationName("Manhattan")
    app.setOrganizationDomain("manhattan.vn")
    app.setApplicationName("CourtView")

    #qmlRegisterType(CourtSetupView, "CourtSetupView", 1, 0, "CourtSetupView")
    #qmlRegisterType(CourtVideo, "CourtVideo", 1, 0, "CourtVideo")

    engine = QQmlApplicationEngine()

    engine.addImportPath(sys.path[0])
    engine.loadFromModule("QML", "CourtViewMain")
    if not engine.rootObjects():
        sys.exit(-1)
    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
