import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTabWidget, QMainWindow, QColorDialog, QMessageBox, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon, QMovie, QPainter, QPen
import math
import pytz
from datetime import datetime, timedelta
import pygame
from PIL import Image

LARGEFONT = ("Arial", 50)


class Alarm(QWidget):
    def __init__(self, parent_layout):
        super().__init__()
        self.layout = parent_layout
        self.alarm_time = ""

        # Membuat canvas untuk jam analog
        self.canvas_label = QLabel(self)
        self.canvas_label.setFixedSize(200, 200)
        self.layout.addWidget(self.canvas_label)
        self.canvas_label.setAlignment(Qt.AlignCenter)  # Mengatur widget di tengah
        self.layout.addWidget(self.canvas_label, alignment=Qt.AlignCenter)

        # Label untuk menampilkan waktu Indonesia Barat
        self.time_label = QLabel("", self)
        self.time_label.setFont(QFont("Bolditalic", 100))
        self.layout.addWidget(self.time_label)

        set_alarm_label = QLabel("Set Alarm (JAM : MENIT)", self)
        set_alarm_label.setFont(QFont("Arial", 20))  # Menetapkan jenis font dan ukuran
        set_alarm_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(set_alarm_label)
        self.entry = QLineEdit(self)
        self.layout.addWidget(self.entry)

        # Menambahkan menu pilihan untuk memilih suara musik
        self.sound_label = QLabel("Select Sound:", self)
        self.sound_combo = QComboBox(self)
        self.sound_combo.addItem("Sound 1")
        self.sound_combo.addItem("Sound 2")
        self.sound_combo.addItem("Sound 3")
        self.sound_combo.addItem("Sound 4")
        self.sound_combo.addItem("Sound 5")
        self.layout.addWidget(self.sound_label)
        self.layout.addWidget(self.sound_combo)
        
        self.set_alarm_button = QPushButton("SET ALARM", self)
        self.set_alarm_button.clicked.connect(self.set_alarm)
        self.layout.addWidget(self.set_alarm_button)

        # Memperbarui waktu setiap detik
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        #tombol menghentikan alarm
        self.stop_alarm_button = QPushButton("Stop Alarm", self)
        self.stop_alarm_button.clicked.connect(self.stop_alarm)
        self.layout.addWidget(self.stop_alarm_button)

        #self.show()

    def update_time(self):
        # Mendapatkan waktu saat ini di timezone Asia/Jakarta
        tz = pytz.timezone('Asia/Jakarta')
        current_time = datetime.now(tz)

        # Menampilkan waktu Indonesia Barat
        self.time_label.setText(current_time.strftime("%H:%M:%S %p"))

        # Menggambar jarum jam
        self.draw_clock(current_time)

    def draw_clock(self, current_time):
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Menggambar lingkaran jam di tengah window
        center = pixmap.rect().center()
        radius = min(center.x(), center.y()) - 10  # Radius lingkaran agar tidak melebihi batas pixmap
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(center, radius, radius)

        # Menggambar angka jam di sekitar lingkaran
        painter.setFont(QFont("Helvetica", 12))
        for hour in range(1, 13):
            angle = math.radians(30 * hour - 90)
            x = center.x() + 0.8 * radius * math.cos(angle) - 6  # Koreksi posisi untuk penulisan teks
            y = center.y() + 0.8 * radius * math.sin(angle) + 6  # Koreksi posisi untuk penulisan teks
            painter.drawText(int(x), int(y), str(hour))

        # Menggambar jarum jam di tengah lingkaran
        hour_angle = math.radians((current_time.hour % 12) * 30 - 90)
        minute_angle = math.radians(current_time.minute * 6 - 90)

        hour_x = center.x() + 0.5 * radius * math.cos(hour_angle)
        hour_y = center.y() + 0.5 * radius * math.sin(hour_angle)
        painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine))
        painter.drawLine(center.x(), center.y(), int(hour_x), int(hour_y))

        minute_x = center.x() + 0.7 * radius * math.cos(minute_angle)
        minute_y = center.y() + 0.7 * radius * math.sin(minute_angle)
        painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
        painter.drawLine(center.x(), center.y(), int(minute_x), int(minute_y))

        painter.end()
        self.canvas_label.setPixmap(pixmap)

    def set_alarm(self):
        alarm_time_str = self.entry.text()

        try:
            alarm_hour, alarm_minute = map(int, alarm_time_str.split(':'))

            # Mengonversi ke timezone Indonesia Barat
            tz = pytz.timezone('Asia/Jakarta')
            current_time = datetime.now(tz)
            alarm_time = current_time.replace(hour=alarm_hour, minute=alarm_minute, second=0, microsecond=0)

            # Memeriksa apakah alarm diatur pada waktu yang sudah berlalu
            if alarm_time < current_time:
                alarm_time += timedelta(days=1)  # Menambahkan satu hari jika alarm sudah berlalu

            # Hitung selisih waktu antara alarm dan waktu sekarang
            delta = alarm_time - current_time

            # Jalankan alarm setelah selisih waktu tersebut
            QTimer.singleShot(int(delta.total_seconds() * 1000), self.ring_alarm)

            QMessageBox.information(self, "Alarm Set", f"Alarm set for {alarm_time_str}")

        except Exception as e:
            QMessageBox.critical(self, "Error", "Invalid time format. Please use HH:MM.")

    def ring_alarm(self):
        #QMessageBox.information(self, "Alarm", "Wake up!")
        # Memilih file musik berdasarkan pilihan dari ComboBox
        selected_sound = self.sound_combo.currentText()
        if selected_sound == "Sound 1":
            sound_file = "sound/sound1.mp3"            
        elif selected_sound == "Sound 2":
            sound_file = "sound/sound2.mp3"
        elif selected_sound == "Sound 3":
            sound_file = "sound/sound3.mp3"
        elif selected_sound == "Sound 4":
            sound_file = "sound/sound4.mp3"
        else:
            sound_file = "sound/sound5.mp3"
        # Memainkan suara alarm dari file MP3
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    def stop_alarm(self):
        pygame.mixer.music.stop()


class Stopwatch(QWidget):
    def __init__(self, parent_layout):
        super().__init__()
        self.layout = parent_layout
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

        # Label to display stopwatch time
        self.stopwatch_label = QLabel("00:00.00", self)
        self.stopwatch_label.setFont(QFont("Bolditalic", 100))
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.stopwatch_label)

        # Buttons to control stopwatch
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_stopwatch)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_stopwatch)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_stopwatch)
        self.reset_button.setEnabled(False)
        self.layout.addWidget(self.reset_button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

    def start_stopwatch(self):
        if not self.running:
            if not self.start_time:
                self.start_time = datetime.now() - timedelta(seconds=self.elapsed_time)
            self.update_time()
            self.running = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.reset_button.setEnabled(False)
            self.timer.start(10)

    def stop_stopwatch(self):
        if self.running:
            self.elapsed_time = (datetime.now() - self.start_time).total_seconds()
            self.running = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.timer.stop()

    def reset_stopwatch(self):
        self.start_time = None
        self.elapsed_time = 0
        self.stopwatch_label.setText("00:00.00")
        self.reset_button.setEnabled(False)

    def update_time(self):
        if self.running:
            now = datetime.now()
            elapsed_time = (now - self.start_time).total_seconds()
            minutes, seconds = divmod(elapsed_time, 60)
            time_str = f"{int(minutes):02}:{seconds:05.2f}"
            self.stopwatch_label.setText(time_str)


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIMPLE ALARM")
        self.setWindowIcon(QIcon('image/icon1.ico'))
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # GIF WALPAPER
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 800, 600)  # Sesuaikan dengan ukuran jendela Anda
        self.background_label.setAttribute(Qt.WA_TranslucentBackground)  # Membuat latar belakang jendela menjadi transparan
        movie = QMovie("image/final-gif.gif")  # Ganti 'background.gif' dengan path ke gambar GIF Anda
        self.background_label.setMovie(movie)
        movie.start()

        # Create central widget and set layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create tabs
        self.tab_control = QTabWidget()
        self.home_tab = QWidget()
        self.alarm_tab = QWidget()
        self.stopwatch_tab = QWidget()

        self.tab_control.addTab(self.home_tab, "Home")
        self.tab_control.addTab(self.alarm_tab, "Alarm")
        self.tab_control.addTab(self.stopwatch_tab, "Stopwatch")
        self.layout.addWidget(self.tab_control)

        # Set up layouts for each tab
        self.home_layout = QVBoxLayout(self.home_tab)
        self.alarm_layout = QVBoxLayout(self.alarm_tab)
        self.stopwatch_layout = QVBoxLayout(self.stopwatch_tab)

        # Create Alarm and Stopwatch instances
        self.alarm = Alarm(self.alarm_layout)
        self.stopwatch = Stopwatch(self.stopwatch_layout)

        # Additional setup for the main window
        self.setup_home_tab()

    def setup_home_tab(self):
        # Home tab content
        self.logo(self.home_layout)
        self.garis_pemisah1(self.home_layout)
        self.waktu_layer1(self.home_layout)
        self.update_time()
        self.garis_pemisah2(self.home_layout)
        self.create_exit_button()
        #self.tombol_ganti_warna(self.home_layout)

    def logo(self, layout):
        foto_ori = Image.open('image/logo1.png')
        ukuran_foto = foto_ori.resize((490, 160), Image.Resampling.LANCZOS)
        ukuran_foto.save("image/logo_resized.png")  # Saving resized image
        self.mylogo = QPixmap("image/logo_resized.png")  # Loading the resized image
        self.image_label = QLabel()
        self.image_label.setPixmap(self.mylogo)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

    def garis_pemisah1(self, layout):
        line = QLabel()
        line.setFixedHeight(6)
        line.setStyleSheet("background-color: red;")
        layout.addWidget(line)

    def garis_pemisah2(self, layout):
        line = QLabel()
        line.setFixedHeight(6)
        line.setStyleSheet("background-color: black;")
        layout.addWidget(line)

    #def tombol_ganti_warna(self, layout):
    #    self.color_button = QPushButton("Silahkan Pilih Warna Untuk Di Ganti")
    #    self.color_button.clicked.connect(self.ganti_warna)
    #    layout.addWidget(self.color_button, alignment=Qt.AlignBottom)

    #def ganti_warna(self):
    #    colors = QColorDialog.getColor()
    #    if colors.isValid():
    #        self.image_label.setStyleSheet(f"background-color: {colors.name()};")
    #        self.clock_label.setStyleSheet(f"background-color: {colors.name()};")

    def waktu_layer1(self, layout):
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 60))
        self.clock_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.clock_label)

    def update_time(self):
        current_time = time.strftime('%I:%M:%S %p')
        self.clock_label.setText(current_time)
        QTimer.singleShot(1000, self.update_time)

    def create_exit_button(self):
        exit_button = QPushButton(">>> KELUAR 😊 APLIKASI << ", self)
        exit_button.clicked.connect(self.close_application)
        exit_button.setStyleSheet("QPushButton {"
                        "border-radius: 10px;"
                        "background-color: white;"
                        "color: black;"
                        "font-family: Arial;"
                        "font-size: 30px;"
                        "}"
                        "QPushButton:hover {"
                        "color: red;"
                        "}")
        self.home_layout.addWidget(exit_button, alignment=Qt.AlignCenter)

    def close_application(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Application()
    main_window.show()
    sys.exit(app.exec_())
