import QtCharts
import QtQuick

Item {
    property alias xLine: xBallTrajectory_
    property alias yLine: yBallTrajectory_
    property alias scatter: scatter_
    property alias cursor: cursor_
    property alias xAxis: xAxis_
    property alias yAxis: yAxis_

    signal bounceClicked(int xAxis)

    ChartView {
        anchors.fill: parent
        title: "Ball Trajectory"
        legend.visible: true

        ValueAxis {
            id: xAxis_
            min: 0
            max: 100 // Set the maximum x value
        }

        ValueAxis {
            id: yAxis_
            min: 0
            max: 2000 // Set the maximum y value
        }

        ScatterSeries {
            id: cursor_
            name: "current frame"
            color: "red"
            axisX: xAxis_
            axisY: yAxis_
            markerShape: ScatterSeries.MarkerShapeRectangle

            XYPoint {
              x: 0
              y: 0
            }

        }

        ScatterSeries {
            id: scatter_
            name: "bounce"
            color: "cyan"
            axisX: xAxis_
            axisY: yAxis_

            onClicked: function (point) {
              console.log("clicked: ", point);
              bounceClicked(point.x);
            }
        }

        LineSeries {
            id: xBallTrajectory_
            name: "y traj"
            color: "blue"
            axisX: xAxis_
            axisY: yAxis_
        }

        LineSeries {
            id: yBallTrajectory_
            name: "x traj"
            color: "green"
            axisX: xAxis_
            axisY: yAxis_
        }
    }
}
