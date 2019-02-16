from base import tokens

class TokenNonWord(tokens.TokenBase):
    def __init__(self,alpha_token):
        tokens.TokenBase.__init__(self,"non-word",alpha_token.text)
