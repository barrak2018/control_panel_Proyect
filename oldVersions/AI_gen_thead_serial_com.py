import sys
import serial
import serial.tools.list_ports as list_ports

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
// ...existing code...
    QDial
)

class SerialWorker(QObject):
    """
    Maneja las operaciones seriales en un hilo separado para no bloquear la GUI.
    """
    connection_status = pyqtSignal(bool, str)  # Señal para estado de conexión (exito/fallo, puerto)
    error = pyqtSignal(str)                    # Señal para reportar errores

    def __init__(self):
        super().__init__()
        self.serial_connection = None
        self.is_running = True

    def connect_port(self, port: str):
        """Intenta conectar al puerto serial especificado."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            if not self.serial_connection.is_open:
                self.serial_connection.open()
            self.connection_status.emit(True, port)
        except serial.SerialException as e:
            self.connection_status.emit(False, port)
            self.error.emit(f"Error al conectar a {port}: {e}")

    def write_data(self, message: str):
        """Escribe datos en el puerto serial si está abierto."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(message.encode())
            except serial.SerialException as e:
                self.connection_status.emit(False, "")
                self.error.emit(f"Error de comunicación: {e}. Desconectando.")
                self.disconnect_port()
        else:
            self.error.emit("Comunicación serial fuera de línea!")

    def disconnect_port(self):
        """Cierra la conexión serial."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.connection_status.emit(False, "")
        self.is_running = False


class COM_Module(QWidget):
    """
    Clase que genera un selector de Puerto COM y controla la Conexion serial (Requiere: QComboBox, QLabel, QHBoxLayout, QWidget, serial(Pyserial))
    
    """
    # Señales para comunicarse con el worker
    request_connect = pyqtSignal(str)
    request_disconnect = pyqtSignal()
    request_write = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Variables
        self.current_port = None

        # --- Configuración del Hilo para el Worker Serial ---
        self.thread = QThread()
        self.worker = SerialWorker()
        self.worker.moveToThread(self.thread)

        # Conectar señales y slots entre GUI y Worker
        self.request_connect.connect(self.worker.connect_port)
        self.request_disconnect.connect(self.worker.disconnect_port)
        self.request_write.connect(self.worker.write_data)

        self.worker.connection_status.connect(self.update_connection_status)
        self.worker.error.connect(lambda msg: print(msg))

        self.thread.start()


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

        # layout

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.ports)
        layout.addWidget(self.label)
        
        

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
        Envía una solicitud para crear una conexión serial en el hilo del worker.
        Args: 
            port (str): Puerto COM Objetivo
        """
        self.current_port = port
        self.request_connect.emit(port)

    def update_connection_status(self, is_connected: bool, port: str):
        """Actualiza la GUI basado en el estado de la conexión."""
        if is_connected:
            print(f"Conexion establecida {port}")
            self.label.setStyleSheet("background-color: lightgreen;")
            self.label.setText("conectado")
        else:
            print("Conexión cerrada o fallida.")
            self.label.setText("desconectado")
            self.label.setStyleSheet("background-color: red;")


    def disconect(self):
        """
        Elimina cualquier Conexion serial existente
        """
        self.request_disconnect.emit()
        self.thread.quit()
        self.thread.wait()
    

    def comunication(self, message:str):
        self.request_write.emit(message)




            
class light_panel(QWidget):
// ...existing code...
// ...existing code...
// ...existing code...
        self.setCentralWidget(main_widget)
        
    def closeEvent(self, a0):
        self.COM_module.disconect()
        a0.accept()




app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()