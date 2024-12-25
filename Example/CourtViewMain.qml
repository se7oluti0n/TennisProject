// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtCore
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import CourtSetupView
import CourtVideo

Window {
    width: 600
    height: 400
    visible: true
    title: "Hello World"

    ColumnLayout {
        spacing: 10
        Layout.fillWidth: true
        Layout.fillHeight: true

        CourtSetupView {
          id: courtView
          width: 600 
          height: 300 
        }

        RowLayout {
            spacing: 10
            width: parent.width
            height: 50

            Text {
              id: video_path
              text: "Hello World"
            }

            Button {
                text: "Browse"
                onClicked: {
                   fileDialog.open() 
                }
            }
        }

        RowLayout {
            spacing: 10
            width: parent.width
            height: 50

            Button {
                id: loadButton
                text: "Load Video"
                onClicked: {
                  courtVideo.read_video(video_path.text)
                }

                enabled: video_path.text !== ""
            }

            Button {
                id: prevButton
                text: "Prev"
                onClicked: {
                  courtVideo.get_prev_frame()
                }
                enabled: courtVideo.checkPrev
            }

            Button {
                id: nextButton
                text: "Next"
                onClicked: {
                  courtVideo.get_next_frame()
                }

                enabled: courtVideo.checkNext
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

      onPrevAvailable: function(val) {
        prevButton.visible = val 
      }

      onNextAvailable: function(val) {
        nextButton.visible = val
      }

      onGotImage: function(image) {
        courtView.setImage(image)
      }

    }

}
