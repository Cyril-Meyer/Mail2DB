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
            body TEXT,
            attachments TEXT
        )
        ''')

        self.conn.commit()

    def add_attachment(self, attachments):
        attachments_info = ''

        for file_name, file_data in attachments:
            file_hash = hashlib.sha256(file_data).hexdigest()
            file_out = file_hash + pathlib.Path(file_name).suffix
            attachments_info += f'{file_name}<=>{file_out}\n'
            # Check that file is not duplicate
            if not file_out in self.zip.namelist():
                self.zip.writestr(file_out, file_data)

        return attachments_info

    def add_email(self, subject, sender, date, body, attachments_info):
        self.cursor.execute('''
        INSERT INTO emails (subject, sender, date, body, attachments)
        VALUES (?, ?, ?, ?, ?)
        ''', (subject, sender, date, body, attachments_info))

        self.conn.commit()

    def add(self, email):
        mail_subject, mail_sender, mail_date, mail_body, mail_attach = email
        attachments_info = self.add_attachment(mail_attach)
        self.add_email(mail_subject, mail_sender, mail_date, mail_body, attachments_info)

    def close(self):
        self.conn.close()
        self.zip.close()
