# 🧠 PEDro Research Monitor & Notifier

This Python script automates the process of checking for new research records on the [PEDro database](https://pedro.org.au/) based on pre-defined search URLs. If new studies are found, it notifies a list of subscribers via email.

---

## 📦 Features

- ✅ Headless browsing with Selenium
- ✅ Avoids duplicate URL checks
- ✅ Tracks record counts from previous runs
- ✅ Sends email notifications if new research is published
- ✅ Allows for future expansion (add/remove subscribers or tracking URLs)

---

## 🛠️ Setup Instructions

1. **Install Requirements**
```bash
pip install selenium
```
2. Environment Variables
Set the following environment variables before running the script:
SENDER_EMAIL – your Gmail address
EMAIL_PASSWORD – Gmail App Password (not your Gmail login)

Example:
export SENDER_EMAIL="youremail@gmail.com"
export EMAIL_PASSWORD="yourapppassword"

3. How It Works
URLs to track and subscribers are hard-coded in load_data().
Script fetches the number of research records found for each search.
Record counts are stored in records_counts.json.
If the count increases, subscribers receive an email notification.
Uses one headless ChromeDriver session for efficiency.

*************************
✉️ Email Format
Sample email content:

🧠 PEDro update for: Lumbar spine, SIJ or pelvis
📈 Numbers of new records: 2
🔗 URL:
https://search.pedro.org.au/advanced-search/results?...  
*************************

📌 Notes
Duplicates in url_list are automatically removed.
You can expand load_data() to load from files or databases.
Errors during scraping are caught and logged.

🔄 Future Improvements
✅ Add/remove subscribers dynamically 
✅ Add/remove tracked URLs dynamically
🔄 Web UI or CLI tool
🔄 Scheduling via cron job or Windows Task Scheduler
