from base import tokens
import json

class TokenNotFoundMorph(tokens.TokenBase):
    def __init__(self,alpha_token):
        tokens.TokenBase.__init__(self,"not-found-morph",alpha_token.text)
        self._alpha_token=alpha_token

def factory(alpha_token,word_list):
    if len(word_list)==1:
        if word_list[0][0]=="word":
            t=TokenWord(alpha_token,word_list[0][1])
        else:
            t=TokenFusedWord(alpha_token,word_list[0][1])
        return [t.style],t

    tlist=[ factory(alpha_token,[w]) for w in word_list ]
    slist=[]
    for t in tlist: slist+=t[0]
    slist=list(set(slist))
    tlist=[ t[1] for t in tlist ]
    return slist,TokenMultipleWord(alpha_token,tlist)

def slugify(text):
    return text.lower().replace(" ","-")

class TokenWord(tokens.Token):
    def __init__(self,alpha_token,word):
        tokens.Token.__init__(self,
                              slugify(word.part_of_speech.name),
                              alpha_token.text,word.description)
        self.word=word
        self.style=(word.part_of_speech.name,self.label,
                    word.part_of_speech.bg_color,word.part_of_speech.fg_color)


        
