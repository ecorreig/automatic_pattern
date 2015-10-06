__author__ = 'dracks'
import argparse
import smtplib
from email.message import Message


def send_mail(subject, message):
    from_addr = 'servers@binding-edu.org'
    to_addr = ['servers@binding-edu.org']
    header = Message()
    header['From'] = from_addr
    header['To'] = ', '.join(to_addr)
    header['Subject'] = subject
    msg = header.as_string() + message

    s = smtplib.SMTP('smtp.1and1.es', 587)
    s.login('mail@binding-edu.org', 'JS!0101')
    s.sendmail('servers@binding-edu.org', 'servers@binding-edu.org', msg)
    s.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_stdout", help="Standard output log file")
    parser.add_argument("file_stderr", help="Standard error log file")

    args = parser.parse_args()

    content_stdout = open(args.file_stdout).read()
    content_stderr = open(args.file_stderr).read()

    if len(content_stdout) > 3 or len(content_stderr) > 3:
        send_mail("Something happened", "std_output: \n"+content_stdout+"\n\n std_error:\n"+content_stderr)
