import serial
from serial.tools import list_ports

from PyQt6.QtCore import pyqtSignal, QObject



class Serial_Engine(QObject):
    connection_status = pyqtSignal(bool, str)
    error = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.current_port = None
        self.connection = None
        self.isConnected = False
        

    def get_list_ports (self):
        ports = list_ports.comports()
        res = []
        for port in ports:
            res.append(port.device)
        return res

    def connect_port(self, port:str, baud:int = 9600 ):
        if self.connection and self.connection.is_open:
            self.connection.close()

            print(f"SerialEngine: Cerrando coneccion con puerto {self.current_port}")

        try:
            self.connection = serial.Serial(port, baud)
            if not self.connection.is_open:
                self.connection.open()
            self.current_port = port
            self.isConnected = True

            print(f"SerialEngine: Conectado al puerto {self.current_port}")

            self.connection_status.emit(True, self.current_port)

        except serial.SerialException as err:

            print(f"SerialEngine: error de Conexion \"{err}\"")

            self.error.emit(f"Error de Conexion \"{err}\"")
            self.isConnected = False
            self.connection_status.emit(False, "")

    def disconnect_port(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"SerialEngine: Desconectado del puerto {self.current_port}")
            self.isConnected = False
            self.connection_status.emit(False, "")
    
    def send(self, data: str):
        if self.connection and self.connection.is_open:
            try:
                self.connection.write(data.encode())
                print(f"SerialEngine: Enviado \"{data}\" al puerto {self.current_port}")
            except serial.SerialException as err:
                print(f"SerialEngine: error al enviar datos \"{err}\"")
                self.error.emit(f"Error al enviar datos \"{err}\"")
        else:
            print("SerialEngine: No hay conexion activa para enviar datos")
            self.error.emit("No hay conexion activa para enviar datos")



if __name__ == "__main__":
    engine = Serial_Engine()
    print(engine.get_list_ports())
    engine.connect_port("COM3", 9600)
    print(engine.isConnected)
    engine.send("Hello, Serial Port!")
    engine.disconnect_port()