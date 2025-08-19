import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import date

# --- Constants ---
# Set your daily water goal in milliliters (e.g., 2000 mL = 2 Liters)
DAILY_GOAL = 2000  
# File to store the tracking data
DATA_FILE = "water_tracker_data.json"

# --- Main Application Class ---
class WaterTrackerApp:
    def __init__(self, root):
        """
        Initialize the main application window and its components.
        """
        self.root = root
        self.root.title("Water Intake Tracker")
        self.root.geometry("400x550")
        self.root.resizable(False, False) # Make window not resizable

        # --- Style Configuration ---
        # Explicitly setting colors to avoid issues with system themes (like macOS Dark Mode)
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') 

        # Define colors for a consistent look
        BG_COLOR = "#F0F8FF"      # AliceBlue
        TEXT_COLOR = "#212121"    # A dark gray for text
        ACCENT_COLOR = "#007ACC"   # A nice blue for highlights
        BUTTON_BG = "#FFFFFF"     # White background for buttons
        BUTTON_ACTIVE_BG = "#E0E0E0" # Light gray for when button is pressed

        self.root.configure(bg=BG_COLOR)
        
        # Configure styles for all widgets to ensure visibility
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 12))
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        self.style.configure("Amount.TLabel", font=("Helvetica", 28, "bold"), foreground=ACCENT_COLOR)
        self.style.configure("TButton", font=("Helvetica", 12), padding=10, background=BUTTON_BG, foreground=TEXT_COLOR)
        self.style.map("TButton", background=[('active', BUTTON_ACTIVE_BG)]) # Make button gray when clicked
        self.style.configure("TProgressbar", thickness=30, background=ACCENT_COLOR, troughcolor=BUTTON_BG)

        # --- Variables ---
        self.current_intake = tk.DoubleVar(value=0.0)

        # --- Load Data ---
        self.load_data()

        # --- UI Setup ---
        self.create_widgets()
        self.update_display()

    def load_data(self):
        """
        Loads water intake data from the JSON file.
        If the data is from a previous day, it resets the intake.
        """
        today = str(date.today())
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Check if the saved date is today
                if data.get("date") == today:
                    self.current_intake.set(data.get("intake", 0.0))
                else:
                    # It's a new day, so reset
                    self.current_intake.set(0.0)
                    self.save_data() # Save the reset state for the new day
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty, start fresh
            self.current_intake.set(0.0)

    def save_data(self):
        """
        Saves the current water intake and today's date to the JSON file.
        """
        data = {
            "date": str(date.today()),
            "intake": self.current_intake.get()
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

    def add_water(self, amount_ml):
        """
        Adds a specified amount of water to the current intake.
        
        Args:
            amount_ml (float): The amount of water to add in milliliters.
        """
        if self.current_intake.get() >= DAILY_GOAL:
            # Optionally, do nothing if goal is already met
            return 
            
        new_intake = self.current_intake.get() + amount_ml
        self.current_intake.set(new_intake)
        self.update_display()
        self.save_data()

        # Show a message when the goal is reached for the first time
        if new_intake >= DAILY_GOAL and (new_intake - amount_ml) < DAILY_GOAL:
            messagebox.showinfo("Goal Reached!", f"Congratulations! You've reached your daily goal of {DAILY_GOAL / 1000:.1f}L.")

    def reset_day(self):
        """
        Manually resets the daily water intake.
        """
        if messagebox.askyesno("Reset", "Are you sure you want to reset your intake for the day?"):
            self.current_intake.set(0.0)
            self.update_display()
            self.save_data()

    def update_display(self):
        """
        Updates all the UI elements to reflect the current intake amount.
        """
        intake_liters = self.current_intake.get() / 1000.0
        goal_liters = DAILY_GOAL / 1000.0
        
        # Update the main text display
        self.amount_label.config(text=f"{intake_liters:.2f} L / {goal_liters:.1f} L")
        
        # Update the progress bar
        progress_percentage = (self.current_intake.get() / DAILY_GOAL) * 100
        self.progress_bar['value'] = progress_percentage
        
        # Update the status label
        if self.current_intake.get() >= DAILY_GOAL:
            self.status_label.config(text="Goal Achieved! Keep it up!", foreground="#2E8B57") # SeaGreen
        else:
            remaining = DAILY_GOAL - self.current_intake.get()
            self.status_label.config(text=f"You need {remaining / 1000:.2f} L more.", foreground="#555555")

    def create_widgets(self):
        """
        Creates and arranges all the widgets in the main window.
        """
        # CORRECTED LINE: Removed commas from the padding string
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Header ---
        title_label = ttk.Label(main_frame, text="Today's Water Intake", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        # --- Amount Display ---
        self.amount_label = ttk.Label(main_frame, text="", style="Amount.TLabel")
        self.amount_label.pack(pady=(10, 20))

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", length=300)
        self.progress_bar.pack(pady=10, ipady=5) # ipady adds internal padding

        # --- Status Label ---
        self.status_label = ttk.Label(main_frame, text="", font=("Helvetica", 11, "italic"))
        self.status_label.pack(pady=(5, 25))
        
        # --- Buttons Frame ---
        buttons_frame = ttk.Frame(main_frame, style="TFrame")
        buttons_frame.pack(fill=tk.X, pady=10)
        buttons_frame.columnconfigure((0, 1), weight=1) # Make columns expand equally

        # --- Quick Add Buttons ---
        glass_button = ttk.Button(buttons_frame, text="Add Glass (250ml)", command=lambda: self.add_water(250))
        glass_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        bottle_button = ttk.Button(buttons_frame, text="Add Bottle (500ml)", command=lambda: self.add_water(500))
        bottle_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- Custom Amount Entry ---
        custom_frame = ttk.Frame(main_frame, style="TFrame")
        custom_frame.pack(fill=tk.X, pady=15)
        
        self.custom_entry = ttk.Entry(custom_frame, font=("Helvetica", 12), width=10)
        self.custom_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.custom_entry.insert(0, "Enter ml")
        
        custom_add_button = ttk.Button(custom_frame, text="Add Custom", command=self.add_custom_amount)
        custom_add_button.pack(side=tk.RIGHT)

        # --- Reset Button ---
        reset_button = ttk.Button(main_frame, text="Reset Day", command=self.reset_day)
        reset_button.pack(pady=(20, 0))

    def add_custom_amount(self):
        """
        Handles adding a custom amount from the entry field.
        """
        try:
            amount = float(self.custom_entry.get())
            if amount > 0:
                self.add_water(amount)
                self.custom_entry.delete(0, tk.END) # Clear entry after adding
                self.custom_entry.insert(0, "Enter ml")
                self.root.focus() # Remove focus from entry field
            else:
                messagebox.showwarning("Invalid Input", "Please enter a positive number.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the amount.")


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = WaterTrackerApp(root)
    root.mainloop()
