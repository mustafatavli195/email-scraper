# Email Scraper & Sender Tool 📧✉️

A Python-based tool that **scrapes websites for emails** and **sends automated emails** using a customizable template. Built on top of the original open-source Email Scraper project by [AdrianTomin](https://github.com/AdrianTomin), with additional features for automated mail campaigns.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

---

## Features ✨

### Original Features

- **Recursive scraping**: Follows links on web pages to visit multiple pages for thorough email extraction.
- **Email extraction**: Uses regular expressions to find and collect email addresses.
- **Easy to use**: Just enter a URL, and the tool will start scraping.

### New Features Added

- **Automated email sending**: Send emails directly from the tool using SMTP (Gmail, Outlook, etc.).
- **Template support**: Use placeholders like `{name}`, `{position}`, and `{sender_name}` in subject and body for personalized emails.
- **Attachment support**: Attach PDF or CV files to your emails.
- **CSV import**: Load recipient lists from CSV files or paste them manually.
- **Delay & break control**: Set minimum delays between emails and automated breaks to reduce risk of being flagged as spam.
- **Logging & reports**: Track email delivery status and save detailed reports automatically.
- **Test email feature**: Send a test email to yourself before launching a full campaign.

---

## Requirements 🛠️

- `python 3.x`
- `requests` – For web scraping.
- `beautifulsoup4` – For HTML parsing.
- `lxml` – HTML parser for BeautifulSoup.
- `tkinter` – For GUI (usually included in standard Python).

---

## Installation Guide 📝

### 1. Clone the repository:

```bash
git clone https://github.com/yourusername/email-scraper-sender.git
cd email-scraper-sender
```

### 2. Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate
```

> On Windows: `venv\Scripts\activate`

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present yet, generate it:

```bash
pip freeze > requirements.txt
```

### 4. Run the tool:

```bash
python email_sender_app.py
```

---

## Example Usage 🖥️

### Scraping Emails:

```
[+] Enter URL to scan: https://example.com
[1] Processing https://example.com
[2] Processing https://example.com/contact
Found emails:
info@example.com
support@example.com
```

### Sending Emails:

- Fill in **sender credentials** (email & password), **subject**, and **message template**.
- Load **recipients from CSV** or paste manually.
- Choose **attachment** (optional).
- Click **Send Test** or **Send All**.

---

## Badges

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

---

## Authors

- Original: [@AdrianTomin](https://www.github.com/AdrianTomin)
- Contributed Enhancements: [@YourUsername](https://www.github.com/yourgithub)
