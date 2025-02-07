import customtkinter as ctk
import pandas as pd
import os
import datetime
import webbrowser
from PIL import Image as PILImage, ImageTk, Image
import sys

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_x = int((screen_width - width) / 2)
    position_y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{position_x}+{position_y}")

def toggle_theme():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("Light")
    else:
        ctk.set_appearance_mode("Dark")

# Set initial theme to dark
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


root = ctk.CTk()
window_width = 1280
window_height = 720



# Center the main window
center_window(root, window_width, window_height)

# Credentials
correct_username = "admin"
correct_password = "letmein"

# Frame config
frame = ctk.CTkFrame(master=root, fg_color="white")
frame.place(relx=0, rely=0, relwidth=0.4, relheight=1.0)

# Grid settings for frame (widgets)
frame.grid_rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], weight=1)
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=0)
frame.grid_columnconfigure(2, weight=1)

user_roll_no = ""
master_file_path = "studentsdata.xlsx"  # Update this to the path of your master file

def open_popup(title, message):
    popup = ctk.CTkToplevel(root)
    popup.title(title)

    label = ctk.CTkLabel(popup, text=message)
    label.pack(pady=20)

    def close_popup():
        popup.destroy()

    button_ok = ctk.CTkButton(popup, text="OK", command=close_popup)
    button_ok.pack(pady=10)

    # Bind the Enter key to the close_popup function
    popup.bind('<Return>', lambda event: close_popup())

    center_window(popup, 400, 200)
    popup.grab_set()
    root.wait_window(popup)



def check_master_file():
    global master_file_path

    # Search for Excel files in the current directory
    excel_files = [f for f in os.listdir() if f.endswith(('.xlsx', '.xls'))]

    if not excel_files:
        open_popup("File Missing", "No Excel file found in the app directory. Please add a master file.")
        return False

    # Set the first found file as the master file
    master_file_path = excel_files[0]
    return True
def process_latecomers():
    if not check_master_file():
        return

    # Load the master file
    master_df = pd.read_excel(master_file_path)

    # Normalize column names: remove spaces and convert to lowercase
    normalized_columns = {col.lower().replace(' ', ''): col for col in master_df.columns}

    required_columns = ['name', 'rollno', 'dept', 'year']

    # Check if all required columns are present
    missing_columns = [col for col in required_columns if col not in normalized_columns]
    if missing_columns:
        open_popup("File Error", f"Master file is missing required columns: {', '.join(missing_columns)}")
        return

    # Retrieve the original column names dictionary
    name_col = normalized_columns['name']
    rollno_col = normalized_columns['rollno']
    dept_col = normalized_columns['dept']
    year_col = normalized_columns['year']

    # Create a folder for latecomers if it doesn't exist
    latecomers_folder = os.path.join(os.path.expanduser("~"), "Documents", "Late Comer Entry")
    if not os.path.exists(latecomers_folder):
        os.makedirs(latecomers_folder)

    current_date = datetime.date.today().strftime("%Y-%m-%d")
    latecomers_file = os.path.join(latecomers_folder, f"{current_date}.csv")

    # Check if the latecomers file already exists
    if not os.path.isfile(latecomers_file):
        latecomers_df = pd.DataFrame(columns=["Name", "Roll No", "Dept", "Year", "Entry Time"])
    else:
        latecomers_df = pd.read_csv(latecomers_file)

    # Assume 'user_roll_no' is used to simulate the roll number for late entry
    if user_roll_no:
        student_info = master_df[master_df[rollno_col] == user_roll_no]

        if not student_info.empty:
            name = student_info.iloc[0][name_col]
            dept = student_info.iloc[0][dept_col]  # Fetch the department
            year = student_info.iloc[0][year_col]  # Fetch the year
            entry_time = datetime.datetime.now().strftime("%H:%M:%S")

            # Add the new entry to the DataFrame
            new_entry = pd.DataFrame([[name, user_roll_no, dept, year, entry_time]],
                                     columns=["Name", "Roll No", "Dept", "Year", "Entry Time"])
            latecomers_df = pd.concat([latecomers_df, new_entry], ignore_index=True)

            # Save the updated DataFrame to the CSV file
            latecomers_df.to_csv(latecomers_file, index=False)

            # Show popup to confirm entry
            open_popup("Entry Recorded", f"Late entry recorded for \n \n {name}.")
        else:
            open_popup("Invalid Roll No", "Roll number not found in the master file.")
def open_new_page():
    new_page = ctk.CTk()  # Create a new full-screen window
    new_page.geometry(f"{window_width}x{window_height}")
    new_page.title("New Page")

    # Disable the window close button
    new_page.protocol("WM_DELETE_WINDOW", lambda: None)



    welcome_label = ctk.CTkLabel(new_page, text="Enter Your Roll No", font=("Century Gothic", 30, "bold"))
    welcome_label.pack(pady=120)

    rollno_entry = ctk.CTkEntry(new_page, placeholder_text="Roll No", font=("Century Gothic", 30), height=50, width=200)
    rollno_entry.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.2
    )
    
    


    theme_switch = ctk.CTkSwitch(new_page, text="Change theme", command=toggle_theme)
    theme_switch.place(relx=0.98, rely=0.02, anchor="ne")

    def submit_entry():
        global user_roll_no
        user_roll_no = rollno_entry.get().upper()  # Convert roll number to uppercase
        rollno_entry.delete(0, ctk.END)  # Clear the entry after submission
        if check_master_file():
            process_latecomers()

    submit_button = ctk.CTkButton(new_page, text="Submit", font=("Century Gothic", 24), command=submit_entry)
    submit_button.place(
        relx=0.5,
        rely=0.6,
        anchor="center",
        relwidth=0.2
    )

    def show_credits():
        def on_link_click(event):
            webbrowser.open("https://github.com/lokifr")
        

        popup = ctk.CTkToplevel(root)
        popup.title("Credits")

        label_text = "Designed & Developed by Lokesh"
        link_text = "GitHub Page"
        

        # Credits text label
        label = ctk.CTkLabel(popup, text=label_text, font=("Century Gothic", 14))
        label.pack(pady=10)

        # GitHub hyperlink label
        link_label_github = ctk.CTkLabel(popup, text=link_text, font=("Century Gothic", 14), cursor="hand2", text_color="blue")
        link_label_github.pack(pady=10)

        # Insta hyperlink label
        link_label_insta = ctk.CTkLabel(popup, text=link_text_insta, font=("Century Gothic", 14), cursor="hand2", text_color="blue")
        link_label_insta.pack(pady=10)

        # Bind the link label click events
        link_label_github.bind("<Button-1>", on_link_click)
        link_label_insta.bind("<Button-1>", on_link_click2)

        # Center the popup
        center_window(popup, 300, 150)

        popup.grab_set()
        root.wait_window(popup)

    credits_button = ctk.CTkButton(new_page, text="i", font=("Century Gothic", 18), command=show_credits,
                                   corner_radius=20, height=40, width=40)
    credits_button.place(relx=0.02, rely=0.98, anchor="sw")

    def logout():
        def confirm_logout():
            new_page.destroy()  # Close the new page
            root.deiconify()  # Show the main window
            root.quit()  # Terminate the application

        def cancel_logout():
            logout_popup.destroy()  # Close the confirmation popupmaster

        logout_popup = ctk.CTkToplevel(new_page)
        logout_popup.title("Confirm Logout")

        label = ctk.CTkLabel(logout_popup, text="Are you sure you want to logout?")
        label.pack(pady=20)

        yes_button = ctk.CTkButton(logout_popup, text="Yes", command=confirm_logout)
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(logout_popup, text="No", command=cancel_logout)
        no_button.pack(side="right", padx=10)

        center_window(logout_popup, 350, 150)
        logout_popup.grab_set()
        new_page.wait_window(logout_popup)

    logout_button = ctk.CTkButton(new_page, text="Logout", font=("Century Gothic", 12), command=logout,
                                  corner_radius=10, height=30, width=100)
    logout_button.place(
        relx=0.98,  # Near the right edge
        rely=0.98,  # Near the bottom edge
        anchor="se"  # South-East anchor for bottom-right placement
    )

    # Bind Enter key to submit roll number
    new_page.bind('<Return>', lambda event: submit_entry())
    # Load and resize the image using Pillow

    new_page.mainloop()


# Widgets size
entry_width = 300
entry_height = 40
button_height = 40

usname = ctk.CTkEntry(frame, placeholder_text="Username", height=entry_height, width=entry_width,
                      corner_radius=20, font=("Century Gothic", 14))
usname.grid(row=8, column=1, padx=10, pady=10)

passwd = ctk.CTkEntry(frame, placeholder_text="Password", height=entry_height, width=entry_width, show="*",
                      corner_radius=20, font=("Century Gothic", 14))
passwd.grid(row=9, column=1, padx=10, pady=10)

def login():
    if usname.get() == correct_username and passwd.get() == correct_password:
        root.withdraw()  # Hide the main window
        open_new_page()  # Open the new full-screen window
    else:
        open_popup("Login Failed", "Incorrect username or password. Please try again.")

button = ctk.CTkButton(frame, text="Login", command=login, height=button_height, width=entry_width,
                       corner_radius=20, font=("Century Gothic", 14))
button.grid(row=11, column=1, padx=10, pady=10)

label = ctk.CTkLabel(frame, text="Welcome Back!!", height=50, width=entry_width,
                     font=("Century Gothic", 30, "bold"), text_color="black")
label.grid(row=5, column=1)

pil_image = PILImage.open(resource_path("logo.png"))
new_size = (300, 300)  # Adjust the size as needed
pil_image = pil_image.resize(new_size, PILImage.LANCZOS)


image_tk = ImageTk.PhotoImage(pil_image)

# Create the CTkLabel with the resized image
image_label = ctk.CTkLabel(frame, image=image_tk, text="")  # text="" to avoid any text overlay
image_label.grid(row=3, column=1, padx=10, pady=10)


image_label.image = image_tk

from PIL import Image as PILImage, ImageTk
import customtkinter as ctk

# Load and resize the image using Pillow
pil_imagebro = PILImage.open(resource_path("bro.png"))
new_sizebro = (700, 700)  # Adjust the size as needed
pil_imagebro = pil_imagebro.resize(new_sizebro, PILImage.LANCZOS)


image_tkbro = ImageTk.PhotoImage(pil_imagebro)


image_labelbro = ctk.CTkLabel(root, image=image_tkbro, text="")

# Center the image label on the screen
image_labelbro.place(relx=0.7, rely=0.5, anchor="center")


image_labelbro.image = image_tkbro


# Bind Enter key for the login page
root.bind('<Return>', lambda event: login())

root.mainloop()

