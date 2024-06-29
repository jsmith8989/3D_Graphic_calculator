import sys
import io
import warnings
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QFrame,
    QListWidget,
    QComboBox,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import QColor, QLinearGradient, QPalette, QBrush
from PyQt5.QtCore import Qt
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#1E1E1E")
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor("#1E1E1E")
        super(MplCanvas, self).__init__(self.fig)

        # Set up the axes
        self.axes.tick_params(colors="white")
        for spine in self.axes.spines.values():
            spine.set_color("white")
        self.axes.axhline(y=0, color="white", linewidth=1)
        self.axes.axvline(x=0, color="white", linewidth=1)

    def set_3d(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111, projection="3d")
        self.axes.set_facecolor("#1E1E1E")
        self.axes.tick_params(colors="white")
        self.axes.xaxis.pane.fill = False
        self.axes.yaxis.pane.fill = False
        self.axes.zaxis.pane.fill = False
        self.axes.xaxis.pane.set_edgecolor("w")
        self.axes.yaxis.pane.set_edgecolor("w")
        self.axes.zaxis.pane.set_edgecolor("w")
        self.axes.grid(True, color="white", linestyle="--", linewidth=0.5, alpha=0.3)

    def set_2d(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor("#1E1E1E")
        self.axes.tick_params(colors="white")
        for spine in self.axes.spines.values():
            spine.set_color("white")
        self.axes.axhline(y=0, color="white", linewidth=1)
        self.axes.axvline(x=0, color="white", linewidth=1)
        self.axes.grid(True, color="white", linestyle="--", linewidth=0.5, alpha=0.3)


class ScientificCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scientific Calculator")
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet("background-color: #2E2E2E;")

        # Set dark gray title bar
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#2E2E2E"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        plot_frame = QFrame()
        plot_frame.setStyleSheet("background-color: #1E1E1E;")
        plot_layout = QVBoxLayout(plot_frame)

        self.equation_label = QLabel("")
        self.equation_label.setStyleSheet(
            """
            color: white; 
            font-size: 12pt;
            qproperty-alignment: AlignCenter;
            background-color: #1E1E1E;
            padding: 5px;
        """
        )
        plot_layout.addWidget(self.equation_label)

        self.canvas = MplCanvas(self, width=10, height=6, dpi=100)
        plot_layout.addWidget(self.canvas)

        zoom_layout = QHBoxLayout()
        zoom_out_button = self.create_metallic_button("Zoom -")
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_button)
        zoom_in_button = self.create_metallic_button("Zoom +")
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_button)
        plot_layout.addLayout(zoom_layout)

        main_layout.addWidget(plot_frame, 2)

        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #2E2E2E;")
        input_layout = QVBoxLayout(input_frame)

        self.equation_entry = QLineEdit()
        self.equation_entry.setStyleSheet(
            """
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #909090, stop:1 #808080);
                color: #FFFFFF;
                font: bold 10pt 'Arial';
                border: 1px solid #999999;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #E0E0E0;
                selection-color: #333333;
            }
        """
        )
        self.equation_entry.returnPressed.connect(self.plot_graph)
        input_layout.addWidget(self.equation_entry)

        plot_button = self.create_metallic_button("Plot Graph")
        plot_button.clicked.connect(self.plot_graph)
        input_layout.addWidget(plot_button)

        calc_layout = QHBoxLayout()
        functions = ["sin", "cos", "tan", "log", "exp"]
        for func in functions:
            button = self.create_metallic_button(func)
            button.clicked.connect(lambda _, f=func: self.add_function(f))
            calc_layout.addWidget(button)
        input_layout.addLayout(calc_layout)

        self.add_style_options(input_layout)

        self.history_listbox = QListWidget()
        self.history_listbox.setStyleSheet(
            """
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #909090, stop:1 #808080);
                color: #FFFFFF;
                font: 9pt 'Arial';
                border: 1px solid #999999;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background: #E0E0E0;
                color: #333333;
            }
            QListWidget::item:hover {
                background: #A0A0A0;
            }
        """
        )
        input_layout.addWidget(self.history_listbox)

        main_layout.addWidget(input_frame, 1)

        self.x_range = (-10, 10)
        self.x = np.linspace(*self.x_range, 400)

    def create_metallic_button(self, text):
        button = QPushButton(text)
        button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #909090, stop:1 #808080);
                color: #FFFFFF;
                font: bold 9pt 'Arial';
                border: 1px solid #999999;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #E8E8E8, stop:1 #E0E0E0);
                color: #333333;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #B8B8B8, stop:1 #B0B0B0);
                color: #FFFFFF;
                padding: 6px 4px 4px 6px;
            }
        """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        button.setGraphicsEffect(shadow)
        return button

    def add_function(self, func):
        current = self.equation_entry.text()
        self.equation_entry.setText(current + func + "(")
        self.equation_entry.setFocus()

    def add_style_options(self, layout):
        style_layout = QHBoxLayout()
        self.color_var = QComboBox()
        self.color_var.addItems(["cyan", "red", "green", "blue", "yellow"])
        style_layout.addWidget(QLabel("Color:"))
        style_layout.addWidget(self.color_var)
        self.style_var = QComboBox()
        self.style_var.addItems(["-", "--", "-.", ":"])
        style_layout.addWidget(QLabel("Style:"))
        style_layout.addWidget(self.style_var)
        layout.addLayout(style_layout)

    def plot_graph(self, update_history=True):
        equation_str = self.equation_entry.text()
        self.equation_label.setText(equation_str)

        equations = equation_str.split(";")
        is_3d = any("z" in eq for eq in equations)

        if is_3d:
            self.canvas.set_3d()
        else:
            self.canvas.set_2d()

        self.canvas.axes.clear()
        self.canvas.axes.set_facecolor("#1E1E1E")

        for eq in equations:
            try:
                original_eq = eq
                if "=" in eq:
                    left, right = eq.split("=")
                    eq = f"({left}) - ({right})"

                if is_3d:
                    # Check if it's a sphere equation
                    if (
                        "x**2" in original_eq
                        and "y**2" in original_eq
                        and "z**2" in original_eq
                    ):
                        # Extract the radius
                        radius_squared = float(original_eq.split("=")[1].strip())
                        radius = np.sqrt(radius_squared)

                        # Create a sphere
                        u = np.linspace(0, 2 * np.pi, 100)
                        v = np.linspace(0, np.pi, 100)
                        x = radius * np.outer(np.cos(u), np.sin(v))
                        y = radius * np.outer(np.sin(u), np.sin(v))
                        z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

                        # Plot the sphere
                        self.canvas.axes.plot_surface(
                            x, y, z, color=self.color_var.currentText(), alpha=0.7
                        )
                    else:
                        # For other 3D equations
                        x = y = np.linspace(self.x_range[0], self.x_range[1], 50)
                        X, Y = np.meshgrid(x, y)

                        def equation(X, Y, Z):
                            return eval(
                                eq,
                                {
                                    "x": X,
                                    "y": Y,
                                    "z": Z,
                                    "np": np,
                                    "sin": np.sin,
                                    "cos": np.cos,
                                    "tan": np.tan,
                                    "log": np.log,
                                    "exp": np.exp,
                                    "sqrt": np.sqrt,
                                    "pi": np.pi,
                                    "e": np.e,
                                },
                            )

                        Z = np.linspace(self.x_range[0], self.x_range[1], 50)
                        Z = Z[:, np.newaxis, np.newaxis]
                        values = equation(X, Y, Z)

                        # Find the zero-crossing
                        zero_crossing = np.where(np.diff(np.sign(values), axis=0))[0]
                        if len(zero_crossing) > 0:
                            idx = zero_crossing[0]
                            Z_surface = Z[idx] + (Z[idx + 1] - Z[idx]) * values[idx] / (
                                values[idx] - values[idx + 1]
                            )
                            self.canvas.axes.plot_surface(
                                X, Y, Z_surface, cmap="viridis", alpha=0.7
                            )
                        else:
                            self.canvas.axes.text(
                                0, 0, 0, "No surface found", color="white"
                            )
                else:
                    # 2D plotting code remains the same
                    x = np.linspace(self.x_range[0], self.x_range[1], 1000)

                    try:
                        y = eval(
                            eq,
                            {
                                "x": x,
                                "np": np,
                                "sin": np.sin,
                                "cos": np.cos,
                                "tan": np.tan,
                                "log": np.log,
                                "exp": np.exp,
                                "sqrt": np.sqrt,
                                "pi": np.pi,
                                "e": np.e,
                            },
                        )
                        self.canvas.axes.plot(
                            x,
                            y,
                            color=self.color_var.currentText(),
                            linestyle=self.style_var.currentText(),
                        )
                    except:
                        # If direct evaluation fails, try implicit equation
                        y = np.linspace(self.x_range[0], self.x_range[1], 1000)
                        X, Y = np.meshgrid(x, y)

                        def equation(X, Y):
                            return eval(
                                eq,
                                {
                                    "x": X,
                                    "y": Y,
                                    "np": np,
                                    "sin": np.sin,
                                    "cos": np.cos,
                                    "tan": np.tan,
                                    "log": np.log,
                                    "exp": np.exp,
                                    "sqrt": np.sqrt,
                                    "pi": np.pi,
                                    "e": np.e,
                                },
                            )

                        Z = equation(X, Y)
                        self.canvas.axes.contour(
                            X,
                            Y,
                            Z,
                            levels=[0],
                            colors=[self.color_var.currentText()],
                            linestyles=[self.style_var.currentText()],
                        )

            except Exception as e:
                error_message = f"Error: {str(e)}"
                self.equation_label.setText(error_message)
                self.history_listbox.addItem(error_message)

        if is_3d:
            self.canvas.axes.set_xlabel("X", color="white")
            self.canvas.axes.set_ylabel("Y", color="white")
            self.canvas.axes.set_zlabel("Z", color="white")
            self.canvas.axes.set_xlim(self.x_range)
            self.canvas.axes.set_ylim(self.x_range)
            self.canvas.axes.set_zlim(self.x_range)
        else:
            self.canvas.axes.set_xlabel("X", color="white")
            self.canvas.axes.set_ylabel("Y", color="white")
            self.canvas.axes.set_xlim(self.x_range)
            self.canvas.axes.set_ylim(self.x_range)

        # Ensure axes are visible
        self.canvas.axes.axhline(y=0, color="white", linewidth=0.5)
        self.canvas.axes.axvline(x=0, color="white", linewidth=0.5)

        self.canvas.draw()
        if update_history:
            self.history_listbox.addItem(f"Equation: {equation_str}")

    def zoom_in(self):
        center_x = (self.x_range[0] + self.x_range[1]) / 2
        range_x = (self.x_range[1] - self.x_range[0]) * 0.9
        self.x_range = (center_x - range_x / 2, center_x + range_x / 2)
        self.x = np.linspace(*self.x_range, 400)
        self.plot_graph(update_history=False)

    def zoom_out(self):
        center_x = (self.x_range[0] + self.x_range[1]) / 2
        range_x = (self.x_range[1] - self.x_range[0]) * 1.1
        self.x_range = (center_x - range_x / 2, center_x + range_x / 2)
        self.x = np.linspace(*self.x_range, 400)
        self.plot_graph(update_history=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = ScientificCalculator()
    calculator.show()
    sys.exit(app.exec_())
