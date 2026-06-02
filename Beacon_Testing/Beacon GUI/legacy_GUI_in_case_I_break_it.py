class TelemetryGUI:

    def __init__(self, root, data_queue):

        self.root = root
        self.data_queue = data_queue

        root.title("CubeSat Telemetry")
        root.geometry("1200x900")

        ##################################################
        # Statistics
        ##################################################

        self.packet_count = 0

        ##################################################
        # History Buffers
        ##################################################

        self.sample_count = 0

        self.sample_history = deque(maxlen=100)

        self.roll_history = deque(maxlen=100)
        self.pitch_history = deque(maxlen=100)
        self.yaw_history = deque(maxlen=100)

        ##################################################
        # Frames
        ##################################################

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

        self.tree_frame = tk.Frame(root)

        self.tree_frame.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.plot_frame = tk.Frame(
            root,
            relief="groove",
            borderwidth=2
        )

        self.plot_frame.pack(
            fill="both",
            expand=False,
            padx=5,
            pady=5
        )

        ##################################################
        # Status Bar
        ##################################################

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

        ##################################################
        # Treeview
        ##################################################

        self.tree = ttk.Treeview(
            self.tree_frame,
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

        self.tree.pack(
            fill="both",
            expand=True
        )

        self.build_tree()

        ##################################################
        # Plot
        ##################################################

        self.figure = Figure(
            figsize=(10, 3),
            dpi=100
        )

        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(
            "Roll / Pitch / Yaw History"
        )

        self.ax.set_xlabel(
            "Packet Number"
        )

        self.ax.set_ylabel(
            "Degrees"
        )

        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.plot_frame
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        ##################################################
        # Start Update Loop
        ##################################################

        self.update_gui()

    ######################################################
    # Tree Construction
    ######################################################

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

    ######################################################
    # Value Formatting
    ######################################################

    def format_value(self, field_name, value):

        try:

            if "voltage" in field_name:
                return f"{value:.3f} V"

            elif "current" in field_name:
                return f"{value:.3f} A"

            elif "temp" in field_name:
                return f"{value:.1f} °C"

            elif field_name in ["roll", "pitch", "yaw"]:
                return f"{value:.2f}°"

            elif "omega" in field_name:
                return f"{value:.2f} RPM"

            elif "rw_speed" in field_name:
                return f"{value:.2f} RPS"

            elif field_name == "detumble_scale":
                return f"{value:.3f}"

            elif field_name in [
                "eFuse_states",
                "eFuse_faults"
            ]:
                return f"0x{value:02X}"

            elif "Faults" in field_name:
                return f"0x{value:04X}"

            else:
                return str(value)

        except Exception:
            return str(value)

    ######################################################
    # Update Telemetry
    ######################################################

    def update_rows(self, wod):

        self.packet_count += 1

        self.packet_var.set(
            f"Packets: {self.packet_count}"
        )

        self.last_packet_var.set(
            f"Last Packet: {wod.utc_time}"
        )

        self.connection_var.set(
            "Connected"
        )

        for field_list in TELEMETRY_GROUPS.values():

            for field_name in field_list:

                try:

                    value = getattr(
                        wod,
                        field_name
                    )

                    display_value = self.format_value(
                        field_name,
                        value
                    )

                    self.tree.item(
                        field_name,
                        values=(display_value,)
                    )

                except AttributeError:

                    self.tree.item(
                        field_name,
                        values=("N/A",)
                    )

        ##################################################
        # Update History Buffers
        ##################################################

        self.sample_count += 1

        self.sample_history.append(
            self.sample_count
        )

        self.roll_history.append(
            wod.roll
        )

        self.pitch_history.append(
            wod.pitch
        )

        self.yaw_history.append(
            wod.yaw
        )

    ######################################################
    # Update Plot
    ######################################################

    def update_plot(self):

        self.ax.clear()

        self.ax.plot(
            self.sample_history,
            self.roll_history,
            label="Roll"
        )

        self.ax.plot(
            self.sample_history,
            self.pitch_history,
            label="Pitch"
        )

        self.ax.plot(
            self.sample_history,
            self.yaw_history,
            label="Yaw"
        )

        self.ax.set_title(
            "Roll / Pitch / Yaw History"
        )

        self.ax.set_xlabel(
            "Packet Number"
        )

        self.ax.set_ylabel(
            "Degrees"
        )

        self.ax.grid(True)

        self.ax.legend()

        self.canvas.draw()

    ######################################################
    # Main GUI Update Loop
    ######################################################

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