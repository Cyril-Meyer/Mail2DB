import argparse
import tarfile

import database
import mail


parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help='The name of the archive file to process')
args = parser.parse_args()

# Initialize Database
db = database.EmailDB('mail.db')

with tarfile.open(args.filename) as tar:
        # Iterate over each member in the tarfile
        for member in tar.getmembers():
            # Check if the member is an email file
            if member.isfile() and member.name.endswith('.eml'):
                # Extract the file and parse its content
                file = tar.extractfile(member)
                if file is not None:
                    email = mail.parse_eml(file)
                    db.add(email)

db.close()
