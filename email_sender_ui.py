import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import smtplib
import ssl
import csv
import os
import mimetypes
import time
import random
from email.message import EmailMessage
from collections import UserDict


class SafeDict(UserDict):
    def __missing__(self, key):
        return ""


class EmailSenderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("automatic mail sending")
        self.geometry("850x750")

        self.default_smtp = "smtp.gmail.com"
        self.default_port = 587

        self.recipients = []
        self.attachment_path = ""
        self.report = []  #  Sending Report

        # Automatic mail report direcrtory
        self.report_dir = os.path.join(os.getcwd(), "reports")
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

        self._build_ui()

    # ------------------ UI ------------------
    def _build_ui(self):
        pad = 6
        frm_sender = ttk.LabelFrame(self, text="Sender (Account Settings)")
        frm_sender.pack(fill="x", padx=pad, pady=pad)

        ttk.Label(frm_sender, text="E-mail:").grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        self.entry_email = ttk.Entry(frm_sender, width=35)
        self.entry_email.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(frm_sender, text="Password:").grid(
            row=0, column=2, sticky="w", padx=4, pady=4
        )
        self.entry_password = ttk.Entry(frm_sender, width=25, show="*")
        self.entry_password.grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(frm_sender, text="SMTP Server:").grid(
            row=1, column=0, sticky="w", padx=4, pady=4
        )
        self.entry_smtp = ttk.Entry(frm_sender, width=25)
        self.entry_smtp.insert(0, self.default_smtp)
        self.entry_smtp.grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(frm_sender, text="Port:").grid(
            row=1, column=2, sticky="w", padx=4, pady=4
        )
        self.entry_port = ttk.Entry(frm_sender, width=8)
        self.entry_port.insert(0, str(self.default_port))
        self.entry_port.grid(row=1, column=3, sticky="w", padx=4, pady=4)

        frm_attach = ttk.LabelFrame(self, text="Ek (CV / PDF)")
        frm_attach.pack(fill="x", padx=pad, pady=pad)
        self.lbl_attach = ttk.Label(frm_attach, text="No file selected yet")
        self.lbl_attach.grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(frm_attach, text="Choose CSV", command=self.choose_attachment).grid(
            row=0, column=1, padx=4, pady=4
        )

        frm_rcpt = ttk.LabelFrame(self, text="Recipients (CSV or Paste)")
        frm_rcpt.pack(fill="both", expand=True, padx=pad, pady=pad)

        ttk.Button(frm_rcpt, text="load CSV", command=self.load_csv).grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        ttk.Button(
            frm_rcpt, text="Read from Text", command=self.parse_recipients_from_text
        ).grid(row=0, column=1, sticky="w", padx=4, pady=4)
        ttk.Label(
            frm_rcpt,
            text="(CSV: columns such as email, name or email addresses below each other)",
        ).grid(row=0, column=2, columnspan=3, sticky="w", padx=4, pady=4)

        self.txt_recipients = scrolledtext.ScrolledText(frm_rcpt, height=8)
        self.txt_recipients.grid(
            row=1, column=0, columnspan=5, sticky="nsew", padx=4, pady=4
        )
        frm_rcpt.rowconfigure(1, weight=1)
        frm_rcpt.columnconfigure(4, weight=1)

        frm_msg = ttk.LabelFrame(self, text="Message & Template")
        frm_msg.pack(fill="both", expand=True, padx=pad, pady=pad)

        ttk.Label(frm_msg, text="Subject:").grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        self.entry_subject = ttk.Entry(frm_msg)
        self.entry_subject.insert(0, "Example - {position}")
        self.entry_subject.grid(
            row=0, column=1, columnspan=4, sticky="we", padx=4, pady=4
        )

        ttk.Label(frm_msg, text="Message (example: Hello {name}, ...) :").grid(
            row=1, column=0, sticky="nw", padx=4, pady=4
        )
        self.txt_body = scrolledtext.ScrolledText(frm_msg, height=8)
        sample_body = "Hello {name},\n\nI would like to apply for the open {position} position in your company. My CV is attached.\n\nGood day,\n{sender_name}"
        self.txt_body.insert("1.0", sample_body)
        self.txt_body.grid(row=1, column=1, columnspan=4, sticky="nsew", padx=4, pady=4)
        frm_msg.columnconfigure(3, weight=1)

        frm_ctrl = ttk.Frame(self)
        frm_ctrl.pack(fill="x", padx=pad, pady=pad)

        ttk.Button(
            frm_ctrl, text="Send Test (To Myself)", command=self.send_test_email
        ).pack(side="left", padx=6)
        ttk.Button(frm_ctrl, text="Send All", command=self.start_send_thread).pack(
            side="left", padx=6
        )

        ttk.Label(frm_ctrl, text="(Min. sec between each email):").pack(
            side="left", padx=6
        )
        self.entry_delay = ttk.Entry(frm_ctrl, width=6)
        self.entry_delay.insert(0, "10")
        self.entry_delay.pack(side="left", padx=4)

        ttk.Label(frm_ctrl, text="(How many emails does a break take):").pack(
            side="left", padx=6
        )
        self.entry_break_every = ttk.Entry(frm_ctrl, width=6)
        self.entry_break_every.insert(0, "20")
        self.entry_break_every.pack(side="left", padx=4)

        ttk.Label(frm_ctrl, text="Break interval (min):").pack(side="left", padx=6)
        self.entry_break_min = ttk.Entry(frm_ctrl, width=4)
        self.entry_break_min.insert(0, "10")
        self.entry_break_min.pack(side="left", padx=2)
        self.entry_break_max = ttk.Entry(frm_ctrl, width=4)
        self.entry_break_max.insert(0, "15")
        self.entry_break_max.pack(side="left", padx=2)

        frm_log = ttk.LabelFrame(self, text="Status")
        frm_log.pack(fill="both", expand=True, padx=pad, pady=pad)
        self.progress = ttk.Progressbar(
            frm_log, orient="horizontal", mode="determinate"
        )
        self.progress.pack(fill="x", padx=4, pady=4)
        self.txt_log = scrolledtext.ScrolledText(frm_log, height=12)
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)

    # ------------------ Reciever ------------------
    def choose_attachment(self):
        path = filedialog.askopenfilename(
            title="Choose CSV",
            filetypes=[("PDF files", "*.pdf"), ("All Files", "*")],
        )
        if path:
            self.attachment_path = path
            self.lbl_attach.config(text=os.path.basename(path))
            self.log(f"Plugin selected: {path}")

    def load_csv(self):
        path = filedialog.askopenfilename(
            title="Choose CSV",
            filetypes=[("CSV files", "*.csv"), ("All Files", "*")],
        )
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = []
                if reader.fieldnames:
                    for r in reader:
                        r2 = {
                            k.strip(): v.strip() for k, v in r.items() if k is not None
                        }
                        if not any(k.lower() == "email" for k in r2.keys()):
                            first_val = next(iter(r2.values()), None)
                            r2 = {"email": first_val, **r2}
                        rows.append(r2)
                else:
                    csvfile.seek(0)
                    for line in csvfile:
                        email = line.strip()
                        if email:
                            rows.append({"email": email})
            self.recipients = [r for r in rows if r.get("email")]
            self.txt_recipients.delete("1.0", tk.END)
            for r in self.recipients:
                self.txt_recipients.insert(tk.END, r.get("email") + "\n")
            self.log(f"CSV loaded: {len(self.recipients)} reciever founded")
        except Exception as e:
            self.log(f"CSV loading error: {e}")
            messagebox.showerror("Hata", f"CSV could not be read: {e}")

    def parse_recipients_from_text(self):
        text = self.txt_recipients.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo(
                "Information", "Enter recipient addresses or upload CSV."
            )
            return
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        rows = []
        for line in lines:
            if "," in line:
                parts = [p.strip() for p in line.split(",")]
                rows.append(
                    {"email": parts[0], "name": parts[1] if len(parts) > 1 else ""}
                )
            else:
                rows.append({"email": line})
        self.recipients = rows
        self.log(f"Metinden {len(rows)} recipient read")

    # ------------------ Send ------------------
    def start_send_thread(self):
        if not self.recipients:
            messagebox.showwarning("Warning", "Recipient list is empty")
            return
        t = threading.Thread(target=self.send_all_emails, daemon=True)
        t.start()

    def send_test_email(self):
        sender = self.entry_email.get().strip()
        if not sender:
            messagebox.showwarning("Warning", "Enter sender email")
            return
        test_row = {
            "email": sender,
            "name": "Test Reciever",
            "position": "Test Position",
            "sender_name": sender,
        }
        t = threading.Thread(
            target=self._send_single, args=(test_row, True), daemon=True
        )
        t.start()

    def send_all_emails(self):
        sender = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        smtp = self.entry_smtp.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except Exception:
            messagebox.showerror("Hata", "Port is not allowed")
            return

        try:
            min_delay = float(self.entry_delay.get().strip())
        except Exception:
            min_delay = 10

        try:
            break_every = int(self.entry_break_every.get().strip())
        except Exception:
            break_every = 20

        try:
            break_min = int(self.entry_break_min.get().strip())
            break_max = int(self.entry_break_max.get().strip())
        except Exception:
            break_min, break_max = 10, 15

        if not sender or not password:
            messagebox.showwarning("Warning", "Enter sender and password")
            return
        if not self.attachment_path:
            proceed = messagebox.askyesno("Warning", "CV not selected. Send?")
            if not proceed:
                return

        total = len(self.recipients)
        self._set_progress_max(total)
        self.report = []

        try:
            if port == 465:
                server = smtplib.SMTP_SSL(
                    smtp, port, context=ssl.create_default_context()
                )
            else:
                server = smtplib.SMTP(smtp, port, timeout=20)
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            server.login(sender, password)
        except Exception as e:
            self.log(f"SMTP Connection Error: {e}")
            messagebox.showerror("Error", f"SMTP Connection Error: {e}")
            return

        sent = 0
        try:
            for idx, r in enumerate(self.recipients, start=1):
                status = "SUCCESS"
                error_msg = ""
                try:
                    self._send_message_via_server(server, sender, r)
                    sent += 1
                    self.log(f"Successful: {r.get('email')}")
                except Exception as e:
                    status = "FAILED"
                    error_msg = str(e)
                    self.log(f"Hata ({r.get('email')}): {e}")
                self.report.append(
                    {
                        "email": r.get("email"),
                        "status": status,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "error_message": error_msg,
                    }
                )
                self._update_progress(idx)

                # Dinamik bekleme ve mola
                if break_every > 0 and idx % break_every == 0:
                    pause = random.randint(break_min * 60, break_max * 60)
                    self.log(f"{idx} mail sent, {pause//60} min break started...")
                    remaining = pause
                    while remaining > 0:
                        mins, secs = divmod(remaining, 60)
                        self.log(f"End of break: {mins} dk {secs:02d} sn")
                        step = min(10, remaining)
                        time.sleep(step)
                        remaining -= step
                else:
                    pause = random.uniform(min_delay, min_delay * 2)
                    self.log(f"Delay: {pause:.1f} sn")
                    time.sleep(pause)
        finally:
            try:
                server.quit()
            except Exception:
                pass
            self.log(f"Transaction completed. Success: {sent}, Total: {total}")
            self.save_report_automatic()

    def _send_single(self, row, is_test=False):
        sender = self.entry_email.get().strip()
        password = self.entry_password.get().strip()
        smtp = self.entry_smtp.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except Exception:
            port = self.default_port
        try:
            if port == 465:
                server = smtplib.SMTP_SSL(
                    smtp, port, context=ssl.create_default_context()
                )
            else:
                server = smtplib.SMTP(smtp, port, timeout=20)
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            server.login(sender, password)
            self._send_message_via_server(server, sender, row)
            server.quit()
            self.log(f"Test message sent: {row.get('email')}")
            if is_test:
                messagebox.showinfo("Successful", "Test message sent.")
        except Exception as e:
            self.log(f"Test submission error: {e}")
            messagebox.showerror("Error", f"Sending error: {e}")

    def _send_message_via_server(self, server, sender, row):
        subject = self.entry_subject.get()
        body = self.txt_body.get("1.0", tk.END)
        mapped = SafeDict(row)
        mapped.setdefault("sender_name", sender)
        subj = subject.format_map(mapped)
        bod = body.format_map(mapped)

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = row.get("email")
        msg["Subject"] = subj
        msg.set_content(bod)

        if self.attachment_path and os.path.exists(self.attachment_path):
            ctype, encoding = mimetypes.guess_type(self.attachment_path)
            if ctype is None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            with open(self.attachment_path, "rb") as f:
                data = f.read()
            msg.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(self.attachment_path),
            )

        server.send_message(msg)

    # ------------------ Report & Log ------------------
    def save_report_automatic(self):
        if not self.report:
            return
        filename = f"transfer_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        path = os.path.join(self.report_dir, filename)
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["email", "status", "timestamp", "error_message"]
                )
                writer.writeheader()
                writer.writerows(self.report)
            self.log(f"Delivery report automatically saved: {path}")
        except Exception as e:
            self.log(f"Failed to save delivery report: {e}")

    def log(self, text):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.txt_log.insert(tk.END, f"[{ts}] {text}\n")
        self.txt_log.see(tk.END)

    def _set_progress_max(self, total):
        self.progress["maximum"] = total
        self.progress["value"] = 0

    def _update_progress(self, value):
        self.progress["value"] = value

if __name__ == "__main__":
    app = EmailSenderApp()
    app.mainloop()
