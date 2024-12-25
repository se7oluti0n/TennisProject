import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 600
    height: 500
    title: "HelloApp"

    Canvas {
      property bool moving: false
      anchors.centerIn: parent
      id: mycanvas
      width: 100
      height: 200
      property int cx: width / 2 
      property int cy: height / 2
      onPaint: {
          var ctx = getContext("2d");
          ctx.fillStyle = Qt.rgba(1, 0, 0, 1);
          ctx.fillRect(0, 0, width, height);

          ctx.beginPath();
          ctx.arc(cx, cy, 5, 0, 2 * Math.PI, true);
          ctx.fillStyle = Qt.rgba(0, 1, 0, 1);
          ctx.fill();
      }

      MouseArea {
          anchors.fill: parent
          property int lastX: 0
          property int lastY: 0
          onPressed: {
              mytext.text = "onPressed: " + mouse.x + " " + mouse.y;
              if (! mycanvas.moving && Math.abs(mouse.x - mycanvas.cx) < 5 && Math.abs(mouse.y - mycanvas.cy) < 5) {
                  mycanvas.moving = true;
                  lastX = mouse.x;
                  lastY = mouse.y;
                  
                  my2ndtext.text = "set lastx, last y : " + lastX + " " + lastY;
              } 
          }

          onReleased: {
              mycanvas.moving = false;
          }

          onPositionChanged: {
              if (mycanvas.moving) {
                  mycanvas.cx = mouse.x ;
                  mycanvas.cy = mouse.y ;
                  mycanvas.requestPaint();
              }
          }


      }
    }
}
