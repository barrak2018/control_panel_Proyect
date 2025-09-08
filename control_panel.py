import sys
from PyQt6.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QDial,
    QLabel,
    QGridLayout,
    QGroupBox
)
from serial_engine import Serial_Engine


class COM_module(QWidget):
    def __init__(self, serial_engine:Serial_Engine):
        super().__init__()

        self.serial = serial_engine
        # Señales
        self.serial.connection_status.connect(self.conection_status_update_protocol)
        
        self.current_port = None
        # Obtener lista de puertos disponibles
        ports_list = self.serial.get_list_ports()
        self.ports = ["None"]
        for port in ports_list:
            self.ports.append(port)
            
        # Crear un combobox para seleccionar el puerto
        self.port_combobox = QComboBox()
        self.port_combobox.addItems(self.ports)
        self.port_combobox.currentTextChanged.connect(self.update_current_port)
        self.port_combobox.currentTextChanged.connect(self.desconection_protocol)
        self.port_combobox.setFixedHeight(40)

        # Label que muestra el estado de la conexion
        self.label = QLabel()
        self.label.setText("Desconectado")
        
        self.label.setStyleSheet(f"background-color: red; border: 5px none #101010; font-weight: bold; border-radius: 5px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(95, 40)


        # Botón para conectar/desconectar
        self.connect_button = QPushButton()
        self.connect_button.setText("0/1")
        self.connect_button.setCheckable(True)
        self.connect_button.released.connect(self.connection_start)
        self.connect_button.setFixedHeight(40)
        
        # Configurar el diseño del módulo
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.port_combobox)
        layout.addWidget(self.label)
        layout.addWidget(self.connect_button)
        
        self.setLayout(layout)
        self.setMaximumSize(370, 100)
    
    def update_current_port(self, port):
        """Actualizar el puerto seleccionado."""
        self.current_port = port

    def connection_start(self):
        """Iniciar o detener la conexión según el estado del botón."""
        if not self.connect_button.isChecked():
            self.serial.disconnect_port()
            self.connect_button.setChecked(False)
        elif self.connect_button.isChecked():
            self.serial.connect_port(self.current_port)
            if self.serial.isConnected == False:
                self.connect_button.setChecked(False)
            else:
                self.connect_button.setChecked(True)
        else:
            print("No se realizó ninguna acción.")

    def conection_status_update_protocol(self, status:bool):
        """Actualizar el protocolo según el estado de conexión."""
        if status:
            
            self.label.setText("Conectado")
            self.label.setStyleSheet("background-color: #57F527; border: 5px none #101010; font-weight: bold; border-radius: 5px;")
        else:
            self.label.setText("Desconectado")
            self.label.setStyleSheet(f"background-color: red; border: 5px none #101010; font-weight: bold; border-radius: 5px;")
        if not status: 
            self.desconection_protocol()
        #print("Protocolo de actualización de estado de conexión activado.")
      
    def desconection_protocol(self):
        """Protocolo para manejar la desconexión. de cara a visuales"""
        self.serial.disconnect_port()
        self.connect_button.setChecked(False)
        #self.label_color = "red"


class Servo_control(QGroupBox):
    def __init__(self, serial_engine:Serial_Engine, title:str = "Control de servo", command:str = "servo"):
        super().__init__()
        self.serial = serial_engine
        self.serial.connection_status.connect(self.connection_update_protocol)
         
        
        self.setTitle(title)

        # indicador de Posicion
        self.grados = QLabel("None")
        self.grados.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # cero button
        self.cero = QPushButton()
        self.cero.setText("0°")
        self.cero.released.connect(lambda: self.serial.send(f"{command}0"))
        self.cero.released.connect(lambda: self.grados.setText("0°"))
        self.cero.setEnabled(False)
        
        # 180 button
        self.boton180 = QPushButton()
        self.boton180.setText("180°")
        self.boton180.released.connect(lambda: self.serial.send(f"{command}180"))
        self.boton180.released.connect(lambda: self.grados.setText("180°"))
        self.boton180.setEnabled(False)

        # 45 button
        self.boton45 = QPushButton()
        self.boton45.setText("45°")
        self.boton45.released.connect(lambda: self.serial.send(f"{command}45"))
        self.boton45.released.connect(lambda:self.grados.setText("45°"))
        self.boton45.setEnabled(False)

        # 135 button
        self.boton135 = QPushButton()
        self.boton135.setText("135°")
        self.boton135.released.connect(lambda: self.serial.send(f"{command}135"))
        self.boton135.released.connect(lambda: self.grados.setText("135°"))
        self.boton135.setEnabled(False)

        # 90 button
        self.boton90 = QPushButton()
        self.boton90.setText("90°")
        self.boton90.released.connect(lambda: self.serial.send(f"{command}90"))
        self.boton90.released.connect(lambda: self.grados.setText("90°"))
        self.boton90.setEnabled(False)

        # dial
        self.dial  = QDial()
        self.dial.setRange(0,180)
        self.dial.setNotchesVisible(True)
        self.dial.sliderReleased.connect(lambda: self.serial.send(f"{command}{self.dial.value()}"))
        self.dial.valueChanged.connect(lambda valor : self.grados.setText(f"{valor}°"))
        self.dial.setEnabled(False)

        

        # grupo de 4 botones 
        container2Layout = QGridLayout()
        container2Layout.setContentsMargins(0, 0, 0, 0)
        container2Layout.setSpacing(0)
        container2Layout.addWidget(self.boton45, 0, 0)
        container2Layout.addWidget(self.boton135, 0, 1)
        container2Layout.addWidget(self.cero, 1, 0)
        container2Layout.addWidget(self.boton180, 1, 1)
        container2 = QWidget()
        container2.setLayout(container2Layout)

        # grupo completo de botones
        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.setSpacing(0)
        containerLayout.setContentsMargins(10, 10, 10, 10)
        
        containerLayout.addWidget(self.grados)
        containerLayout.addWidget(self.dial)
        containerLayout.addWidget(self.boton90)
        containerLayout.addWidget(container2)
        
        self.setFixedSize(242, 215)
        self.setLayout(containerLayout)
        
        
    def connection_update_protocol (self, status:bool):
        if status:
            self.cero.setEnabled(True)
            self.boton135.setEnabled(True)
            self.boton180.setEnabled(True)
            self.boton45.setEnabled(True)
            self.boton90.setEnabled(True)
            self.dial.setEnabled(True)

        else:
            self.cero.setEnabled(False)
            self.boton135.setEnabled(False)
            self.boton180.setEnabled(False)
            self.boton45.setEnabled(False)
            self.boton90.setEnabled(False)
            self.dial.setEnabled(False)
            self.dial.setValue(0)
            self.grados.setText("None")
        
    
class Ligh_control(QGroupBox):
    '''
    Genera una botonera capaz de enviar comandos por comunicacion serial
    REQUIERE Serial_Engine!!!!!
    Args:
        serial_engine (Serial_Engine): instancia de la clase Serial_engine en uso
        title (str): Titulo Principal de panel
        buttons (list): lista 2d con par ordenado de titulo y comando {debe ser de esta manera: [["titulo1", "comando1"],["titulo2", "comando2"]]}

    '''
    def __init__(self, serial_engine:Serial_Engine, title:str = "Control de Luces", buttons: list = [["titulo", "comando"]]):
        super().__init__()
        self.setTitle(title)
        self.serial = serial_engine
        serial_engine.connection_status.connect(self.connection_update_protocol)
        self.buttons_list = []
        for titulo, comando in buttons:
            boton = QPushButton(titulo)
            print(comando)
            boton.released.connect(lambda com = comando: serial_engine.send(com))
            boton.setEnabled(False)
            self.buttons_list.append(boton)


        
        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 10, 10, 10)
        x = 0
        y = 0
        for widget in self.buttons_list:
            layout.addWidget(widget, y, x)
            x += 1
            if x > 1:
                x = 0
                y += 1
            


        self.setMaximumWidth(242)
        self.setLayout(layout)
   
    def connection_update_protocol (self, status:bool):
        if status:
            for boton in self.buttons_list:
                boton.setEnabled(True)
        else:
            for boton in self.buttons_list:
                boton.setEnabled(False)
                

    

    
        


    

        
    

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")

        self.serial_engine = Serial_Engine()
        self.serial_engine_thread = QThread()
        self.serial_engine.moveToThread(self.serial_engine_thread)
        self.serial_engine_thread.start()   


        self.COM_module = COM_module(self.serial_engine)
        self.servo = Servo_control(self.serial_engine)
        botones = [["led 1", "led1"],["led 2", "led2"], ["led 3", "led3"]]
        self.luz = Ligh_control(self.serial_engine, "luz de la placa", botones)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.COM_module)
        main_layout.addWidget(self.servo)
        main_layout.addWidget(self.luz)
        # main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def closeEvent(self, event):
        self.serial_engine.disconnect_port()
        self.serial_engine_thread.quit()
        self.serial_engine_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_window()
    window.show()
    sys.exit(app.exec())