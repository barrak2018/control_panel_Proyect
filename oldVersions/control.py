import sys
import serial
import serial.tools.list_ports as list_ports

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QDial
)

class COM_Module(QWidget):
    """
    Clase que genera un selector de Puerto COM y controla la Conexion serial (Requiere: QComboBox, QLabel, QHBoxLayout, QWidget, serial(Pyserial))
    
    """
    def __init__(self):
        super().__init__()
        # Variables
        self.serial_connection = None
        self.current_port = None

        # lista de puertos 

        self.ports = QComboBox()
        self.ports.addItems(self.get_Ports())
        self.ports.currentTextChanged.connect(self.on_select_port)
        self.ports.setFixedWidth(90)
        self.ports.setFixedHeight(20)


        # indicador de conneccion

        self.label =  QLabel()
        self.label.setText("desconectado")
        self.label.setStyleSheet("background-color: red;")
        self.label.setFixedWidth(90)
        self.label.setFixedHeight(20)

        # boton de conexion 

        self.connection_switch = QPushButton()
        self.connection_switch.setText("0/1")
        self.connection_switch.setCheckable(True)
        self.connection_switch.clicked.connect(self.toggle_connection)

        # layout

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.ports)
        layout.addWidget(self.label)
        layout.addWidget(self.connection_switch)
        
        

        self.setFixedHeight(50)
        self.setLayout(layout)

    # Funciones

    def get_Ports(self):
        """
        Obtiene una lista Depuertos COM Disponibles
        Returns:
            list:Lista de Puertos COM Disponibles
        """
        
        puestos =  list_ports.comports()
        respuesta =  []
        for port in puestos:
            respuesta.append(port.device)
        return respuesta
    
    def on_select_port(self, port:str):
        """
        Crea una Connexion serial segun el puerto ingresado
        Args: 
            port (str): Puerto COM Objetivo
        """
        self.current_port = port
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Vieja conexion cerrada")
            
        try:
            self.serial_connection = serial.Serial(port, 9600)
            if not self.serial_connection.is_open:
                self.serial_connection.open()
            print(f"Conexion establecida {port}")
            self.label.setStyleSheet("background-color: lightgreen;")
            self.label.setText("conectado")
            self.connection_switch.setChecked(True)
        except serial.SerialException as err:
            print(F"error de comunicacion con {port}: {err}")
            self.label.setText("desconectado")
            self.label.setStyleSheet("background-color: red;")
            self.connection_switch.setChecked(False)
            self.serial_connection = None

    def disconect(self):
        """
        Elimina cualquier Conexion serial existente
        """
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Vieja conexion cerrada")
            self.label.setStyleSheet("background-color: red;")
    
    def comunication(self, message:str):
        #print(self.serial_connection)
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(message.encode())
                print("transminitendo...")
            except serial.SerialException as err:
                print(f"error en el emvio del comando: {err}")
        else:
            print("Comunicacion serial fuera de linea!")
    
    def toggle_connection(self):
        if self.connection_switch.isChecked():
            self.on_select_port(self.current_port)
        else:
            self.disconect()

        if self.serial_connection and self.serial_connection.is_open:
            self.connection_switch.setChecked(True)
        else:
            self.connection_switch.setChecked(False)

            
class light_panel(QWidget):

    def __init__(self, com_module_ref:COM_Module):
        super().__init__()

        self.COM_module = com_module_ref


        self.label = QLabel()
        self.label.setText("Luces")
        
        self.label.setFixedWidth(90)
        self.label.setFixedHeight(20)
        label_style = """
        font-size: 16px;
        font-weight: bold;
        font-family: Arial;"""
        self.label.setStyleSheet(label_style)

        self.Luces = QPushButton()
        self.Luces.setText("Placa")
        self.Luces.setFixedWidth(90)
        self.Luces.setFixedHeight(20)
        self.Luces.clicked.connect(lambda: self.COM_module.comunication("led"))
        

        layout  = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.Luces)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


class Servo_panel(QWidget):

    def __init__(self, com_module_ref:COM_Module):
        super().__init__()

        self.COM_module = com_module_ref


        self.label = QLabel()
        self.label.setText("Servo")
        self.label.setFixedWidth(90)
        self.label.setFixedHeight(20)
        label_style = """
        font-size: 16px;
        font-weight: bold;
        font-family: Arial;"""
        self.label.setStyleSheet(label_style)

        self.servo = QDial()
        self.servo.setNotchesVisible(True)
        self.servo.setRange(0,180)
        self.servo_label = QLabel()
        self.servo.valueChanged.connect(self.servo_label.setNum)
        self.servo.sliderReleased.connect(lambda: self.COM_module.comunication(f"servo{self.servo.value()}"))
        

        layout  = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.servo_label)
        layout.addWidget(self.servo)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("COM")
        # Widgets de los modulos
        self.COM_module = COM_Module()
        luces = light_panel(self.COM_module)
        Servo_panel_ref = Servo_panel(self.COM_module)
        

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.COM_module)

        container1 = QWidget()
        container1.setLayout(QHBoxLayout())
        container1.layout().addWidget(luces)
        container1.layout().addWidget(Servo_panel_ref)
        container1.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(container1)

        

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        
    def closeEvent(self, a0):
        self.COM_module.disconect()
        a0.accept()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()