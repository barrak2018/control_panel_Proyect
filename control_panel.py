import sys
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QPushButton,
)
from serial_engine import Serial_Engine


class COM_module(QWidget):
    def __init__(self, serial_engine:Serial_Engine):
        super().__init__()

        self.serial = serial_engine
        #signals
        self.serial.connection_status.connect(self.conection_status_update_protocol)
        
        self.current_port = None
        ports_list = self.serial.get_list_ports()
        self.ports = ["None"]
        for port in ports_list:
            self.ports.append(port)
            
        self.port_combobox = QComboBox()
        self.port_combobox.addItems(self.ports)
        self.port_combobox.currentTextChanged.connect(self.update_current_port)

        self.connect_button = QPushButton()
        self.connect_button.setText("0/1")
        self.connect_button.setCheckable(True)
        self.connect_button.released.connect(self.connection_start)
        

        layout = QHBoxLayout()
        layout.addWidget(self.port_combobox)
        layout.addWidget(self.connect_button)
        
        self.setLayout(layout)
    
    def update_current_port(self, port):
        self.current_port = port

    def connection_start (self):
        
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
            print("no hice nada")
    def conection_status_update_protocol(self, status:bool):
        if not status: 
            self.desconection_protocol()
            print("conection_status_update_protocol Activado")


            
    def desconection_protocol(self):
        self.serial.disconnect_port()
        self.connect_button.setChecked(False)

            






class ServoControl(QWidget):
    pass
    

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