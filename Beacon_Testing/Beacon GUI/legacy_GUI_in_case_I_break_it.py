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