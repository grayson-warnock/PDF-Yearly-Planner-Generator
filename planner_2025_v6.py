from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import calendar
import datetime

year = 2025

# Set Sunday as the first day of the week
cal = calendar.TextCalendar(calendar.SUNDAY)

# Create a canvas for the PDF
c = canvas.Canvas("planner.pdf", pagesize=letter)
width, height = letter

# ----------------------------
# Page 1: Yearly Planner with 2025 Calendar (Shifted to the Right)
# ----------------------------
c.bookmarkPage("yearly")
c.setFont("Helvetica", 24)
c.drawCentredString(width / 2, height - 50, f"Yearly Planner - {year}")

# Use a monospaced font for the calendar grid
c.setFont("Courier", 8)

# Adjust margins to move the months further to the right
margin_x = 120  # Further increased left margin to shift right
margin_bottom = 40
calendar_top_y = height - 80
available_height = calendar_top_y - margin_bottom
rows = 4
cols = 3
cell_height = available_height / rows
cell_width = (width - margin_x - 40) / cols  # Increased spacing between months

# Loop over all 12 months to draw each month in its grid cell
for m in range(1, 13):
    col = (m - 1) % cols
    row = (m - 1) // cols
    cell_x = margin_x + col * cell_width
    cell_top_y = calendar_top_y - row * cell_height

    month_str = cal.formatmonth(year, m)
    lines = month_str.splitlines()
    
    line_height = 10
    current_y = cell_top_y - line_height
    for line in lines:
        c.drawString(cell_x, current_y, line)
        current_y -= line_height

    # Make the entire cell clickable to go to the corresponding monthly page
    c.linkRect("", f"monthly_{m}", (cell_x, cell_top_y - cell_height, cell_x + cell_width, cell_top_y))

c.showPage()  # End Yearly Planner Page

# ----------------------------
# Pages 2-13: Monthly Planner Pages (Now With Days of the Week and Weekly Links)
# ----------------------------
month_to_week = {}
for m in range(1, 13):
    c.bookmarkPage(f"monthly_{m}")
    c.setFont("Helvetica", 24)
    month_name = calendar.month_name[m]
    c.drawCentredString(width / 2, height - 50, f"Monthly Planner - {month_name} {year}")

    # Define calendar grid parameters
    weeks = cal.monthdayscalendar(year, m)  # Get weeks, starting with Sunday
    grid_margin = 80  # Shift right to accommodate week numbers
    grid_top = height - 100  # Space below the title
    cell_w = (width - grid_margin - 50) / 7
    cell_h = 30

    # Draw Days of the Week Labels
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    c.setFont("Helvetica-Bold", 12)
    for i, day in enumerate(days_of_week):
        x = grid_margin + i * cell_w
        c.drawString(x + (cell_w / 4), grid_top, day)

    # Move grid down slightly to accommodate labels
    grid_top -= 20

    # Draw the monthly calendar grid with week numbers
    c.setFont("Helvetica", 10)
    for week_index, week in enumerate(weeks):
        first_valid_day = next((d for d in week if d != 0), None)
        if first_valid_day:
            week_number = datetime.date(year, m, first_valid_day).isocalendar()[1]
            month_to_week[week_number] = m
        else:
            week_number = "?"

        week_x = grid_margin - 30
        week_y = grid_top - week_index * cell_h
        c.drawString(week_x, week_y - cell_h / 2 + 4, f"W{week_number}")
        c.linkRect("", f"weekly_{week_number}", (week_x - 5, week_y - cell_h, week_x + 20, week_y))

        for weekday, day in enumerate(week):
            if day == 0:
                continue  # Skip empty days

            cell_x = grid_margin + weekday * cell_w
            cell_y = grid_top - week_index * cell_h
            day_str = str(day)

            # Draw a box around the day
            c.rect(cell_x, cell_y - cell_h, cell_w, cell_h)

            # Draw the day number centered in the box
            text_width = c.stringWidth(day_str, "Helvetica", 10)
            c.drawString(cell_x + (cell_w - text_width) / 2, cell_y - cell_h / 2 + 4, day_str)

            # Add clickable link to corresponding daily page
            c.linkRect("", f"daily_{m}_{day}", (cell_x, cell_y - cell_h, cell_x + cell_w, cell_y))
    
  # Navigation Links on Monthly Page:
    c.setFont("Helvetica", 12)
    back_year_text = "Back to Yearly Planner"
    tw = c.stringWidth(back_year_text, "Helvetica", 12)
    x = 50
    y = 30
    c.drawString(x, y, back_year_text)
    c.linkRect("", "yearly", (x, y, x + tw, y + 12))
  
    c.showPage()  # End monthly page

# ----------------------------
# Daily Planner Pages
# ----------------------------
for m in range(1, 13):
    for day in range(1, 32):  # Max 31 days in a month
        try:
            datetime.date(year, m, day)  # Validate date
        except ValueError:
            continue  # Skip invalid dates

        c.bookmarkPage(f"daily_{m}_{day}")
        c.setFont("Helvetica", 24)
        c.drawCentredString(width / 2, height - 50, f"Daily Planner - {calendar.month_name[m]} {day}, {year}")
        
        back_month_text = "Back to Monthly Planner"
        tw = c.stringWidth(back_month_text, "Helvetica", 12)
        x = 50
        y = 30
        c.setFont("Helvetica", 12)
        c.drawString(x, y, back_month_text)
        c.linkRect("", f"monthly_{m}", (x, y, x + tw, y + 12))
        
        c.showPage()  # End daily page

# ----------------------------
# Weekly Planner Pages with Structured Layout, Notes, and Navigation
# ----------------------------
for week in range(1, 54):
    c.bookmarkPage(f"weekly_{week}")
    c.setFont("Helvetica", 24)
    c.drawCentredString(width / 2, height - 50, f"Weekly Planner - Week {week}, {year}")
    
    # Add structured layout for weekly planning
    c.setFont("Helvetica-Bold", 14)
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    start_y = height - 100
    box_height = 60
    
    for i, day in enumerate(days):
        y = start_y - i * (box_height + 10)
        c.drawString(50, y, day)
        c.rect(50, y - box_height, width - 100, box_height)
    
    # Navigation Links
    c.setFont("Helvetica", 12)
    if week in month_to_week:
        back_month = month_to_week[week]
        back_month_text = "Back to Monthly Planner"
        tw = c.stringWidth(back_month_text, "Helvetica", 12)
        x = 50
        y = 15
        c.drawString(x, y, back_month_text)
        c.linkRect("", f"monthly_{back_month}", (x, y, x + tw, y + 12))
    
    c.showPage()  # End weekly page

c.save()
