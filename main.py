import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QTextEdit, QLineEdit, QMessageBox, QLabel, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import serial
import serial.tools.list_ports


class SerialReader(QThread):
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connected = pyqtSignal()  # сигнал успішного підключення

    def __init__(self, port_name, baudrate=9600, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.baudrate = baudrate
        self.running = False
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port_name, self.baudrate, timeout=1)
        except Exception as e:
            self.error_occurred.emit(str(e))
            return

        # Порт відкрився успішно
        self.connected.emit()

        self.running = True
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.readline()
                    try:
                        line = raw.decode(errors='ignore')
                    except:
                        line = ''
                    self.data_received.emit(line)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.error_occurred.emit(str(e))
                break

        if self.ser and self.ser.is_open:
            self.ser.close()

    def write(self, text):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(text.encode())
            except Exception as e:
                self.error_occurred.emit(str(e))

    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Port Interface")
        self.reader_thread = None
        self.last_received_time = time.time()

        self.init_ui()
        self.setup_timers()
        self.refresh_com_ports()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # COM port та baudrate
        com_layout = QHBoxLayout()
        self.combobox = QComboBox()
        self.combobox.addItem("")  # пустий перший рядок
        self.combobox.currentIndexChanged.connect(self.on_port_selected)

        # Додамо вибір baudrate з розширеним списком
        self.baudrate_box = QComboBox()
        for rate in ["4800", "9600", "14400", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]:
            self.baudrate_box.addItem(rate)
        self.baudrate_box.setCurrentText("9600")

        self.refresh_button = QPushButton("Refresh COMs")
        self.refresh_button.clicked.connect(self.refresh_com_ports)
        com_layout.addWidget(QLabel("COM Port:"))
        com_layout.addWidget(self.combobox)
        com_layout.addWidget(QLabel("Baudrate:"))
        com_layout.addWidget(self.baudrate_box)
        com_layout.addWidget(self.refresh_button)
        layout.addLayout(com_layout)

        # Connect / Disconnect
        conn_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setEnabled(False)
        self.connect_button.clicked.connect(self.connect_serial)
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        conn_layout.addWidget(self.connect_button)
        conn_layout.addWidget(self.disconnect_button)
        layout.addLayout(conn_layout)

        # Text dump (світло-сірий тон з рамкою)
        self.text_dump = QTextEdit()
        self.text_dump.setReadOnly(True)
        self.text_dump.setStyleSheet("background-color: #F0F0F0; border: 1px solid black;")  # Light background matching window with thin black border
        layout.addWidget(self.text_dump)

        # Send text та кнопка
        send_layout = QHBoxLayout()
        self.send_input = QLineEdit()
        self.send_input.setEnabled(False)
        # При натисканні Enter у полі викликати send_text
        self.send_input.returnPressed.connect(self.send_text)
        self.send_button = QPushButton("Send")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_text)
        # Checkbox "keep command"
        self.keep_checkbox = QCheckBox("keep command")
        self.keep_checkbox.setChecked(False)

        send_layout.addWidget(QLabel("Send Text:"))
        send_layout.addWidget(self.send_input)
        send_layout.addWidget(self.send_button)
        send_layout.addWidget(self.keep_checkbox)
        layout.addLayout(send_layout)

    def setup_timers(self):
        # Перевірка “здоров’я” з'єднання кожні 5 сек
        self.check_timer = QTimer(self)
        self.check_timer.setInterval(5000)  # 5 секунд
        self.check_timer.timeout.connect(self.check_connection_health)

    def refresh_com_ports(self):
        self.combobox.clear()
        self.combobox.addItem("")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.combobox.addItem(port.device)
        self.connect_button.setEnabled(False)

    def on_port_selected(self, index):
        port = self.combobox.currentText()
        if port:
            self.connect_button.setEnabled(True)
        else:
            self.connect_button.setEnabled(False)

    def connect_serial(self):
        port = self.combobox.currentText()
        if not port:
            return

        baud = int(self.baudrate_box.currentText())
        self.reader_thread = SerialReader(port, baudrate=baud)
        self.reader_thread.data_received.connect(self.handle_data)
        self.reader_thread.error_occurred.connect(self.handle_error)
        self.reader_thread.connected.connect(self.handle_connected)
        self.reader_thread.start()

        self.connect_button.setEnabled(False)
        self.text_dump.append(f"Connecting to {port} at {baud} baud…")
        self.last_received_time = time.time()
        self.check_timer.start()

    def handle_connected(self):
        # Це викличеться, якщо порт відкрився без помилок
        self.text_dump.append(f"Connected to {self.reader_thread.port_name}.\n")
        self.disconnect_button.setEnabled(True)
        self.send_input.setEnabled(True)
        self.send_button.setEnabled(False)

    def disconnect_serial(self):
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread = None

        self.disconnect_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.send_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.text_dump.append("Disconnected.\n")
        self.check_timer.stop()

    def handle_data(self, data):
        text = data.rstrip("\r\n")
        self.text_dump.append(text)
        self.last_received_time = time.time()

        # Якщо порт відкритий і ми вже отримали хоч один байт, можна активувати Send
        if self.reader_thread and self.reader_thread.ser and self.reader_thread.ser.is_open:
            self.send_button.setEnabled(True)

        # Тут можна додати логіку пошуку "SEQUENCE:" + збір у масив до "\n\n"

    def handle_error(self, error_msg):
        QMessageBox.critical(self, "Serial Error", f"Error: {error_msg}")
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread = None
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)
        self.send_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.combobox.setCurrentIndex(0)
        self.check_timer.stop()
        self.text_dump.append(f"Connection failed: {error_msg}\n")

    def check_connection_health(self):
        if not self.reader_thread:
            return
        elapsed = time.time() - self.last_received_time
        if elapsed > 5:
            self.send_button.setEnabled(False)
        else:
            self.send_button.setEnabled(True)

    def send_text(self):
        text = self.send_input.text()
        if self.reader_thread:
            self.reader_thread.write(text + "\n")
            if not self.keep_checkbox.isChecked():
                self.send_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec_())
