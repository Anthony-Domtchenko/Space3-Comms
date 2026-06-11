import serial
from wod_beacon_struct import *
from ax25 import *
import threading
import queue
import tkinter as tk
from tkinter import ttk
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


PORT = "COM4"
BAUD = 115200
BEACON_TIME_STRING_BYTES = 32   
CUBESAT_IDENTIFIER_BYTES = 6    
UART_SOF = 0x64     
BEACON_MSG_ID = 0x65        


RX_HEADER_BYTES = 3
RX_CRC_BYTES = 2

BEACON_TIME_STRING_BYTES = 32
CUBESAT_IDENTIFIER_BYTES = 6

data_queue = queue.Queue()

TELEMETRY_GROUPS = {
    "General": [
        "utc_time",
        "identifier"
    ],

    "EPS": [
        "rail_3v3_voltage",
        "rail_3v3_current_ch1",
        "rail_3v3_current_ch2",

        "rail_5v_voltage",
        "rail_5v_current_ch1",
        "rail_5v_current_ch2",

        "rail_6v_voltage",
        "rail_6v_current_ch1",
        "rail_6v_current_ch2",

        "rail_12v_voltage",
        "rail_12v_current_ch1",
        "rail_12v_current_ch2",

        "battery_voltage",
        "sys_voltage",
        "battery_current",

        "battery_temp",
        "mcu_temp",
        "charger_die_temp",

        "mppt1_voltage",
        "mppt2_voltage",

        "mppt1_current",
        "mppt2_current",

        "eFuse_states",
        "eFuse_faults"
    ],

    "ADCS": [
        "roll",
        "pitch",
        "yaw",

        "omega_x",
        "omega_y",
        "omega_z",

        "x_rw_speed",
        "y_rw_speed",
        "z_rw_speed",

        "x_mag_current",
        "y_mag_current",
        "z_mag_current",

        "x_mag_field_sense",
        "y_mag_field_sense",
        "z_mag_field_sense",
        "x_mag_field_filt",
        "y_mag_field_filt",
        "z_mag_field_filt",

        "sun_sense_1",
        "sun_sense_2",
        "sun_sense_3",
        "sun_sense_4",
        "sun_sense_5",
        "sun_sense_6",

        "detumble_scale"
    ],

    "Faults": [
        "EPS_Faults",
        "OBC_Faults",
        "ADCS_Faults",
        "Payload_Faults",
        "Comms_Faults",
        "Satellite_State"
    ]
}




def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF

    for b in data:
        crc ^= b << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return crc


def read_exact(ser: serial.Serial, n: int) -> bytes:
    data = ser.read(n)

    if len(data) != n:
        raise TimeoutError(f"Expected {n} bytes, got {len(data)}")

    return data


def read_packet(ser: serial.Serial):
    while True:
        b = ser.read(1)

        if not b:
            continue

        if b[0] == UART_SOF:
            break

    packet_id = read_exact(ser, 1)[0]
    length = read_exact(ser, 1)[0]

    payload = read_exact(ser, length)
    crc_bytes = read_exact(ser, 2)

    received_crc = crc_bytes[0] | (crc_bytes[1] << 8)

    header = bytes([UART_SOF, packet_id, length])
    calculated_crc = crc16_ccitt(header + payload)

    if received_crc != calculated_crc:
        raise ValueError(
            f"CRC mismatch: received 0x{received_crc:04X}, "
            f"calculated 0x{calculated_crc:04X}"
        )

    return packet_id, payload


def print_beacon(wod: BeaconPacket):
    print("-------------------------------------------------------")
    print("TIME:", wod.utc_time)
    print("IDENTIFIER:", wod.identifier)

    print("3V3 VOLTAGE:", wod.rail_3v3_voltage)
    print("3V3 CURRENT CH1:", wod.rail_3v3_current_ch1)
    print("3V3 CURRENT CH2:", wod.rail_3v3_current_ch2)

    print("5V VOLTAGE:", wod.rail_5v_voltage)
    print("5V CURRENT CH1:", wod.rail_5v_current_ch1)
    print("5V CURRENT CH2:", wod.rail_5v_current_ch2)

    print("6V VOLTAGE:", wod.rail_6v_voltage)
    print("6V CURRENT CH1:", wod.rail_6v_current_ch1)
    print("6V CURRENT CH2:", wod.rail_6v_current_ch2)

    print("12V VOLTAGE:", wod.rail_12v_voltage)
    print("12V CURRENT CH1:", wod.rail_12v_current_ch1)
    print("12V CURRENT CH2:", wod.rail_12v_current_ch2)

    print("BATTERY VOLTAGE:", wod.battery_voltage)
    print("SYSTEM VOLTAGE:", wod.sys_voltage)
    print("BATTERY CURRENT:", wod.battery_current)
    print("BATTERY TEMPERATURE:", wod.battery_temp)
    print("MCU TEMPERATURE:", wod.mcu_temp)
    print("CHARGER DIE TEMPERATURE:", wod.charger_die_temp)

    print("MPPT1 VOLTAGE:", wod.mppt1_voltage)
    print("MPPT2 VOLTAGE:", wod.mppt2_voltage)
    print("MPPT1 CURRENT:", wod.mppt1_current)
    print("MPPT2 CURRENT:", wod.mppt2_current)

    print("EFUSE STATES:", wod.eFuse_states)
    print("EFUSE FAULTS:", wod.eFuse_faults)

    print("ROLL:", wod.roll)
    print("PITCH:", wod.pitch)
    print("YAW:", wod.yaw)

    print("OMEGA X:", wod.omega_x)
    print("OMEGA Y:", wod.omega_y)
    print("OMEGA Z:", wod.omega_z)

    print("X REACTION WHEEL SPEED:", wod.x_rw_speed)
    print("Y REACTION WHEEL SPEED:", wod.y_rw_speed)
    print("Z REACTION WHEEL SPEED:", wod.z_rw_speed)

    print("X MAGNETORQUER CURRENT:", wod.x_mag_current)
    print("Y MAGNETORQUER CURRENT:", wod.y_mag_current)
    print("Z MAGNETORQUER CURRENT:", wod.z_mag_current)

    print("DETUMBLE SCALE:", wod.detumble_scale)

    print("EPS FAULTS:", wod.EPS_Faults)
    print("OBC FAULTS:", wod.OBC_Faults)
    print("ADCS FAULTS:", wod.ADCS_Faults)
    print("PAYLOAD FAULTS:", wod.Payload_Faults)
    print("COMMS FAULTS:", wod.Comms_Faults)

    print("-------------------------------------------------------")



# Serial Thread
def serial_worker():
    print(f"Opening {PORT} at {BAUD} baud")

    with serial.Serial(PORT, BAUD, timeout=1) as ser:

        while True:
            try:
                packet_id, payload = read_packet(ser)

                if packet_id != BEACON_MSG_ID:
                    continue

                print("Packet Received! Raw AX25 Bytes:")
                print(payload.hex(' '))
                decodedPacket = ax25decode(payload)
                wod = BeaconPacket.from_buffer_copy(decodedPacket.data)
                data_queue.put(wod)  # add WOD data to GUI queue

            except TimeoutError:
                continue

            except Exception as e:
                print(f"Packet error: {e}")



class TelemetryGUI:

    def __init__(self, root, data_queue):

        self.root = root
        self.data_queue = data_queue

        root.title("CubeSat Ground Station")
        root.geometry("1400x1000")

        #################################################
        # Statistics
        #################################################

        self.packet_count = 0

        #################################################
        # History Buffers
        #################################################

        self.sample_count = 0

        self.sample_history = deque(maxlen=100)

        # Roll/Pitch/Yaw

        self.roll_history = deque(maxlen=100)
        self.pitch_history = deque(maxlen=100)
        self.yaw_history = deque(maxlen=100)

        # Omega

        self.omega_x_history = deque(maxlen=100)
        self.omega_y_history = deque(maxlen=100)
        self.omega_z_history = deque(maxlen=100)

        # Reaction Wheels

        self.rw_x_history = deque(maxlen=100)
        self.rw_y_history = deque(maxlen=100)
        self.rw_z_history = deque(maxlen=100)

        #################################################
        # STATUS BAR
        #################################################

        self.status_frame = tk.Frame(
            root,
            relief="groove",
            borderwidth=2
        )

        self.status_frame.pack(
            fill="x",
            padx=5,
            pady=5
        )

        self.connection_var = tk.StringVar(
            value="Disconnected"
        )

        self.packet_var = tk.StringVar(
            value="Packets: 0"
        )

        self.last_packet_var = tk.StringVar(
            value="Last Packet: N/A"
        )

        tk.Label(
            self.status_frame,
            textvariable=self.connection_var
        ).pack(side="left", padx=10)

        tk.Label(
            self.status_frame,
            textvariable=self.packet_var
        ).pack(side="left", padx=10)

        tk.Label(
            self.status_frame,
            textvariable=self.last_packet_var
        ).pack(side="left", padx=10)

        #################################################
        # NOTEBOOK
        #################################################

        self.notebook = ttk.Notebook(root)

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        #################################################
        # TELEMETRY TAB
        #################################################

        self.telemetry_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.telemetry_tab,
            text="Telemetry"
        )

        #################################################
        # TREEVIEW + SCROLLBAR
        #################################################

        tree_container = tk.Frame(
            self.telemetry_tab
        )

        tree_container.pack(
            fill="both",
            expand=True
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=("value",),
            show="tree headings"
        )

        self.tree.heading(
            "#0",
            text="Parameter"
        )

        self.tree.heading(
            "value",
            text="Value"
        )

        self.tree.column(
            "#0",
            width=350
        )

        self.tree.column(
            "value",
            width=200
        )

        scrollbar = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.build_tree()

        #################################################
        # ADCS TAB
        #################################################

        self.adcs_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.adcs_tab,
            text="ADCS"
        )

        #################################################
        # ADCS FIGURE
        #################################################

        self.figure = Figure(
            figsize=(12, 10),
            dpi=100
        )

        self.roll_ax = self.figure.add_subplot(511)
        self.pitch_ax = self.figure.add_subplot(512)
        self.yaw_ax = self.figure.add_subplot(513)
        self.omega_ax = self.figure.add_subplot(514)
        self.rw_ax = self.figure.add_subplot(515)

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.adcs_tab
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        #################################################
        # START GUI UPDATE LOOP
        #################################################

        self.update_gui()

    #####################################################
    # TREE CREATION
    #####################################################

    def build_tree(self):

        for group_name, field_list in TELEMETRY_GROUPS.items():

            group_id = self.tree.insert(
                "",
                "end",
                text=group_name,
                open=True
            )

            for field_name in field_list:

                self.tree.insert(
                    group_id,
                    "end",
                    iid=field_name,
                    text=field_name.replace("_", " ").upper(),
                    values=("---",)
                )

    #####################################################
    # VALUE FORMATTING
    #####################################################

    def format_value(self, field_name, value):

        try:

            if "voltage" in field_name:
                return f"{value:.3f} V"

            elif "current" in field_name:
                return f"{value:.3f} A"

            elif "temp" in field_name:
                return f"{value:.1f} °C"

            elif field_name in [
                "roll",
                "pitch",
                "yaw"
            ]:
                return f"{value:.2f} rad"

            elif "omega" in field_name:
                return f"{value:.2f} RPM"

            elif "rw_speed" in field_name:
                return f"{value:.2f} RPS"
            
            elif "field" in field_name:
                return f"{value:.2f} uT"

            elif "Faults" in field_name:
                return f"0x{value:04X}"
            
            elif "sun_sense" in field_name:
                return f"{value:.3f} V"

            elif field_name in [
                "eFuse_states",
                "eFuse_faults"
            ]:
                return f"0x{value:02X}"

            return str(value)

        except Exception:
            return str(value)

    #####################################################
    # UPDATE TELEMETRY VALUES
    #####################################################

    def update_rows(self, wod):

        self.packet_count += 1

        self.connection_var.set(
            "Connected"
        )

        self.packet_var.set(
            f"Packets: {self.packet_count}"
        )

        self.last_packet_var.set(
            f"Last Packet: {wod.utc_time}"
        )

        for field_list in TELEMETRY_GROUPS.values():

            for field_name in field_list:

                try:

                    value = getattr(
                        wod,
                        field_name
                    )

                    self.tree.item(
                        field_name,
                        values=(
                            self.format_value(
                                field_name,
                                value
                            ),
                        )
                    )

                except AttributeError:
                    pass

        #
        # Store history
        #

        self.sample_count += 1

        self.sample_history.append(
            self.sample_count
        )

        self.roll_history.append(wod.roll)
        self.pitch_history.append(wod.pitch)
        self.yaw_history.append(wod.yaw)

        self.omega_x_history.append(wod.omega_x)
        self.omega_y_history.append(wod.omega_y)
        self.omega_z_history.append(wod.omega_z)

        self.rw_x_history.append(wod.x_rw_speed)
        self.rw_y_history.append(wod.y_rw_speed)
        self.rw_z_history.append(wod.z_rw_speed)

    #####################################################
    # UPDATE PLOTS
    #####################################################

    def update_plot(self):

        #
        # Roll
        #

        self.roll_ax.clear()

        self.roll_ax.plot(
            self.sample_history,
            self.roll_history
        )

        self.roll_ax.set_title(
            "Roll (Rad)"
        )

        self.roll_ax.grid(True)

        #
        # Pitch
        #

        self.pitch_ax.clear()

        self.pitch_ax.plot(
            self.sample_history,
            self.pitch_history
        )

        self.pitch_ax.set_title(
            "Pitch (Rad)"
        )

        self.pitch_ax.grid(True)

        #
        # Yaw
        #

        self.yaw_ax.clear()

        self.yaw_ax.plot(
            self.sample_history,
            self.yaw_history
        )

        self.yaw_ax.set_title(
            "Yaw (Rad)"
        )

        self.yaw_ax.grid(True)

        #
        # Omega XYZ
        #

        self.omega_ax.clear()

        self.omega_ax.plot(
            self.sample_history,
            self.omega_x_history,
            label="X"
        )

        self.omega_ax.plot(
            self.sample_history,
            self.omega_y_history,
            label="Y"
        )

        self.omega_ax.plot(
            self.sample_history,
            self.omega_z_history,
            label="Z"
        )

        self.omega_ax.set_title(
            "Body Rates (RPM)"
        )

        self.omega_ax.legend()

        self.omega_ax.grid(True)

        #
        # Reaction Wheels
        #

        self.rw_ax.clear()

        self.rw_ax.plot(
            self.sample_history,
            self.rw_x_history,
            label="RW X"
        )

        self.rw_ax.plot(
            self.sample_history,
            self.rw_y_history,
            label="RW Y"
        )

        self.rw_ax.plot(
            self.sample_history,
            self.rw_z_history,
            label="RW Z"
        )

        self.rw_ax.set_title(
            "Reaction Wheel Speed (RPS)"
        )

        self.rw_ax.legend()

        self.rw_ax.grid(True)

        self.figure.tight_layout()

        self.canvas.draw()

    #####################################################
    # MAIN UPDATE LOOP
    #####################################################

    def update_gui(self):

        updated = False

        while not self.data_queue.empty():

            wod = self.data_queue.get()

            self.update_rows(wod)

            updated = True

        if updated:
            self.update_plot()

        self.root.after(
            100,
            self.update_gui
        )



def main():

    serial_thread = threading.Thread(
        target=serial_worker,
        daemon=True
    )

    serial_thread.start()

    root = tk.Tk()

    gui = TelemetryGUI(
        root,
        data_queue
    )

    root.mainloop()
    

if __name__ == "__main__":
    main()