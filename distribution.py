import base64
import datetime
import json
import os.path
import re
import sys
import Tkinter as Tk
import tkMessageBox
import urllib2


AUTH_ID = ''
AUTH_TOKEN = ''
URL = 'https://api.plivo.com/v1/Account/%s/Message/' % AUTH_ID
try:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
except NameError:
    APP_ROOT = os.path.dirname(os.path.abspath(sys.argv[0]))


class Window(Tk.Tk):
    def __init__(self):
        Tk.Tk.__init__(self)
        width, height = 287, 132
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry('%dx%d+%d+%d' % (width, height, (screen_width - width) / 2, (screen_height - height) / 2))
        self.resizable(width=Tk.FALSE, height=Tk.FALSE)
        self.title('SMS Distribution')

        self.label = Tk.Label(self, text=u'Alpha-numeric Sender')
        self.label.grid(row=0, column=0, sticky=Tk.W)

        self.alpha_var = Tk.StringVar()
        self.alpha_var.trace('w', lambda name, index, mode, sv=self.alpha_var: self.modifying_alpha(sv))
        self.alpha = Tk.Entry(self, textvariable=self.alpha_var)
        self.alpha.grid(row=0, column=1, columnspan=2, sticky=Tk.W)
        self.alpha.insert(Tk.INSERT, 'test')

        self.text = Tk.Text(self, width=40, height=5, bg='green')
        self.text.grid(row=1, column=0, columnspan=3, sticky=Tk.W)
        self.tk.call(self.text._w, 'edit', 'modified', 0)
        self.text.bind_all('<<Modified>>', self.modifying_text)

        self.count = Tk.Label(self, text=u'Numbers: 0')
        self.count.grid(row=2, column=0, sticky=Tk.W)
        self.count.bind('<Button-1>', self.copy_numbers)
        self.numbers = []

        self.button = Tk.Button(self, text=u'Send', command=self.send_messages)
        self.button.grid(row=2, column=2, sticky=Tk.W)

    def modifying_alpha(self, sv):
        if re.compile(r'^[\w \-]{1,12}$').match(sv.get()) is not None:
            self.alpha.config(bg='green')
        else:
            self.alpha.config(bg='red')

    def modifying_text(self, event=None):
        self.tk.call(self.text._w, 'edit', 'modified', 0)
        length = len(self.text.get('1.0', Tk.END))
        if length < 70:
            self.text.config(bg='green')
        elif length < 140:
            self.text.config(bg='yellow')
        else:
            self.text.config(bg='red')

    def copy_numbers(self, event=None):
        self.numbers = []
        invalid = []
        for line in self.clipboard_get().split('\n'):
            for number in line.split(','):
                number = filter(lambda x: x.isdigit(), number)
                if number.startswith('380'):
                    number = number[3:]
                elif number.startswith('80'):
                    number = number[2:]
                elif number.startswith('0'):
                    number = number[1:]
                if len(number) == 9:
                    self.numbers.append('380' + number)
                else:
                    invalid.append(line)
        if invalid:
            tkMessageBox.showinfo('Warning', 'These numbers have invalid format: \n' + '\n'.join(invalid))
        self.numbers = list(set(self.numbers))
        self.count.config(text='Numbers: %d' % len(self.numbers))

    def send_messages(self):
        alpha = self.alpha.get()
        if re.compile(r'^[\w \-]{1,12}$').match(alpha) is None:
            tkMessageBox.showwarning('Error', 'Incorrect Alpha-numeric Sender')
            return
        text = self.text.get('1.0', Tk.END)[:-1]
        if not text:
            tkMessageBox.showwarning('Error', 'Empty message')
            return

        auth = 'Basic ' + base64.urlsafe_b64encode('%s:%s' % (AUTH_ID, AUTH_TOKEN))
        headers = {'content-type': 'application/json', 'User-Agent': 'PythonPlivo', 'Authorization': auth}
        values = {'src': alpha, 'text': text.encode('utf-8')}

        for number in self.numbers:
            values['dst'] = number
            request = urllib2.Request(URL, json.dumps(values), headers)
            try:
                urllib2.urlopen(request)
            except IOError, e:
                with open(os.path.join(APP_ROOT, 'logs.txt'), 'a') as f:
                    f.write('%s: %s raised error `%s`\n' % (datetime.datetime.now(), number, e))


if __name__ == '__main__':
    window_obj = Window()
    window_obj.mainloop()
