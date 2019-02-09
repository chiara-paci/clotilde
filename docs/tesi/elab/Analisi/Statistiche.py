# -*- coding: utf-8 -*-

from config import *

class Statistiche(object):
    
    def __init__(self,glossario):
        self.glossario=glossario
        self.num_nomi_propri=[0,0]
        orig=ORIGINI.keys()
        orig=map(lambda x: x.lower(),orig)
        orig.sort()
        gram=GRAMMATICALI.keys()
        gram.sort()
        ngrm=NON_GRAMMATICALI.keys()
        ngrm.sort()
        self.col_keys={}
        self.col_keys["header"]=0
        self.num_cols=2+len(ORIGINI.keys())
        self.num_rows=len(gram)+len(ngrm)+1
        if "np" in gram: self.num_rows-=1

        self.R=map(lambda x: [""]+map(lambda x:[0,0],range(0,self.num_cols-1)),
                   range(0,self.num_rows))
        n=1
        for o in ["n.s."]+orig:
            self.col_keys[o]=n
            n+=1

        self.row_keys={}
        self.row_keys_gr={}
        self.row_keys_ng={}
        n=0
        for g in gram:
            if g=="np":
                continue
            self.row_keys[g]=n
            self.row_keys_gr[g]=n
            self.R[n][0]=GRAMMATICALI[g]
            n+=1
        self.NG=n
        for g in ngrm:
            self.row_keys[g]=n
            self.row_keys_ng[g]=n
            self.R[n][0]=NON_GRAMMATICALI[g]
            n+=1
        for (g,tit) in [ ( "n.s.","altro") ]:
            self.row_keys[g]=n
            self.R[n][0]=tit
            n+=1
        for v in self.glossario.get_all():
            if not v.matches: continue
            if v.origine:
                if v.origine[-1]=="?":
                    vorig=v.origine[:-1].lower()
                else:
                    vorig=v.origine.lower()
            else:
                vorig="n.s."
            if v.categorie:
                vcat=v.categorie
            else:
                vcat=["n.s."]
            c=self.col_keys[vorig]
            # QUI
            card=v.get_cardinalita()
            for g in vcat:
                if g=="np":
                    self.num_nomi_propri[0]+=1
                    self.num_nomi_propri[1]+=card
                    continue
                r=self.row_keys[g]
                try:
                    self.R[r][c][0]+=1
                    self.R[r][c][1]+=card
                except IndexError,e:
                    print r,c
                    sys.exit()

        self.row_keys["totgramm"]=-3
        self.row_keys["totnongramm"]=-2
        self.row_keys["totali"]=-1
        for (totrange,tottitle) in [ (range(0,self.NG),"tot. grammaticali"),
                                     (range(self.NG,self.num_rows-1),"tot. lessico"),
                                     ([-1,-2,-3],"totale") ]:
            tots=[tottitle]+map(lambda x: [0,0], range(1,self.num_cols))
            for r in totrange:
                for c in range(1,self.num_cols):
                    tots[c][0]+=self.R[r][c][0]
                    tots[c][1]+=self.R[r][c][1]
            self.R.append(tots)

    def get_sparsa(self):
        Q=self.R
        col_keys=self.col_keys
        num_cols=self.num_cols
        num_rows=self.num_rows+3
        return(Q,col_keys,num_cols,num_rows,self.NG,True)

    def get_nonsparsa(self):
        Q=[]

        # quelli rispetto a Q
        q_cols={}
        # quelli rispetto a self.R
        qr_cols=[]

        for clab in self.col_keys.keys():
            if clab=="header":
                qr_cols.append(clab)
                continue
            if not self.R[-1][self.col_keys[clab]][0]:
                continue
            qr_cols.append(clab)

        q_cols["header"]=0
        q_cols["n.s."]=1
        c=2
        for clab in qr_cols:
            if clab=="header": continue
            if clab=="n.s.": continue
            q_cols[clab]=c
            c+=1

        q_num_cols=len(q_cols.keys())

        def col_map(r_riga):
            q=[r_riga[0]]+map(lambda x: [0,0],range(1,q_num_cols))
            for clab in qr_cols:
                print q_cols[clab],self.col_keys[clab],clab
                print q
                print r_riga
                q[q_cols[clab]]=r_riga[self.col_keys[clab]]
            return(q)

        def row_filter(r_riga):
            t=reduce(lambda x,y: x+y,map(lambda x: x[0],r_riga[1:]))
            return(bool(t))

        Q=map(col_map,filter(row_filter,self.R[:self.NG]))
        num_gramm=len(Q)
        Q+=map(col_map,filter(row_filter,self.R[self.NG:-4]))
        print self.row_keys["n.s."],self.R[-4][0],len(self.R)
        print self.R[-4]
        if row_filter(self.R[-4]):
            Q.append(col_map(self.R[-4]))
            ns_esiste=True
        else:
            ns_esiste=False
            
        Q+=map(col_map,self.R[-3:])

        num_rows=len(Q)

        return((Q,q_cols,q_num_cols,num_rows,num_gramm,ns_esiste))
