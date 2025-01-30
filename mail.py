import email
import email.policy
import email.parser
import email.utils
import html.parser


class HTMLToPlainText(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.plain_text = []
        self.ignore_content = False

    def handle_starttag(self, tag, attrs):
        if tag in ['style', 'script']:
            self.ignore_content = True

    def handle_endtag(self, tag):
        if tag in ['style', 'script']:
            self.ignore_content = False

    def handle_data(self, data):
        if not self.ignore_content:
            self.plain_text.append(data)

    def get_plain_text(self):
        return ''.join(self.plain_text)


def convert_html_to_plaintext(html_content):
    parser = HTMLToPlainText()
    parser.feed(html_content)
    return parser.get_plain_text()


def parse_eml_file(file_path):
    with open(file_path, 'rb') as f:
        return parse_eml(f)


def parse_eml(file):
    msg = email.parser.BytesParser(policy=email.policy.default).parse(file)
    # Extract email subject, sender and date
    mail_subject = msg['subject']
    mail_from = email.utils.parseaddr(msg['from'])[1]

    try:
        mail_date = email.utils.parsedate_to_datetime(msg['date']).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        mail_date = msg['date']
        print('mail date parse error:', mail_date)

    # Extract email body
    mail_body = msg.get_body(('plain',))

    if mail_body is not None:
        mail_body = mail_body.get_content()
    else:
        mail_body = msg.get_body(('plain', 'html'))
        if mail_body is not None:
            mail_body = convert_html_to_plaintext(mail_body.get_content()).replace('\n', ' ')
        else:
            mail_body = '~NO MAIL BODY~'

    # Extract email attachments
    mail_attach = []

    for part in msg.iter_parts():
        # attachment
        if part.get_content_disposition() == 'attachment':
            file_name = part.get_filename()
            file_data = part.get_payload(decode=True)
            mail_attach.append((file_name, file_data))

    return mail_subject, mail_from, mail_date, mail_body, mail_attach
