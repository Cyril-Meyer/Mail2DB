import hashlib
import pathlib
import sqlite3
import zipfile


class EmailDB:
    def __init__(self,
                 db_filename='mail.db',
                 attachments_filename='mail_attach.zip',
                 init=True):
        if not db_filename.endswith('.db'):
            db_filename = db_filename + '.db'
        if not attachments_filename.endswith('.zip'):
            attachments_filename = attachments_filename + '.zip'
        # SQLite DB
        self.conn = sqlite3.connect(db_filename)
        self.cursor = self.conn.cursor()
        if init:
            self.init_database()
        # ZIP attachments archive
        self.zip = zipfile.ZipFile(attachments_filename, 'w', zipfile.ZIP_DEFLATED)

    def init_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            sender TEXT,
            date TIMESTAMP,
            body TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            FOREIGN KEY (email_id) REFERENCES emails (id)
        )
        ''')

        self.conn.commit()

    def add_email(self, subject, sender, date, body):
        self.cursor.execute('''
        INSERT INTO emails (subject, sender, date, body)
        VALUES (?, ?, ?, ?)
        ''', (subject, sender, date, body))

        self.conn.commit()
        return self.cursor.lastrowid

    def add_attachment(self, email_id, file_name, file_data):
        file_hash = hashlib.sha256(file_data).hexdigest()
        self.cursor.execute('''
        INSERT INTO attachments (email_id, file_name, file_hash)
        VALUES (?, ?, ?)
        ''', (email_id, file_name, file_hash))

        file_out = file_hash + pathlib.Path(file_name).suffix
        if not file_out in self.zip.namelist():
            self.zip.writestr(file_out, file_data)

        self.conn.commit()

    def add(self, email):
        mail_subject, mail_sender, mail_date, mail_body, mail_attach = email
        email_id = self.add_email(mail_subject, mail_sender, mail_date, mail_body)
        for file_name, file_data in mail_attach:
            self.add_attachment(email_id, file_name, file_data)

    def close(self):
        self.conn.close()
        self.zip.close()
