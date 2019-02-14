from base import tokens

class TokenNonWord(tokens.TokenBase):
    def __init__(self,text):
        tokens.TokenBase.__init__(self,"non-word",text)
