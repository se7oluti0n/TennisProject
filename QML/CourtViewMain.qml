// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtCore
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Controls.Material
import CourtSetupView
import CourtVideo
import PlotView

Window {
    id: window
    width: settings.windowWidth
    height: settings.windowHeight
    visible: true
    title: "Hello World"
    Material.theme: Material.Dark
    Material.accent: Material.Red

    onWidthChanged: {
        settings.windowWidth = window.width;
        courtView.handleResize();
    }

    onHeightChanged: {
        settings.windowHeight = window.height;
        courtView.handleResize();
    }

    ColumnLayout {
        spacing: 10
        //Layout.preferredWidth : parent.width
        //Layout.preferredHeight: parent.height
        Layout.fillWidth: true
        Layout.fillHeight: true

        RowLayout {
            spacing: 10
            Layout.fillWidth: true

            CourtSetupView {
                id: courtView
                implicitWidth: (window.width - 10) * 0.7
                implicitHeight: window.height - 100

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    onClicked: function (mouse) {
                        if (mouse.button === Qt.RightButton) {
                            console.log("Right-click detected at", mouse.x, mouse.y);
                            courtView.handleRightClicked(mouse.x, mouse.y);
                        }
                    }

                    onPressed: function (mouse) {
                        if (mouse.button === Qt.LeftButton) {
                            courtView.handleMousePressed(mouse.x, mouse.y);
                        }
                    }

                    onReleased: function (mouse) {
                        courtView.handleMouseReleased(mouse.x, mouse.y);
                    }

                    onPositionChanged: function (mouse) {
                        courtView.handleMouseMoved(mouse.x, mouse.y);
                    }
                }
            }

            ColumnLayout {
                Layout.preferredWidth: (window.width - 10) * 0.3
                Layout.preferredHeight: window.height - 100

                spacing: 10
                PlotView {
                    id: xPlotView
                    implicitWidth: parent.width 
                    implicitHeight: (parent.height - 10) / 2
                }
                PlotView {
                    id: yPlotView
                    implicitWidth: parent.width 
                    implicitHeight: (parent.height - 10) / 2
                }
            }
        }

        RowLayout {
            spacing: 10
            Layout.fillWidth: true
            Layout.preferredHeight: 40

            Text {
                id: video_path
                text: settings.videoPath
                onTextChanged: {
                    settings.videoPath = video_path.text;
                }
            }

            Button {
                text: "Browse"
                onClicked: {
                    fileDialog.open();
                }
            }
        }

        RowLayout {
            spacing: 10
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            Layout.bottomMargin: 5

            Button {
                id: loadButton
                text: "Load Video"
                onClicked: {
                    courtVideo.read_video(video_path.text);
                }

                enabled: video_path.text !== ""
            }

            Button {
                id: prevButton
                text: "Prev"
                onClicked: {
                    courtVideo.get_prev_frame();
                }
                enabled: courtVideo.checkPrev
            }

            Button {
                id: nextButton
                text: "Next"
                onClicked: {
                    courtVideo.get_next_frame();
                }

                enabled: courtVideo.checkNext
            }

            Button {
                text: "Realign Court"
                onClicked: {
                    courtView.update_homography();
                }
            }

            Button {
                text: "Process frame"
                onClicked: {
                    pickle_vision.process_frame();
                }
            }
        }
    }

    FileDialog {
        id: fileDialog
        currentFolder: StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
        onAccepted: video_path.text = selectedFile
    }

    CourtVideo {
        id: courtVideo

        onPrevAvailable: function (val) {
            console.log("Prev Available: " + val);
            prevButton.enabled = val;
        }

        onNextAvailable: function (val) {
            nextButton.enabled = val;
        }

        onGotImage: function (frame_id, image) {
            courtView.setImage(frame_id, image);
        }

        onBallDetected: function (frame_id, x, y) {
            courtView.handleBallDetected(frame_id, x, y);
        }

        onXPlotReady: function (plot_img) {
            xPlotView.setPlot(plot_img);
        }

        onYPlotReady: function (plot_img) {
            yPlotView.setPlot(plot_img);
        }
    }

    Settings {
        id: settings
        property string videoPath: "No Video Selected"
        property int windowWidth: 640
        property int windowHeight: 400
    }

    Component.onDestruction: {
        settings.videoPath = video_path.text;
    }
}
