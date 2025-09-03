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
    QLabel
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
        print("Protocolo de actualización de estado de conexión activado.")
      
    def desconection_protocol(self):
        """Protocolo para manejar la desconexión. de cara a visuales"""
        self.serial.disconnect_port()
        self.connect_button.setChecked(False)
        #self.label_color = "red"

            






class ServoControl(QWidget):
    def __init__(self, serial_engine:Serial_Engine, title:str = "Control de servo"):
        super().__init__()
        self.serial = serial_engine

         


        self.label = QLabel()
    def closeEvent(self, a0):
        self.serial.disconnect_port()
        return super().closeEvent(a0)
        


    

        
    

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")

        self.serial_engine = Serial_Engine()
        self.serial_engine_thread = QThread()
        self.serial_engine.moveToThread(self.serial_engine_thread)
        self.serial_engine_thread.start()   


        self.COM_module = COM_module(self.serial_engine)
        



        main_layout = QVBoxLayout()
        main_layout.addWidget(self.COM_module)
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