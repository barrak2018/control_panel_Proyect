import serial
from serial.tools import list_ports
from PyQt6.QtCore import pyqtSignal, QObject, QThread
import time  # Importamos la librería time

class Monitor(QObject):
    on_desconection = pyqtSignal()

    def __init__(self, conexion: serial.Serial):
        super().__init__()
        self.is_running = True
        self.conexion = conexion

    def surveillance(self):
        if self.conexion and self.conexion.is_open:
            print("Monitor: Iniciando vigilancia...")
            while self.is_running:
                try:
                    # Agregamos una pequeña pausa para no consumir todo el CPU
                    time.sleep(0.01) 
                    if self.conexion.in_waiting > 0:
                        message = self.conexion.readline().decode("utf-8").strip()
                        print(f"Monitor: {message}")
                except serial.SerialException as e:
                    print(f"Monitor: error de serial: {e}")
                    self.is_running = False
                    self.on_desconection.emit()
        else:
            print("Monitor: Conexión no válida, terminando.")
            self.on_desconection.emit()

    def stop(self):
        self.is_running = False

class Serial_Engine(QObject):
    connection_status = pyqtSignal(bool, str)
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_port = None
        self.connection = None
        self.isConnected = False
        self.hilo_monitor = None
        self.monitor = None

    def get_list_ports(self):
        ports = list_ports.comports()
        res = [port.device for port in ports]
        return res

    def connect_port(self, port: str, baud: int = 9600):
        if self.connection and self.connection.is_open:
            self.disconnect_port()
            print(f"SerialEngine: Cerrando conexión previa con puerto {self.current_port}")

        try:
            self.connection = serial.Serial(port, baud)
            if not self.connection.is_open:
                self.connection.open()
            self.current_port = port
            self.isConnected = True
            
            # Iniciar el monitor en un hilo separado
            self.start_monitor()

            print(f"SerialEngine: Conectado al puerto {self.current_port}")
            self.connection_status.emit(True, self.current_port)

        except serial.SerialException as err:
            print(f"SerialEngine: error de Conexión \"{err}\"")
            self.error.emit(f"Error de Conexión \"{err}\"")
            self.isConnected = False
            self.connection_status.emit(False, "")

    def start_monitor(self):
        if not self.hilo_monitor:
            self.hilo_monitor = QThread()
            self.monitor = Monitor(self.connection)
            self.monitor.moveToThread(self.hilo_monitor)
            self.hilo_monitor.started.connect(self.monitor.surveillance)
            self.hilo_monitor.finished.connect(self.hilo_monitor.deleteLater)
            self.monitor.on_desconection.connect(self.disconnect_port)
            self.hilo_monitor.start()

    def disconnect_port(self):
        if self.monitor:
            self.monitor.stop()

        if self.hilo_monitor and self.hilo_monitor.isRunning():
            self.hilo_monitor.quit()
            self.hilo_monitor.wait()

        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"SerialEngine: Desconectado del puerto {self.current_port}")
            self.isConnected = False
            self.connection_status.emit(False, "")
            self.hilo_monitor = None
            self.monitor = None
    
    def send(self, data: str):
        if self.connection and self.connection.is_open:
            try:
                self.connection.write(data.encode())
                print(f"SerialEngine: Enviado \"{data}\" al puerto {self.current_port}")
            except serial.SerialException as err:
                print(f"SerialEngine: error al enviar datos \"{err}\"")
                self.error.emit(f"Error al enviar datos \"{err}\"")
        else:
            print("SerialEngine: No hay conexión activa para enviar datos")
            self.error.emit("No hay conexión activa para enviar datos")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    
    engine = Serial_Engine()
    print("Puertos disponibles:", engine.get_list_ports())
    
    if engine.get_list_ports():
        # Conectarse al primer puerto disponible
        port_to_connect = engine.get_list_ports()[0]
        engine.connect_port(port_to_connect)
        print("Estado de la conexión:", engine.isConnected)

        # Esperar un tiempo para que el monitor haga su trabajo
        time.sleep(5)
        
        # Enviar un mensaje
        engine.send("Hello, Serial Port!")
        
        # Esperar un poco más y luego desconectar
        time.sleep(2)
        engine.disconnect_port()
    else:
        print("No se encontraron puertos seriales disponibles.")
    
    sys.exit(0)
