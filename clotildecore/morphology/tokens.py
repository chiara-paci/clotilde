from base import tokens

class TokenNotFoundMorph(tokens.TokenBase):
    def __init__(self,alpha_token):
        tokens.TokenBase.__init__(self,"not-found-morph",alpha_token.text)
        self._alpha_token=alpha_token

def factory(alpha_token,word_list):
    if len(word_list)==1:
        if word_list[0][0]=="word":
            return TokenWord(alpha_token,word_list[0][1])
        return TokenFusedWord(alpha_token,word_list[0][1])

    tlist=[ factory(alpha_token,[w]) for w in word_list ]
    return TokenMultipleWord(alpha_token,tlist)


class TokenWord(tokens.Token):
    def __init__(self,alpha_token,word):
        tokens.Token.__init__(self,
                              word.cache_part_of_speech,
                              alpha_token.text,Description(json.loads(word.cache_description)))


        
