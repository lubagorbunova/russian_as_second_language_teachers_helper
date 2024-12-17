class TelebotResponse:
    def __init__(self, chat="", text="", commands=[], buttons=[], all=False, off_ignore=False, mess_type='text'):
        self.chat = chat
        self.text = text
        self.photo = ''
        self.all = all
        self.off_ignore = off_ignore
        self.commands = commands  #TelebotCommand
        self.buttons = buttons    #TelebotCommand
        self.mess_type = mess_type
        

class TelebotRequest:        
        def __init__(self, chat="", name="", text="", mess_type='text'):
            self.chat = chat
            self.name = name
            self.text = text
            self.mess_type = mess_type


class TelebotCommand:
    def __init__(self, name='', text=''):
        self.name = name
        self.text = text