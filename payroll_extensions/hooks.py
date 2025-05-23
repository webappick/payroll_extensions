app_name = "payroll_extensions"
app_title = "Payroll Extensions"
app_publisher = "Your Name"
app_description = "Auto-calculate late entry/early exits"
app_email = "your@email.com"
app_license = "MIT"

has_website_theme = 0

doc_events = {
    "Salary Slip": {
        "on_submit": "payroll_extensions.salary_hooks.calculate_all_metrics"
    }
}
