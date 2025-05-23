import frappe
from frappe.utils import get_time, get_datetime, add_to_date, add_days

def calculate_all_metrics(doc, method=None):
    frappe.log_error("✅ Hook triggered", doc.name)

    employee = doc.employee
    start_date = doc.start_date
    end_date = doc.end_date

    late_seconds = 0
    early_seconds = 0
    extended_leaves = 0
    threshold_time = get_time("10:00:00")
    threshold_hours = 9

    attendance = frappe.get_all("Attendance", filters={
        "employee": employee,
        "attendance_date": ["between", [start_date, end_date]]
    }, fields=["attendance_date", "in_time", "out_time", "status"])

    for a in attendance:
        if a.in_time:
            in_time = get_time(a.in_time)
            if in_time > threshold_time:
                late_seconds += (
                    (in_time.hour * 3600 + in_time.minute * 60 + in_time.second)
                    - (threshold_time.hour * 3600 + threshold_time.minute * 60 + threshold_time.second)
                )
        if a.in_time:
            in_time_dt = get_datetime(a.in_time)
            if a.out_time:
                out_time_dt = get_datetime(a.out_time)
                expected_out = add_to_date(in_time_dt, hours=threshold_hours)
                if out_time_dt < expected_out:
                    early_seconds += (expected_out - out_time_dt).total_seconds()
            else:
                early_seconds += 1800

    holidays = frappe.get_all("Holiday", filters={
        "holiday_date": ["between", [start_date, end_date]]
    }, fields=["holiday_date"])
    holiday_dates = [h.holiday_date for h in holidays]
    weekly_off_days = [5, 6]

    absences = [a for a in attendance if a.status == "Absent"]
    for a in absences:
        absence_date = a.attendance_date
        before = add_days(absence_date, -1)
        after = add_days(absence_date, 1)
        if (
            before in holiday_dates or after in holiday_dates
            or before.weekday() in weekly_off_days
            or after.weekday() in weekly_off_days
        ):
            extended_leaves += 0.5

    doc.custom_late_entries = int(late_seconds)
    doc.custom_early_exits = int(early_seconds)
    doc.custom_extended_leaves = extended_leaves

    frappe.log_error("✅ Values Set", f"Late: {doc.custom_late_entries}, Early: {doc.custom_early_exits}, Leave: {doc.custom_extended_leaves}")