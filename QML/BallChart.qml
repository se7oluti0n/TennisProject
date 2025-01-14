import QtCharts
import QtQuick

Item {
    property alias xLine: xBallTrajectory_
    property alias yLine: yBallTrajectory_
    property alias xScatter: xScatter_
    property alias yScatter: yScatter_
    property alias xAxis: xAxis_
    property alias yAxis: yAxis_

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

        // axes: [xAxis, yAxis]


        ScatterSeries {
            id: yScatter_
            name: "Bounce Y"
            color: "blue"
            axisX: xAxis_
            axisY: yAxis_
        }

        ScatterSeries {
            id: xScatter_
            name: "Bounce X"
            color: "blue"
            axisX: xAxis_
            axisY: yAxis_
        }

        LineSeries {
            id: xBallTrajectory_
            name: "y traj"
            color: "red"
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
