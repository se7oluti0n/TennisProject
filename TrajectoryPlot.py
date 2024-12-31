import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QImage


def matplotlib_figure_to_qimage(y_data, label="", title="", figsize=(5, 4), dpi=100):
    # Step 1: Create a Matplotlib figure
    fig = Figure(figsize=figsize, dpi=dpi)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    x_data = np.asarray(range(len(y_data)))
    ax.plot(x_data, y_data, label=label)
    ax.set_title(title)
    ax.legend()
    ax.grid()

    # Step 2: Render the figure to a NumPy array
    canvas.draw()
    buf = canvas.buffer_rgba()
    width, height = fig.get_size_inches() * fig.get_dpi()
    width, height = int(width), int(height)
    image_array = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))

    # Step 3: Convert the NumPy array to a QImage
    qimage = QImage(
        image_array.data,
        width,
        height,
        QImage.Format.Format_RGBA8888,
    ).copy()  # Use .copy() to ensure buffer memory stays valid

    return qimage
