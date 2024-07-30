import tkinter as tk
from tkinter import ttk
from datetime import datetime
import csv
import os
from collections import deque

# Global variables to store the last entry for undo functionality and last 10 entries
last_entry = None
last_entries = deque(maxlen=10)  # Keeps track of the last 10 entries
duplicate_message = None  # Global variable for duplicate entry message

def submit_data(event=None):
    global last_entry, duplicate_message
    
    bib = bib_entry.get().strip()
    comment = comment_entry.get().strip() or "NONE"  # Use "NONE" if comment is empty

    if not bib:
        return  # Do nothing if the bib field is empty

    location = location_var.get().split('_')[0]  # Extract the first two letters
    status = status_var.get()
    timestamp = datetime.now().strftime('%H%M')
    day = datetime.now().day

    # Check for duplicates
    file_exists = os.path.isfile('data_entries.csv')
    if file_exists:
        with open('data_entries.csv', mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if row[0] == bib and row[1] == status:
                    duplicate_message = f"Duplicate Entry for Bib {bib} {status}."
                    update_result_label()
                    return
    
    # Clear the duplicate message if present
    duplicate_message = None

    # Save the last entry before adding the new one
    last_entry = [bib, status, timestamp, day, location, comment]
    last_entries.append(last_entry)

    # Save to the CSV file
    with open('data_entries.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Bib', 'Status', 'Timestamp', 'Day', 'Location', 'Comment'])
        writer.writerow(last_entry)

    # Update the result label
    update_result_label()

    # Clear the entry fields
    bib_entry.delete(0, tk.END)
    status_var.set("IN")
    comment_entry.delete(0, tk.END)  # Clear the comment entry

    # Check if the submit button should be disabled
    check_bib_entry()

def undo_last_entry():
    global last_entry
    if last_entry:
        # Check if the file exists and is not empty
        if os.path.isfile('data_entries.csv') and os.path.getsize('data_entries.csv') > 0:
            # Read all entries except the last one
            with open('data_entries.csv', mode='r') as file:
                lines = file.readlines()
            
            # Remove the last line (the most recent entry)
            with open('data_entries.csv', mode='w') as file:
                if len(lines) > 1:
                    file.writelines(lines[:-1])
                else:
                    # If there's only one line, just clear the file
                    open('data_entries.csv', 'w').close()

            # Remove the last entry from the list
            if last_entries:
                last_entries.pop()
            
            # Clear the last entry
            last_entry = None

            # Update the result label
            update_result_label()
        else:
            result_label.config(state=tk.NORMAL)
            result_label.delete(1.0, tk.END)
            result_label.insert(tk.END, "No entries to undo.")
            result_label.config(state=tk.DISABLED)

def update_result_label():
    global duplicate_message
    
    display_text = ""
    
    # Add the duplicate message if present
    if duplicate_message:
        display_text += f"{duplicate_message}\n"
    
    # Add recent entries
    for entry in reversed(last_entries):
        display_text += f"Bib: {entry[0]}, Status: {entry[1]}, Timestamp: {entry[2]}, Comment: {entry[5]}\n"
    
    if not display_text:
        display_text = "No entries available."

    result_label.config(state=tk.NORMAL)  # Enable editing to update text
    result_label.delete(1.0, tk.END)  # Clear the text widget
    result_label.insert(tk.END, display_text.strip())
    result_label.config(state=tk.DISABLED)  # Disable editing again

def check_bib_entry(event=None):
    if bib_entry.get().strip():
        submit_button.config(state=tk.NORMAL)
        root.bind('<Return>', submit_data)
    else:
        submit_button.config(state=tk.DISABLED)
        root.unbind('<Return>')

def handle_tab(event): #focus tab to comment from bib
    if event.widget == bib_entry:
        comment_entry.focus_set()
        return "break"  # Prevent the default tab behavior

# Create the main window
root = tk.Tk()
root.title("Data Entry Form")

# Create and place the labels and entry fields
tk.Label(root, text="Bib:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
bib_entry = ttk.Entry(root)
bib_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
bib_entry.bind('<KeyRelease>', check_bib_entry)  # Check bib entry on every key release
bib_entry.bind('<Tab>', handle_tab)  # Handle Tab key to move focus to Comment

tk.Label(root, text="Location:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
location_options = [
    "MM_Marble Mountain SnoPark", "BL_Blue Lake", "AC_Ape Canyon", "WR_Windy Ridge",
    "JR_Johnston Ridge", "CW_Coldwater Lake", "NP_Norway Pass", "EP_Elk Pass",
    "WM_Wright Meadow (Rd.9327)", "SB_Spencer Butte", "LR_Lewis River", "QR_Quartz Ridge",
    "CB_Council Bluff", "CH_Chain of Lakes", "KT_Klickitat", "TS_Twin Sisters",
    "OC_Owens Creek", "FN_Finish Line"
]
location_var = tk.StringVar(value=location_options[0])
location_menu = ttk.Combobox(root, textvariable=location_var, values=location_options, state="readonly")
location_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Status:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
status_var = tk.StringVar(value="IN")  # Default to "IN"

# Create a frame to contain the status radio buttons
status_frame = tk.Frame(root)
status_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="w")

# Place the radio buttons inside the frame
in_radio = ttk.Radiobutton(status_frame, text="IN", variable=status_var, value="IN")
in_radio.pack(side=tk.LEFT, padx=(0, 10))  # Add padding to the right for spacing
out_radio = ttk.Radiobutton(status_frame, text="OUT", variable=status_var, value="OUT")
out_radio.pack(side=tk.LEFT, padx=(0, 10))  # Add padding to the right for spacing
drop_radio = ttk.Radiobutton(status_frame, text="DROP", variable=status_var, value="DROP")
drop_radio.pack(side=tk.LEFT)

# Adjust the column weights to make sure the radio buttons are centered
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

tk.Label(root, text="Comment:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
comment_entry = ttk.Entry(root)
comment_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

# Create and place the submit button
submit_button = ttk.Button(root, text="Submit", command=submit_data)
submit_button.grid(row=4, column=0, columnspan=3, pady=10)
submit_button.config(state=tk.DISABLED)  # Initially disabled

# Create and place the undo button
undo_button = ttk.Button(root, text="Undo Last", command=undo_last_entry)
undo_button.grid(row=5, column=0, columnspan=3, pady=10)

# Label to display the result
result_label = tk.Text(root, height=10, width=80, wrap=tk.WORD, state=tk.DISABLED)
result_label.grid(row=6, column=0, columnspan=3, pady=10)

# Set initial focus on the bib_entry field
bib_entry.focus_set()

# Run the application
root.mainloop()
