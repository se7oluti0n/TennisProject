// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtCore
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Controls.Material 2.15
import CourtSetupView
import "."

// import PlotView

Window {
    id: window
    width: settings.windowWidth
    height: settings.windowHeight
    visible: true
    title: "Pickleball Tracker"

    Material.theme: Material.Dark
    Material.primary: "#6200EE"       // Primary color
    Material.accent: "#03DAC6"        // Accent color
    Material.foreground: "#FFFFFF"    // Foreground color (e.g., text)
    Material.background: "#121212"    // Background color

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

        CourtSetupView {
            id: courtView
            implicitWidth: window.width
            implicitHeight: window.height - 400

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                onClicked: function (mouse) {
                    if (mouse.button === Qt.RightButton) {
                        // console.log("Right-click detected at", mouse.x, mouse.y);
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

        BallChart {
            id: ball_chart
            implicitWidth: window.width
            implicitHeight: 300

            onBounceClicked: function (frame_id) {
                console.log("replay at frame " + frame_id);
                chart_controller.handleReplayAtFrame(frame_id)
            }

            MouseArea {
                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                    bottom: parent.verticalCenter
                }
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                onClicked: function (mouse) {
                    if (mouse.button === Qt.RightButton) {
                        // console.log("Right-click detected at", mouse.x, mouse.y);
                        console.log("Reset zoom");
                    }
                }

                onPressed: function (mouse) {
                    if (mouse.button === Qt.LeftButton) {
                        chart_controller.handleLeftMousePressed(mouse.x);
                    }
                }

                onReleased: function (mouse) {
                    chart_controller.handleLeftMouseReleased();
                }

                onPositionChanged: function (mouse) {
                    chart_controller.handleMouseMove(mouse.x);
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
            Button {
                text: "Save Homography"
                onClicked: {
                    courtView.saveHomography();
                }
            }
            Button {
                text: "Load Homography"
                onClicked: {
                    courtView.loadHomography();
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
                    video_controller.read_video(video_path.text);
                }

                enabled: video_path.text !== ""
            }

            Button {
                id: prevButton
                text: "Prev"
                onClicked: {
                    video_controller.get_prev_frame();
                }
                // enabled: false
            }

            Button {
                id: nextButton
                text: "Next"
                onClicked: {
                    video_controller.get_next_frame();
                }

                // enabled: false
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

            Button {
                id: playBtn
                text: "Play"
                onClicked: {
                    if (playBtn.text === "Pause") {
                        video_controller.pause();
                    } else {
                        video_controller.play();
                    }
                }
            }
        }
    }

    FileDialog {
        id: fileDialog
        currentFolder: StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
        onAccepted: video_path.text = selectedFile
    }

    Connections {
        target: video_controller

        function onPrevAvailable(val) {
        // console.log("Prev Available: " + val);
        // prevButton.enabled = val;
        }

        function onNextAvailable(val) {
        // nextButton.enabled = val;
        }

        function onGotImage(frame_id, image) {
            courtView.setImage(frame_id, image);
        }

        function onBallDetected(frame_id, x, y) {
            courtView.handleBallDetected(frame_id, x, y);
        }

        function onBouncesDetected(bounces) {
            courtView.handleBounceDetected(bounces);
        }

        function onXPlotReady(plot_img) {
        // xPlotView.setPlot(plot_img);
        }

        function onYPlotReady(plot_img) {
        // yPlotView.setPlot(plot_img);
        }

        function onPlayingStatusChanged(isPlaying) {
            playBtn.text = isPlaying ? "Pause" : "Play";
        }
    }

    Connections {
        target: chart_controller

        function onXBallTrajectoryUpdated(pointx, pointy) {
            // console.log("update x line");
            ball_chart.xLine.append(pointx, pointy);
        }

        function onYBallTrajectoryUpdated(pointx, pointy) {
            ball_chart.yLine.append(pointx, pointy);
        }

        function onBounceUpdated(x, y) {
            ball_chart.scatter.append(x, y);
        }

        function onAxisXUpdated(max_val) {
            ball_chart.xAxis.max = max_val;
            ball_chart.xAxis.min = max_val - 100;
        }

        function onAxisYUpdated(max_val) {
            ball_chart.yAxis.max = max_val;
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
        video_controller.stop();
    }
}
