import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import webbrowser

from geopy.geocoders import Nominatim

# Load Dataset
try:
    df = pd.read_csv("colleges.csv")  # Ensure your dataset file is named "colleges.csv"
except FileNotFoundError:
    messagebox.showerror("File Error", "Dataset file 'colleges.csv' not found!")
    exit()

# API Key for Google Maps (optional)
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your API key

# List of all Indian states (28 states and 8 Union Territories)
indian_states = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
    "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", 
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi", "Puducherry", 
    "Ladakh", "Lakshadweep", "Jammu and Kashmir"
]
indian_states.sort()

# Helper Function to Update Programs
def update_programs(event):
    """Update program dropdown based on selected course."""
    selected_course = course_dropdown.get()
    if selected_course:
        # Get the unique programs related to the selected course from the dataset
        programs = df[df["Course"] == selected_course]["Program Offered"].unique().tolist()
        program_dropdown["values"] = programs
        if programs:
            program_dropdown.set(programs[0])  # Set the first available program as default
        else:
            program_dropdown.set('')
    else:
        program_dropdown.set('')
def toggle_hostel():
    """Toggle the Hostel Only filter."""
    hostel_filter.set(not hostel_filter.get())
    hostel_button.config(
        text="Hostel: Yes" if hostel_filter.get() else "Hostel: No",
        bg="green" if hostel_filter.get() else "#23272a"
    )

def toggle_scholarship():
    """Toggle the Scholarship Only filter."""
    scholarship_filter.set(not scholarship_filter.get())
    scholarship_button.config(
        text="Scholarship: Yes" if scholarship_filter.get() else "Scholarship: No",
        bg="green" if scholarship_filter.get() else "#23272a"
    )       

# Helper Function to Filter Colleges
def filter_colleges():
    """Filter colleges based on user input, including course and program."""
    state = state_dropdown.get()
    course = course_dropdown.get()
    program = program_dropdown.get()  # Selected program
    fee_limit = fee_var.get()
    hostel_only = hostel_filter.get()
    scholarship_only = scholarship_filter.get()
    student_marks = marks_var.get()


   

    if not state:
        messagebox.showwarning("Input Error", "Please select State.")
        return
    if  not course:
        messagebox.showwarning("Input Error", "Please select Course.")
        return
    if not program:
        messagebox.showwarning("Input Error","Please select Program.")
        return
         # Validate the student's academic performance input
    try:
        student_marks = float(student_marks)
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter Percentage(%).")
        return
    if student_marks>100:
        messagebox.showwarning("Input Error","Please enter a valid percentage(%).")
        return
    # Apply fee limit filter
    #if fee_limit:
    try:
        fee_limit = int(fee_limit)
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid fee amount.")
        return
    # Filter colleges based on the selected filters
    filtered = df[(df["State"] == state) & (df["Course"] == course)]

    # Apply program filter
    if program:
        filtered = filtered[filtered["Program Offered"] == program]
    

    # Apply hostel filter
    if hostel_only:
        filtered = filtered[filtered["Hostel"].str.strip().str.lower() == "yes"]
        print("After hostel filter:", filtered)

    if scholarship_only:
        filtered = filtered[filtered["Scholarship"].str.strip().str.lower() == "yes"]
        print("After scholarship filter:", filtered)
    filtered = filtered[(filtered["Min Marks"] <= student_marks) & (filtered["Fees"] <= fee_limit)]

    # Filter based on academic performance
    filtered = filtered[filtered["Min Marks"] <= student_marks]
    # Apply fees filter
    #if fee_limit:
    filtered = filtered[filtered["Fees"] <= fee_limit]
    # Update the table with filtered data
    if filtered.empty:
        messagebox.showinfo("No Results", "No colleges found based on the selected filters.")
    else:
        update_table(filtered)

def update_table(filtered_df):
    """Update the results table with filtered data."""
    for row in table.get_children():
        table.delete(row)
    for _, row in filtered_df.iterrows():
        table.insert("", "end", values=(row["State"], row["Course"], row["College"], row["Fees"], row["Rating"], row["College Type"], row["Min Marks"],row["Website"]))
    apply_tags()

# Helper Function to Show College on Map
def show_on_map():
    """Open the selected college's location on OpenStreetMap."""
    selected = table.focus()
    if selected:
        college = table.item(selected, "values")[2]  # Get the college name from the table
        state = state_dropdown.get()
        address = f"{college}, {state}, India"
        
        print(f"Selected College: {college}")  # Debug: Print selected college name
        
        # Use Nominatim API to get coordinates
        geolocator = Nominatim(user_agent="college_map_app")
        location = geolocator.geocode(address)

        if location:
            # Open the location in OpenStreetMap (OSM)
            url = f"https://www.openstreetmap.org/?mlat={location.latitude}&mlon={location.longitude}#map=15/{location.latitude}/{location.longitude}"
            webbrowser.open(url)
        elif "Raj Kumar Goel Institute of Technology" in college:  # Use a partial match for college name
            url = f"https://www.openstreetmap.org/search?lat=28.699606&lon=77.443611#map=19/28.699606/77.443611"
            webbrowser.open(url)
        else:
            messagebox.showerror("Error", "Unable to find the college location on the map.")
    else:
        messagebox.showwarning("No Selection", "Please select a college to view on the map.")
def bookmark_college():
    """Bookmark the selected college."""
    selected = table.focus()
    if selected:
        college = table.item(selected, "values")[2]
        bookmarks.append(college)
        messagebox.showinfo("Success", f"{college} has been added to your bookmarks!")
    else:
        messagebox.showwarning("No Selection", "Please select a college to bookmark.")

def view_bookmarks():
    """View bookmarked colleges."""
    if not bookmarks:
        messagebox.showinfo("Bookmarks", "No colleges bookmarked yet.")
        return
    bookmark_window = tk.Toplevel(root)
    bookmark_window.title("Bookmarked Colleges")
    tk.Label(bookmark_window, text="Your Bookmarked Colleges:", font=("Arial", 14)).pack(pady=10)
    for college in bookmarks:
        tk.Label(bookmark_window, text=college, font=("Arial", 12)).pack()

# Helper Function to Reset All Fields
def reset_fields():
    """Reset all input fields and filters."""
    state_dropdown.set('')  # Reset State dropdown
    course_dropdown.set('')  # Reset Course dropdown
    program_dropdown.set('')  # Reset Program dropdown
    marks_var.set('')  # Reset Marks input field
    fee_var.set('')  # Reset Fee input field
    hostel_var.set('')  # Reset Hostel checkbox
    scholarship_var.set('')  # Reset Scholarship checkbox
   # Clear the table
    for row in table.get_children():
        table.delete(row)
def open_website(event):
    """Open the website link in the browser."""
    item = table.selection()
    if item:
        website = table.item(item, "values")[7]  # Get the website column value
        if website:
            webbrowser.open(website)
        else:
            messagebox.showwarning("No Website", "No website found for this college.")

# GUI Setup
root = tk.Tk()
root.title("College Recommendation System")
root.geometry("1020x760")
root.config(bg="#2c2f33")


# Header
header = tk.Label(root, text="College Recommendation System", font=("Comic Sans", 24, "bold"), bg="#7289da", fg="white", pady=10)
header.pack(fill="x")

# Filters Frame
filters_frame = tk.Frame(root, bg="#23272a", pady=10)
filters_frame.pack(fill="x", padx=20)

# Dropdowns
courses = [course.replace(',', '') for course in df["Course"].unique()]

tk.Label(filters_frame, text="State:", bg="#23272a", fg="white" ,font="30").grid(row=0, column=0, padx=5, pady=5)
state_dropdown = ttk.Combobox(filters_frame, values=indian_states)
state_dropdown.grid(row=0, column=1, padx=5, pady=5)

tk.Label(filters_frame, text="Course:", bg="#23272a", fg="white" ,font="30").grid(row=0, column=2, padx=5, pady=5)
course_dropdown = ttk.Combobox(filters_frame, values=courses)
course_dropdown.grid(row=0, column=3, padx=5, pady=5)

# Add Event Binding to Course Dropdown to Update Program
course_dropdown.bind("<<ComboboxSelected>>", update_programs)

tk.Label(filters_frame, text="Program:", bg="#23272a", fg="white",font="30").grid(row=1, column=0, padx=5, pady=5)
program_dropdown = ttk.Combobox(filters_frame)
program_dropdown.grid(row=1, column=1, padx=5, pady=5)

# Student's Academic Performance Input (Marks)
tk.Label(filters_frame, text="Percentage(%):", bg="#23272a", fg="white",font="30").grid(row=1, column=2, padx=5, pady=5)
marks_var = tk.StringVar()
marks_entry = tk.Entry(filters_frame, textvariable=marks_var)
marks_entry.grid(row=1, column=3, padx=5, pady=5)

# Fees Input
tk.Label(filters_frame, text="Max Fees:", bg="#23272a", fg="white",font="30").grid(row=1, column=4, padx=5, pady=5)
fee_var = tk.StringVar()
fee_entry = tk.Entry(filters_frame, textvariable=fee_var)
fee_entry.grid(row=1, column=5, padx=5, pady=5)

# Additional Filters (Hostel and Scholarship checkboxes)
#hostel_var = tk.BooleanVar()
#scholarship_var = tk.BooleanVar()
# Toggle Button States
hostel_filter = tk.BooleanVar(value=False)  # Correctly define hostel_filter
scholarship_filter = tk.BooleanVar(value=False)  # Correctly define scholarship_filter


# Toggle Buttons
hostel_button = tk.Button(
    filters_frame, text="Hostel: Yes", bg="#23272a", fg="white", command=toggle_hostel
)
hostel_button.grid(row=2, column=0, padx=5, pady=5)

scholarship_button = tk.Button(
    filters_frame, text="Scholarship: No", bg="#23272a", fg="white", command=toggle_scholarship
)
scholarship_button.grid(row=2, column=1, padx=5, pady=5)

# Filter Button and Reset Button
filter_button = tk.Button(filters_frame, text="Filter Colleges",font="20", command=filter_colleges, bg="#7289da", fg="white")
filter_button.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

reset_button = tk.Button(filters_frame, text="Reset",font="20",  command=reset_fields, bg="#7289da", fg="white")
reset_button.grid(row=2, column=3, columnspan=2, padx=10, pady=10)

# Apply custom styles to Treeview
style = ttk.Style()
style.configure("Treeview", rowheight=30, font=("Arial", 12))  # Increase font size and row height
style.map("Treeview", background=[("selected", "lightblue")])  # Highlight selected row

# Define columns, including a new column for Website
table_frame = tk.Frame(root, bg="#2c2f33")
table_frame.pack(fill="both", expand=True, padx=20, pady=20)
table = ttk.Treeview(
    table_frame,
    columns=("State", "Course", "College", "Fees", "Rating", "College Type", "Criteria(%)", "Website"),
    show="headings",
    style="Treeview",
)
table.heading("State", text="State")
table.heading("Course", text="Course")
table.heading("College", text="College")
table.heading("Fees", text="Fees")
table.heading("Rating", text="Rating")
table.heading("College Type", text="College Type")
table.heading("Criteria(%)",text="Criteria(%)")
table.heading("Website",text="Website")

table.column("State", width=90)
table.column("Course", width=80)
table.column("College", width=240)
table.column("Fees", width=80)
table.column("Rating", width=50)
table.column("College Type", width=90)
table.column("Criteria(%)",width=30)
table.column("Website", width=130)

table.pack(fill="both", expand=True)

# Hover effect for Treeview
def on_hover(event):
    row_id = table.identify_row(event.y)
    for row in table.get_children():
        table.tag_configure(row, background="white")  # Reset all row colors
    if row_id:
        table.tag_configure(row_id, background="dodgerblue")  # Change the hovered row color

def on_leave(event):
    for row in table.get_children():
        table.tag_configure(row, background="white")  # Reset all row colors when leaving

# Apply tags to rows for hover effect
def apply_tags():
    for row in table.get_children():
        table.item(row, tags=(row,))

apply_tags()  # Apply tags initially
table.bind("<Motion>", on_hover)
table.bind("<Leave>", on_leave)


# Bind the website column to the open_website function
table.bind("<Double-1>", open_website)

# Bookmarks
bookmarks = []
bookmark_btn = tk.Button(root, text="Bookmark College", command=bookmark_college, bg="#99aab5", fg="black")
bookmark_btn.pack(side="left", padx=20, pady=10)

view_bookmark_btn = tk.Button(root, text="View Bookmarks", command=view_bookmarks, bg="#7289da", fg="white")
view_bookmark_btn.pack(side="right", padx=20, pady=10)

# Map Button
map_btn = tk.Button(root, text="View on Map", command=show_on_map, bg="#43b581", fg="white")
map_btn.pack(side="right", padx=20, pady=10)

root.mainloop()


