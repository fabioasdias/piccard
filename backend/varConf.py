from numpy import isnan
class oneVariable(object):
    def __init__(self,vname,sname=None):
        self._cols=dict()
        self._mult=dict()
        if not sname:
            sname=vname[:5]
        self.setName(vname,sname)
    def setName(self,vname,shortname):
        self._name=vname
        self._sname=shortname
    def getName(self):
        return(self._name)
    def getShortName(self):
        return(self._sname)    
    def getLabels(self):
        return([self._name,])
    def getShortLabels(self):
        return([self._sname,])    
    def _addColumn(self, year, colName,mult=1):
        if year not in self._cols:
            self._cols[year] = []
            self._mult[year] = []

        self._cols[year].append(colName)
        self._mult[year].append(mult)
    def addColumns(self,year, cols,mult=[]):#mult is handy for average income inflation correction
        if not mult:
            mult=[1.0,]*len(cols)

        for i,col in enumerate(cols):
            self._addColumn(year,col,mult[i])
            
    def computeValue(self,gjProps,year):
        ret = 0
        for i,col in enumerate(self._cols[year]):
            if (col==''):
                continue
            if (col[0]=='-'):
                s=True
                col=col[1:]
            else:
                s=False
            if (col not in gjProps):
                continue

            try:
                val=self._mult[year][i]*float(gjProps[col])
            except:
                return(['NaN',])

            if (isnan(val)):
                return(['NaN',])                                

            if (s):
                ret-=val
            else:
                ret+=val
        return([ret,])

class distVariable(object):
    def __init__(self,dName,vtype='category'):
        """Kind of variable influences how it is treated afterwards: 'category' or 'sequential' """
        self._vars=[]
        self.setName(dName)
        self._vtype=vtype
    def getType(self):
        return(self._vtype)
    def setName(self,dName):
        self._name=dName
    def getName(self):
        return(self._name)
    def addRange(self,rVar):
        self._vars.append(rVar)
    def getLabels(self):
        ret=[]
        for v in self._vars:
            ret.extend(v.getLabels())
        return(ret)
    def getShortLabels(self):
        ret=[]
        for v in self._vars:
            ret.extend(v.getShortLabels())
        return(ret)    
    def computeValue(self,gjProps,year):
        ret=[]
        for v in self._vars:
            ret.extend(v.computeValue(gjProps,year))
        return(ret)
    
        


def getVariables(kind='CA'):
    allVars=[]
    if (kind=='CA'):
        allVars.append(distVariable('Home language'))
        tVar=oneVariable('English','Eng') 
        tVar.addColumns(1971,['COL0000000205',]) #
        tVar.addColumns(1981,['COL0000000120','COL0000000123','COL0000000126',]) # english mother tongue, french mother tongue, other mother tongue
        tVar.addColumns(1991,['COL0000000164',]) #
        tVar.addColumns(2001,['COL0000000230',]) #
        tVar.addColumns(2011,['COL0000000703',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('French','Fre') 
        tVar.addColumns(1971,['COL0000000206',]) #
        tVar.addColumns(1981,['COL0000000121','COL0000000124','COL0000000127',]) # english mother tongue, french mother tongue, other mother tongue
        tVar.addColumns(1991,['COL0000000165',]) #
        tVar.addColumns(2001,['COL0000000231',]) #
        tVar.addColumns(2011,['COL0000000704',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Other','Oth') 
        tVar.addColumns(1971,['COL0000000207',]) #
        tVar.addColumns(1981,['COL0000000128',]) #
        tVar.addColumns(1991,['COL0000000166',]) #
        tVar.addColumns(2001,['COL0000000232',]) #
        tVar.addColumns(2011,['COL0000000705',]) #
        allVars[-1].addRange(tVar)



        #https://www.bankofcanada.ca/rates/related/inflation-calculator/
        # 1970/1980/1990/2000 -> 2010
        # allVars.append(distVariable('Avg. H. income (2010 eq)','sequential'))
        # tVar=oneVariable('Total') 
        # tVar.addColumns(1971,['COL0000000379',],[5.79]) # households average income from all sources
        # tVar.addColumns(1981,['COL0000000362',],[2.54]) # family income all families
        # tVar.addColumns(1991,['COL0000000665',],[1.47]) # family income
        # tVar.addColumns(2001,['COL0000001514',],[1.22]) # all families 20% sample data
        # tVar.addColumns(2011,['COL0000003899',],[1.0]) # family income
        # allVars[-1].addRange(tVar)

        #-------
        allVars.append(distVariable('Population','internal'))
        tVar=oneVariable('Total')
        tVar.addColumns(1971,['COL0000000003'])
        tVar.addColumns(1981,['COL0000000009'])
        tVar.addColumns(1991,['COL0000000007'])
        tVar.addColumns(2001,['COL0000000005'])
        tVar.addColumns(2011,['COL0000000005'])
        allVars[-1].addRange(tVar)

        #----------------

        allVars.append(distVariable('Age','sequential'))
        tVar=oneVariable('0-4')
        tVar.addColumns(1971,['COL0000000006','COL0000000025'])
        tVar.addColumns(1981,['COL0000000013','COL0000000025'])
        tVar.addColumns(1991,['COL0000000009','COL0000000026'])
        tVar.addColumns(2001,['COL0000000010','COL0000000029'])
        tVar.addColumns(2011,['COL0000000013',])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('5-14')
        tVar.addColumns(1971,['COL0000000008','COL0000000027','COL0000000007','COL0000000026'])
        tVar.addColumns(1981,['COL0000000015','COL0000000027','COL0000000014','COL0000000026'])
        tVar.addColumns(1991,['COL0000000011','COL0000000028','COL0000000010','COL0000000027'])
        tVar.addColumns(2001,['COL0000000012','COL0000000031','COL0000000011','COL0000000030'])
        tVar.addColumns(2011,['COL0000000015','COL0000000014'])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('15-24')
        tVar.addColumns(1971,['COL0000000009','COL0000000010','COL0000000011','COL0000000013','COL0000000028','COL0000000029','COL0000000030','COL0000000032','COL0000000014','COL0000000033'])
        tVar.addColumns(1981,['COL0000000016','COL0000000028','COL0000000017','COL0000000029'])
        tVar.addColumns(1991,['COL0000000012','COL0000000029','COL0000000013','COL0000000030'])
        tVar.addColumns(2001,['COL0000000013','COL0000000032','COL0000000014','COL0000000033'])
        tVar.addColumns(2011,['COL0000000016','COL0000000022'])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('25-34')
        tVar.addColumns(1971,['COL0000000015','COL0000000016','COL0000000034','COL0000000035'])
        tVar.addColumns(1981,['COL0000000018','COL0000000030'])
        tVar.addColumns(1991,['COL0000000014','COL0000000015','COL0000000031','COL0000000032'])
        tVar.addColumns(2001,['COL0000000015','COL0000000016','COL0000000034','COL0000000035'])
        tVar.addColumns(2011,['COL0000000023','COL0000000024'])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('35-44')
        tVar.addColumns(1971,['COL0000000017','COL0000000018','COL0000000036','COL0000000037'])
        tVar.addColumns(1981,['COL0000000019','COL0000000031'])
        tVar.addColumns(1991,['COL0000000016','COL0000000017','COL0000000033','COL0000000034'])
        tVar.addColumns(2001,['COL0000000017','COL0000000018','COL0000000036','COL0000000037'])
        tVar.addColumns(2011,['COL0000000025','COL0000000026',])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('45-54')
        tVar.addColumns(1971,['COL0000000019','COL0000000020','COL0000000038','COL0000000039'])
        tVar.addColumns(1981,['COL0000000020','COL0000000032'])
        tVar.addColumns(1991,['COL0000000018','COL0000000019','COL0000000035','COL0000000036'])
        tVar.addColumns(2001,['COL0000000019','COL0000000020','COL0000000038','COL0000000039'])
        tVar.addColumns(2011,['COL0000000027','COL0000000028',])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('55-64')
        tVar.addColumns(1971,['COL0000000021','COL0000000022','COL0000000040','COL0000000041'])
        tVar.addColumns(1981,['COL0000000021','COL0000000033'])
        tVar.addColumns(1991,['COL0000000020','COL0000000021','COL0000000037','COL0000000038'])
        tVar.addColumns(2001,['COL0000000021','COL0000000022','COL0000000040','COL0000000041'])
        tVar.addColumns(2011,['COL0000000029','COL0000000030',])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('65 and over','65+')
        tVar.addColumns(1971,['COL0000000023','COL0000000024','COL0000000042','COL0000000043'])
        tVar.addColumns(1981,['COL0000000022','COL0000000023','COL0000000034','COL0000000035'])
        tVar.addColumns(1991,['COL0000000022','COL0000000023','COL0000000024','COL0000000039','COL0000000040','COL0000000041'])
        tVar.addColumns(2001,['COL0000000023','COL0000000024','COL0000000025','COL0000000026','COL0000000027','COL0000000042','COL0000000043','COL0000000044','COL0000000045','COL0000000046'])
        tVar.addColumns(2011,['COL0000000031','COL0000000032','COL0000000033','COL0000000034','COL0000000035',])
        allVars[-1].addRange(tVar)



        #---------------------
        allVars.append(distVariable('Education level'))

        tVar=oneVariable('HS or below','No HS') 
        tVar.addColumns(1971,['COL0000000217','COL0000000219', # high school, some uni with no other trade
            'COL0000000214','COL0000000215','-COL0000000008','-COL0000000027','-COL0000000007','-COL0000000026']) #minus 5-14 so all are 15+, includes grade 9-10
        tVar.addColumns(1981,['COL0000000167','COL0000000169','COL0000000171' # high school, other non-uni without certificate, uni withtou degree
            'COL0000000165','COL0000000166']) # <9, 9-13 without certificate
        tVar.addColumns(1991,['COL0000000351','COL0000000353','COL0000000355','COL0000000356', # high school, other non-uni without certificate, uni without degree/certificate
            'COL0000000349','COL0000000350',]) # <9, 9-13 without certificate
        tVar.addColumns(2001,['COL0000001395','COL0000001398','COL0000001401','COL0000001402', # 20% sample data, high school, college wihtout diploma, uni without degree, certificate or diploma
            'COL0000001392','COL0000001394',]) # 20% sample data, <9, 1-14 without certificate
        tVar.addColumns(2011,['COL0000003197', #
            'COL0000003196',]) # no certificate, diploma, degree
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Trades or college') 
        tVar.addColumns(1971,['COL0000000216','COL0000000218','COL0000000220',]) # if has some  trade, it's here, unless uni
        tVar.addColumns(1981,['COL0000000168','COL0000000170',]) # trades, other non-uni with certificate
        tVar.addColumns(1991,['COL0000000352','COL0000000354',]) # trades, other non-uni with certificate
        tVar.addColumns(2001,['COL0000001396','COL0000001399',]) # 20% sample data, trades, college
        tVar.addColumns(2011,['COL0000003199','COL0000003200',]) # Apprenticeship or trades certificate or diploma, College, CEGEP or other non-university certificate or diploma
        allVars[-1].addRange(tVar)

        tVar=oneVariable('University','Univ') 
        tVar.addColumns(1971,['COL0000000221','COL0000000222',]) # uni w or w/o trade
        tVar.addColumns(1981,['COL0000000172',]) #
        tVar.addColumns(1991,['COL0000000357','COL0000000358',]) # uni with certificate, with degree
        tVar.addColumns(2001,['COL0000001403','COL0000001404']) # 20% sample data, uni with certificate or diploma, bachelors or higher
        tVar.addColumns(2011,['COL0000003201','COL0000003202',]) # below bachelors, bachelors or above
        allVars[-1].addRange(tVar)
        #-----------------------------------------------------------------           
        allVars.append(distVariable('Occupation'))
        tVar=oneVariable('Managerial and business support') #light blue
        tVar.addColumns(1971,['COL0000000287','COL0000000302','COL0000000291','COL0000000306',]) # male, female
        tVar.addColumns(1981,['COL0000000240','COL0000000256','COL0000000244','COL0000000260',]) # male, female
        tVar.addColumns(1991,['COL0000000503','COL0000000526','COL0000000510','COL0000000533',]) # male, female
        tVar.addColumns(2001,['COL0000000997','COL0000001002',]) #
        tVar.addColumns(2011,['COL0000003462','COL0000003463',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Culture') #purple
        tVar.addColumns(1971,['COL0000000290','COL0000000305','COL0000000288','COL0000000303',]) # male, female
        tVar.addColumns(1981,['COL0000000241','COL0000000243','COL0000000257','COL0000000259',]) # male, female
        tVar.addColumns(1991,['COL0000000504',' COL0000000505','COL0000000506','COL0000000507','COL0000000509','COL0000000527','COL0000000528',
            'COL0000000529','COL0000000530','COL0000000532',]) # male, female
        tVar.addColumns(2001,['COL0000001009','COL0000001017','COL0000001021',]) #
        tVar.addColumns(2011,['COL0000003464','COL0000003466','COL0000003467',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Health') #red 
        tVar.addColumns(1971,['COL0000000289','COL0000000304',]) # male, female
        tVar.addColumns(1981,['COL0000000242','COL0000000258',]) # male, female
        tVar.addColumns(1991,['COL0000000508','COL0000000531',]) # male, female
        tVar.addColumns(2001,['COL0000001012',]) #
        tVar.addColumns(2011,['COL0000003465',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Sales and service') #pink 
        tVar.addColumns(1971,['COL0000000292','COL0000000293','COL0000000307','COL0000000308',]) # male, female
        tVar.addColumns(1981,['COL0000000245','COL0000000246','COL0000000261','COL0000000262',]) # male, female
        tVar.addColumns(1991,['COL0000000511','COL0000000512','COL0000000534','COL0000000535',]) # male, female
        tVar.addColumns(2001,['COL0000001024',]) #
        tVar.addColumns(2011,['COL0000003468',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Trades and construction') #orange 
        tVar.addColumns(1971,['COL0000000297','COL0000000298','COL0000000312','COL0000000313',]) # male, female
        tVar.addColumns(1981,['COL0000000250','COL0000000251',]) # construction, transport (male)
        tVar.addColumns(1991,['COL0000000520','COL0000000521','COL0000000543','COL0000000544',]) # male, female
        tVar.addColumns(2001,['COL0000001035',]) #
        tVar.addColumns(2011,['COL0000003469',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Primary') #green
        tVar.addColumns(1971,['COL0000000294','COL0000000309',]) # male, female
        tVar.addColumns(1981,['COL0000000247','COL0000000263',]) #
        tVar.addColumns(1991,['COL0000000513','COL0000000514','COL0000000515','COL0000000516','COL0000000536','COL0000000537',
            'COL0000000538','COL0000000539',]) #
        tVar.addColumns(2001,['COL0000001045',]) #
        tVar.addColumns(2011,['COL0000003470',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Manufacturing') #blue
        tVar.addColumns(1971,['COL0000000295','COL0000000296','COL0000000310','COL0000000311',]) # male, female
        tVar.addColumns(1981,['COL0000000248','COL0000000249','COL0000000264','COL0000000265',]) # male, female
        tVar.addColumns(1991,['COL0000000517','COL0000000518','COL0000000519','COL0000000522','COL0000000523','COL0000000540,'
            'COL0000000541','COL0000000542','COL0000000545','COL0000000546',]) #
        tVar.addColumns(2001,['COL0000001049',]) #
        tVar.addColumns(2011,['COL0000003471',]) #
        allVars[-1].addRange(tVar)

 
         #-----------------------------
        allVars.append(distVariable('Religion'))
        tVar=oneVariable('Catholic') 
        tVar.addColumns(1971,['COL0000000192','COL0000000194']) 
        tVar.addColumns(1981,['COL0000000138',]) 
        tVar.addColumns(1991,['COL0000000233',]) 
        tVar.addColumns(2001,['COL0000001683','COL0000001702']) 
        tVar.addColumns(2011,['COL0000002714',]) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Protestant') 
        tVar.addColumns(1971,['COL0000000176','COL0000000177','COL0000000178','COL0000000195','COL0000000191','COL0000000187','COL0000000190','COL0000000188','COL0000000185','COL0000000193','COL0000000189','COL0000000184','COL0000000180','COL0000000181','COL0000000182']) 
        tVar.addColumns(1981,['COL0000000139',]) 
        tVar.addColumns(1991,['COL0000000236',]) 
        tVar.addColumns(2001,['COL0000001704','COL0000001701','COL0000001685','COL0000001686','COL0000001688','COL0000001689','COL0000001691','COL0000001692','COL0000001693','COL0000001699','COL0000001708','COL0000001703','COL0000001712','COL0000001707','COL0000001705','COL0000001713','COL0000001715']) 
        tVar.addColumns(2011,['COL0000002712','COL0000002713','COL0000002716','COL0000002717','COL0000002718','COL0000002719']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Jewish') 
        tVar.addColumns(1971,['COL0000000186',]) 
        tVar.addColumns(1981,['COL0000000143',]) 
        tVar.addColumns(1991,['COL0000000251',]) 
        tVar.addColumns(2001,['COL0000001694',]) 
        tVar.addColumns(2011,['COL0000002722',]) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Eastern Orthodox','E. Ortho') 
        tVar.addColumns(1971,['COL0000000183',]) 
        tVar.addColumns(1981,['COL0000000142',]) 
        tVar.addColumns(1991,['COL0000000250',]) 
        tVar.addColumns(2001,['COL0000001698','COL0000001710','COL0000001716','COL0000001700']) 
        tVar.addColumns(2011,['COL0000002715',]) 
        allVars[-1].addRange(tVar)
        
        tVar=oneVariable('Eastern non-christian', 'ENC') 
        tVar.addColumns(1971,['COL0000000179',]) 
        tVar.addColumns(1981,['COL0000000145',]) 
        tVar.addColumns(1991,['COL0000000252','COL0000000253','COL0000000254','COL0000000255']) 
        tVar.addColumns(2001,['COL0000001690','COL0000001695','COL0000001696','COL0000001697']) 
        tVar.addColumns(2011,['COL0000002710','COL0000002724','COL0000002723','COL0000002721']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('No preference') 
        tVar.addColumns(1971,['COL0000000196',]) 
        tVar.addColumns(1981,['COL0000000144',]) 
        tVar.addColumns(1991,['COL0000000257',]) 
        tVar.addColumns(2001,['COL0000001684',]) 
        tVar.addColumns(2011,['COL0000002727',]) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Other') 
        tVar.addColumns(1971,['COL0000000197',]) 
        tVar.addColumns(1981,['COL0000000146',]) 
        tVar.addColumns(1991,['COL0000000256',]) 
        tVar.addColumns(2001,['COL0000001711','COL0000001714','COL0000001687','COL0000001709','COL0000001706']) 
        tVar.addColumns(2011,['COL0000002726','COL0000002725','COL0000002720']) 
        allVars[-1].addRange(tVar)






        #---------------------------------------
        allVars.append(distVariable('Household Income (2015)','sequential'))
        tVar=oneVariable('<30k') 
        tVar.addColumns(1971,['COL0000000373','COL0000000374']) 
        tVar.addColumns(1981,['COL0000000384','COL0000000385']) 
        tVar.addColumns(1991,['COL0000000678','COL0000000679','COL0000000680']) 
        tVar.addColumns(2001,['COL0000001503','COL0000001504','COL0000001505']) 
        tVar.addColumns(2011,['COL0000003976','COL0000003977','COL0000003978','COL0000003979','COL0000003980']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('30-90k')
        tVar.addColumns(1971,['COL0000000375','COL0000000376','COL0000000377',])
        tVar.addColumns(1981,['COL0000000386','COL0000000387','COL0000000388','COL0000000389',])
        tVar.addColumns(1991,['COL0000000681','COL0000000682','COL0000000683','COL0000000684',])
        tVar.addColumns(2001,['COL0000001506','COL0000001507','COL0000001509','COL0000001508',])
        tVar.addColumns(2011,['COL0000003981','COL0000003982','COL0000003983','COL0000003984',]) #~85-135k
        allVars[-1].addRange(tVar)

        tVar=oneVariable('>90k')
        tVar.addColumns(1971,['COL0000000378',])
        tVar.addColumns(1981,['COL0000000390','COL0000000391',]) 
        tVar.addColumns(1991,['COL0000000685','COL0000000686',]) #~105k
        tVar.addColumns(2001,['COL0000001510','COL0000001511','COL0000001512','COL0000001513',]) #~105k
        tVar.addColumns(2011,['COL0000003985','COL0000003986','COL0000003987','COL0000003988',]) #~135k
        allVars[-1].addRange(tVar)

    #--------------------------------------------
        allVars.append(distVariable('Marital status'))
        tVar=oneVariable('Single') 
        tVar.addColumns(1971,['COL0000000044',]) 
        tVar.addColumns(1981,['COL0000000036',]) 
        tVar.addColumns(1991,['COL0000000042',]) # persons 15 years of age and over
        tVar.addColumns(2001,['COL0000000048',]) 
        tVar.addColumns(2011,['COL0000000185',]) # never legally married
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Married (incl. separated)') 
        tVar.addColumns(1971,['COL0000000046','COL0000000047',]) # married, separated
        tVar.addColumns(1981,['COL0000000038',]) 
        tVar.addColumns(1991,['COL0000000043','COL0000000044',]) # legally married and not separated, legally married and separated
        tVar.addColumns(2001,['COL0000000049','COL0000000050',]) # legally married and not separated, separated but still legally married
        tVar.addColumns(2011,['COL0000000181','COL0000000186',]) # legally married or living with a common law, separated
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Widowed') 
        tVar.addColumns(1971,['COL0000000048',])
        tVar.addColumns(1981,['COL0000000039',]) 
        tVar.addColumns(1991,['COL0000000045',]) 
        tVar.addColumns(2001,['COL0000000052',]) 
        tVar.addColumns(2011,['COL0000000188',]) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Divorced') 
        tVar.addColumns(1971,['COL0000000049',]) 
        tVar.addColumns(1981,['COL0000000040',])
        tVar.addColumns(1991,['COL0000000046',]) 
        tVar.addColumns(2001,['COL0000000051',]) 
        tVar.addColumns(2011,['COL0000000187',]) 
        allVars[-1].addRange(tVar)

    #----------------------------------------------------------------------
        allVars.append(distVariable('Place of birth'))
        tVar=oneVariable('Canada') 
        tVar.addColumns(1971,['COL0000000149',]) 
        tVar.addColumns(1981,['COL0000000147',])
        tVar.addColumns(1991,['COL0000000295',]) 
        tVar.addColumns(2001,['COL0000000406',]) 
        tVar.addColumns(2011,['COL0000001465',]) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Europe','Euro') #includes russia
        tVar.addColumns(1971,['COL0000000152','COL0000000153','COL0000000154','COL0000000155','COL0000000156',
            'COL0000000157','COL0000000158','COL0000000159','COL0000000160','COL0000000161','COL0000000162',
            'COL0000000163','COL0000000164','COL0000000165','COL0000000166',]) 
        tVar.addColumns(1981,['COL0000000152','COL0000000153']) # uk, other european
        tVar.addColumns(1991,['COL0000000301','COL0000000302',]) # uk, other europe
        tVar.addColumns(2001,['COL0000000410','COL0000000412','COL0000000417','COL0000000418','COL0000000419',
            'COL0000000422','COL0000000426','COL0000000429','COL0000000433','COL0000000434','COL0000000436',    
            'COL0000000437','COL0000000438','COL0000000439','COL0000000444','COL0000000446','COL0000000450','COL0000000454',
            'COL0000000456',]) 
        tVar.addColumns(2011,['COL0000001481',])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Asia') # 
        tVar.addColumns(1971,['COL0000000167','COL0000000168','COL0000000169',]) 
        tVar.addColumns(1981,['COL0000000154',]) 
        tVar.addColumns(1991,['COL0000000304','COL0000000305',]) # india, other asia
        tVar.addColumns(2001,['COL0000000411','COL0000000413','COL0000000415','COL0000000416','COL0000000420',
            'COL0000000423','COL0000000425','COL0000000427','COL0000000428','COL0000000430','COL0000000431',
            'COL0000000445','COL0000000451','COL0000000452','COL0000000453','COL0000000459',]) 
        tVar.addColumns(2011,['COL0000001508',])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Africa') 
        tVar.addColumns(1971,['COL0000000170',]) 
        tVar.addColumns(1981,['',]) #CHASS doesnt have it, statcan pointed to a pdf in archive.org
        tVar.addColumns(1991,['COL0000000303',]) 
        tVar.addColumns(2001,['COL0000000442','COL0000000443','COL0000000447','COL0000000455','COL0000000457',
            'COL0000000458',]) 
        tVar.addColumns(2011,['COL0000001499',]) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Americas') 
        tVar.addColumns(1971,['COL0000000151','COL0000000171',]) # usa, west indies and latin america
        tVar.addColumns(1981,['COL0000000150','COL0000000151',]) # usa, other america
        tVar.addColumns(1991,['COL0000000298','COL0000000299','COL0000000300',]) # usa, central and south america, caribbean and bermuda 
        tVar.addColumns(2001,['COL0000000414','COL0000000421','COL0000000424','COL0000000432','COL0000000435',
            'COL0000000440','COL0000000441','COL0000000448',]) 
        tVar.addColumns(2011,['COL0000001469',])
        allVars[-1].addRange(tVar) 

        tVar=oneVariable('Other') 
        tVar.addColumns(1971,['COL0000000172',]) 
        tVar.addColumns(1981,['',])
        tVar.addColumns(1991,['COL0000000306',]) # oceania and other
        tVar.addColumns(2001,['COL0000000449','COL0000000460',]) # fiji, other
        tVar.addColumns(2011,['COL0000001526',]) # oceania and other
        allVars[-1].addRange(tVar)


##########################################################################################
        
    if (kind=='US'):

        allVars.append(distVariable('Population','internal'))
        tVar=oneVariable('Total') 
        tVar.addColumns(1970,['CEB001','CEB010','CEB002','CEB011','CEB003','CEB012','CEB004','CEB013','CEB005','CEB014','CEB006','CEB015','CEB007','CEB016','CEB008','CEB017','CEB009','CEB018'])
        tVar.addColumns(1980,['C9D001','C9D002','C9D003','C9D004','C9D005','C9D006', 'C9D007', 'C9D008', 'C9D009', 'C9D010', 'C9D011', 'C9D012', 'C9D013', 'C9D014','C9D015'])
        tVar.addColumns(1990,['EUZ001','EUZ002','EUZ003','EUZ004','EUZ005', 'EUZ006','EUZ007','EUZ008','EUZ009','EUZ010','EUZ011','EUZ012','EUZ013','EUZ014','EUZ015','EUZ016','EUZ017','EUZ018','EUZ019','EUZ020','EUZ021','EUZ022','EUZ023','EUZ024','EUZ025',])
        tVar.addColumns(2000,['FL9003','FL9002','FL9001','FL9004','FL9005','FL9006'])
        tVar.addColumns(2010,['JMCE003','JMCE004','JMCE005','JMCE006','JMCE007','JMCE008'])
        allVars[-1].addRange(tVar)
        #--------------------

        allVars.append(distVariable('Race'))
        tVar=oneVariable('White') 
        tVar.addColumns(1970,['CEB001','CEB010',]) # male, female
        tVar.addColumns(1980,['C9D001',]) #
        tVar.addColumns(1990,['ET4001','ET4002','ET4003','ET4004','ET4005','ET4006','ET4007','ET4008',
            'ET4009','ET4010','ET4011','ET4012','ET4013','ET4014','ET4015','ET4016','ET4017','ET4018',
            'ET4019','ET4020','ET4021','ET4022','ET4023','ET4024','ET4025','ET4026','ET4027','ET4028',
            'ET4029','ET4030','ET4031','ET4032','ET4033','ET4034','ET4035','ET4036','ET4037','ET4038',
            'ET4039','ET4040','ET4041','ET4042','ET4043','ET4044','ET4045','ET4046','ET4047','ET4048',
            'ET4049','ET4050','ET4051','ET4052','ET4053','ET4054','ET4055','ET4056','ET4057','ET4058',
            'ET4059','ET4060','ET4061','ET4062',]) #
        tVar.addColumns(2000,['FL9001',]) #
        tVar.addColumns(2010,['JMCE003',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Black') 
        tVar.addColumns(1970,['CEB002','CEB011',]) # male, female
        tVar.addColumns(1980,['C9D002',]) #
        tVar.addColumns(1990,['ET4063','ET4064','ET4065','ET4066','ET4067','ET4068','ET4069','ET4070',
            'ET4071','ET4072','ET4073','ET4074','ET4075','ET4076','ET4077','ET4078','ET4079','ET4080',
            'ET4081','ET4082','ET4083','ET4084','ET4085','ET4086','ET4087','ET4088','ET4089','ET4090',
            'ET4091','ET4092','ET4093','ET4094','ET4095','ET4096','ET4097','ET4098','ET4099','ET4100',
            'ET4101','ET4102','ET4103','ET4104','ET4105','ET4106','ET4107','ET4108','ET4109','ET4110',
            'ET4111','ET4112','ET4113','ET4114','ET4115','ET4116','ET4117','ET4118','ET4119','ET4120',
            'ET4121','ET4122','ET4123','ET4124',]) #
        tVar.addColumns(2000,['FL9002',]) #
        tVar.addColumns(2010,['JMCE004',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Indian, eskimo and aleut','Nat.') 
        tVar.addColumns(1970,['CEB003','CEB012',]) # indian
        tVar.addColumns(1980,['C9D003','C9D004','C9D005',]) #
        tVar.addColumns(1990,['ET4125','ET4126','ET4127','ET4128','ET4129','ET4130','ET4131','ET4132',
            'ET4133','ET4134','ET4135','ET4136','ET4137','ET4138','ET4139','ET4140','ET4141','ET4142',
            'ET4143','ET4144','ET4145','ET4146','ET4147','ET4148','ET4149','ET4150','ET4151','ET4152',
            'ET4153','ET4154','ET4155','ET4156','ET4157','ET4158','ET4159','ET4160','ET4161','ET4162',
            'ET4163','ET4164','ET4165','ET4166','ET4167','ET4168','ET4169','ET4170','ET4171','ET4172',
            'ET4173','ET4174','ET4175','ET4176','ET4177','ET4178','ET4179','ET4180','ET4181','ET4182',
            'ET4183','ET4184','ET4185','ET4186',]) #
        tVar.addColumns(2000,['FL9003',]) #
        tVar.addColumns(2010,['JMCE005',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Asian, Hawaiian, other pacific islander') 
        tVar.addColumns(1970,['CEB004','CEB005','CEB006','CEB007','CEB008','CEB013','CEB014','CEB015',
            'CEB016','CEB017',]) #japanese, chinese, filipino, hawaiian, korean
        tVar.addColumns(1980,['C9D006','C9D007','C9D008','C9D009','C9D010','C9D011','C9D012','C9D013',
            'C9D014',]) # japanese, chinese, filipino, korean, asian indian, vietnamese, hawaiian, guamanian, samoan
        tVar.addColumns(1990,['ET4187','ET4188','ET4189','ET4190','ET4191','ET4192','ET4193','ET4194',
            'ET4195','ET4196','ET4197','ET4198','ET4199','ET4200','ET4201','ET4202','ET4203','ET4204',
            'ET4205','ET4206','ET4207','ET4208','ET4209','ET4210','ET4211','ET4212','ET4213','ET4214',
            'ET4215','ET4216','ET4217','ET4218','ET4219','ET4220','ET4221','ET4222','ET4223','ET4224',
            'ET4225','ET4226','ET4227','ET4228','ET4229','ET4230','ET4231','ET4232','ET4233','ET4234',
            'ET4235','ET4236','ET4237','ET4238','ET4239','ET4240','ET4241','ET4242','ET4243','ET4244',
            'ET4245','ET4246','ET4247','ET4248',]) # asian or pacific islander
        tVar.addColumns(2000,['FL9004','FL9005',]) # asian, native hawaiian and other pacific islander
        tVar.addColumns(2010,['JMCE006','JMCE007',]) # asian, native hawaiian and other pacific islander
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Other') 
        tVar.addColumns(1970,['CEB009','CEB018',]) #
        tVar.addColumns(1980,['C9D015',]) #
        tVar.addColumns(1990,['ET4249','ET4250','ET4251','ET4252','ET4253','ET4254','ET4255','ET4256',
            'ET4257','ET4258','ET4259','ET4260','ET4261','ET4262','ET4263','ET4264','ET4265','ET4266',
            'ET4267','ET4268','ET4269','ET4270','ET4271','ET4272','ET4273','ET4274','ET4275','ET4276',
            'ET4277','ET4278','ET4279','ET4280','ET4281','ET4282','ET4283','ET4284','ET4285','ET4286',
            'ET4287','ET4288','ET4289','ET4290','ET4291','ET4292','ET4293','ET4294','ET4295','ET4296',
            'ET4297','ET4298','ET4299','ET4300','ET4301','ET4302','ET4303','ET4304','ET4305','ET4306',
            'ET4307','ET4308','ET4309','ET4310',]) #
        tVar.addColumns(2000,['FL9006',]) #
        tVar.addColumns(2010,['JMCE008',]) #
        allVars[-1].addRange(tVar)
#-------------------------------------------
        allVars.append(distVariable('Marital status'))
        tVar=oneVariable('Married (inc. Sep.)') 
        tVar.addColumns(1970,['CII001', 'CII006', 'CII011', 'CII016', 'CII021', 'CII026', 'CII031', 'CII036', 'CII041', 'CII046', 'CII051', 'CII056', 'CII061', 'CII066',
            'CII004','CII009','CII014','CII019','CII024','CII029','CII034','CII039','CII044','CII049','CII054','CII059','CII064','CII069',]) #sep
        tVar.addColumns(1980,['C7F002','C7F007',
            'C7F003','C7F008'])
        tVar.addColumns(1990,['ET6002','ET6007','ET6003','ET6008']) 
        tVar.addColumns(2000,['GIZ002','GIZ006']) 
        tVar.addColumns(2010,['J0WE018','J0WE111']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Widowed') 
        tVar.addColumns(1970,['CII002','CII007','CII012','CII017','CII022','CII027','CII032','CII037','CII042','CII047','CII052','CII057','CII062','CII067',]) 
        tVar.addColumns(1980,['C7F004','C7F009'])
        tVar.addColumns(1990,['ET6004','ET6009']) 
        tVar.addColumns(2000,['GIZ003','GIZ007']) 
        tVar.addColumns(2010,['J0WE065','J0WE158']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Divorced') 
        tVar.addColumns(1970,['CII003','CII008','CII013','CII018','CII023','CII028','CII033','CII038','CII043','CII048','CII053','CII058','CII063','CII068',]) 
        tVar.addColumns(1980,['C7F005','C7F010'])
        tVar.addColumns(1990,['ET6005','ET6010']) 
        tVar.addColumns(2000,['GIZ004','GIZ008']) 
        tVar.addColumns(2010,['J0WE080','J0WE173']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Never married','Single') 
        tVar.addColumns(1970,['CII005','CII010','CII015','CII020','CII025','CII030','CII035','CII040','CII045','CII050','CII055','CII060','CII065','CII070',]) 
        tVar.addColumns(1980,['C7F001','C7F006'])
        tVar.addColumns(1990,['ET6001','ET6006']) 
        tVar.addColumns(2000,['GIZ001','GIZ005']) 
        tVar.addColumns(2010,['J0WE003','J0WE096']) 
        allVars[-1].addRange(tVar)

#--------------------------------------------------------------------

        allVars.append(distVariable('Education level','sequential'))
        tVar=oneVariable('Not completed High School','No HS') 
        tVar.addColumns(1970,['C06001','C06002', 'C06003', 'C06004', 'C06005', 'C06006']) 
        tVar.addColumns(1980,['DHS001'])
        tVar.addColumns(1990,['E33001','E33002']) 
        tVar.addColumns(2000,['GKT001', 'GKT002', 'GKT003', 'GKT004', 'GKT005', 'GKT006', 'GKT007', 'GKT008', 'GKT017', 'GKT018', 'GKT019', 'GKT020', 'GKT021', 'GKT022', 'GKT023', 'GKT024']) 
        tVar.addColumns(2010,['JN9E003', 'JN9E004', 'JN9E005', 'JN9E006', 'JN9E007', 'JN9E008', 'JN9E009', 'JN9E010', 'JN9E020', 'JN9E021', 'JN9E022', 'JN9E023', 'JN9E024', 'JN9E025', 'JN9E026', 'JN9E027']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('High School','HS') 
        tVar.addColumns(1970,['C06007']) 
        tVar.addColumns(1980,['DHS002'])
        tVar.addColumns(1990,['E33003']) 
        tVar.addColumns(2000,['GKT009','GKT025']) 
        tVar.addColumns(2010,['JN9E011','JN9E028']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('College 1-3 years','1-3 C') 
        tVar.addColumns(1970,['C06008']) 
        tVar.addColumns(1980,['DHS003'])
        tVar.addColumns(1990,['E33004','E33005']) 
        tVar.addColumns(2000,['GKT010', 'GKT011', 'GKT012', 'GKT026', 'GKT027', 'GKT028']) 
        tVar.addColumns(2010,['JN9E012', 'JN9E013', 'JN9E014', 'JN9E029', 'JN9E030', 'JN9E031']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('College 4+ years','4+ C') 
        tVar.addColumns(1970,['C06009','C06010']) 
        tVar.addColumns(1980,['DHS004','DHS005'])
        tVar.addColumns(1990,['E33006','E33007']) 
        tVar.addColumns(2000,['GKT013', 'GKT014', 'GKT015', 'GKT016', 'GKT029', 'GKT030', 'GKT031', 'GKT032']) 
        tVar.addColumns(2010,['JN9E015', 'JN9E016', 'JN9E017', 'JN9E018', 'JN9E032', 'JN9E033', 'JN9E034', 'JN9E035']) 
        allVars[-1].addRange(tVar)

#-----------------------------------------------------------------------------------
        allVars.append(distVariable('Family income (2010)'))
        tVar=oneVariable('<50k') 
        tVar.addColumns(1970,['C3T001','C3T002','C3T003','C3T004','C3T005','C3T006','C3T007','C3T008',
            'C3T009',]) #
        tVar.addColumns(1980,['DIK001','DIK002','DIK003','DIK004','DIK005','DIK006','DIK007','DIK008',]) #
        tVar.addColumns(1990,['E0Q001','E0Q002','E0Q003','E0Q004','E0Q005','E0Q006','E0Q007','E0Q008',
            'E0Q009','E0Q010',]) #
        tVar.addColumns(2000,['GNN001','GNN002','GNN003','GNN004','GNN005','GNN006','GNN007',]) #
        tVar.addColumns(2010,['JPNE002','JPNE003','JPNE004','JPNE005','JPNE006','JPNE007','JPNE008',
            'JPNE009','JPNE010',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('50k-100k','50-100k') 
        tVar.addColumns(1970,['C3T010','C3T011','C3T012',]) #
        tVar.addColumns(1980,['DIK009','DIK010','DIK011','DIK012','DIK013',]) #
        tVar.addColumns(1990,['E0Q011','E0Q012','E0Q013','E0Q014','E0Q015','E0Q016','E0Q017','E0Q018',
            'E0Q019','E0Q020',]) #
        tVar.addColumns(2000,['GNN008','GNN009','GNN010','GNN011',]) #
        tVar.addColumns(2010,['JPNE011','JPNE012','JPNE013',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('>$100k') 
        tVar.addColumns(1970,['C3T013','C3T014','C3T015',]) #
        tVar.addColumns(1980,['DIK014','DIK015','DIK016','DIK017',]) #
        tVar.addColumns(1990,['E0Q021','E0Q022','E0Q023','E0Q024','E0Q025',]) #
        tVar.addColumns(2000,['GNN012','GNN013','GNN014','GNN015','GNN016',]) #
        tVar.addColumns(2010,['JPNE014','JPNE015','JPNE016','JPNE017',]) #
        allVars[-1].addRange(tVar)
#-----------------------------------------------------------------
        # allVars.append(distVariable('Rent (Approximated 2010 USD)','sequential'))
        # tVar=oneVariable('Less than $500','<500') 
        # tVar.addColumns(1970,['CHA001','CHA002','CHA003','CHA004','CHA005','CHA006',]) #
        # tVar.addColumns(1980,['C8N001','C8N002','C8N003','C8N004','C8N005','C8N006','C8N007',]) #
        # tVar.addColumns(1990,['ES4001','ES4002','ES4003','ES4004',]) #
        # tVar.addColumns(2000,['GBK001','GBK002','GBK003','GBK004','GBK005','GBK006',]) #
        # tVar.addColumns(2010,['JSXE003','JSXE004','JSXE005','JSXE006','JSXE007','JSXE008','JSXE009','JSXE010','JSXE011',]) #
        # allVars[-1].addRange(tVar)

        # tVar=oneVariable('$500 - $1,000','0.5-1k') 
        # tVar.addColumns(1970,['CHA007','CHA008','CHA009','CHA010',]) #
        # tVar.addColumns(1980,['C8N008','C8N009','C8N010']) #
        # tVar.addColumns(1990,['ES4005','ES4006','ES4007','ES4008','ES4009','ES4010',]) #
        # tVar.addColumns(2000,['GBK007','GBK008','GBK009','GBK010','GBK011','GBK012','GBK013','GBK014',]) #
        # tVar.addColumns(2010,['JSXE012','JSXE013','JSXE014','JSXE015','JSXE016','JSXE017','JSXE018','JSXE019',]) #
        # allVars[-1].addRange(tVar)

        # tVar=oneVariable('$1,000 - $1500','1-1.5k') 
        # tVar.addColumns(1970,['CHA011','CHA012',]) #
        # tVar.addColumns(1980,['C8N011','C8N012','C8N013',]) #
        # tVar.addColumns(1990,['ES4011','ES4012','ES4013','ES4014',]) #
        # tVar.addColumns(2000,['GBK015','GBK016','GBK017']) #
        # tVar.addColumns(2010,['JSXE020','JSXE021',]) #
        # allVars[-1].addRange(tVar)

        # tVar=oneVariable('$1,500 - $2,000','1.5-2k') 
        # tVar.addColumns(1970,['CHA013','CHA014',]) #
        # tVar.addColumns(1980,['',]) # no data
        # tVar.addColumns(1990,['ES4015','ES4016',]) #
        # tVar.addColumns(2000,['GBK018','GBK019',]) #
        # tVar.addColumns(2010,['JSXE022',]) #
        # allVars[-1].addRange(tVar)

        # tVar=oneVariable('More than $2,000','>2k') 
        # tVar.addColumns(1970,['',]) # no data
        # tVar.addColumns(1980,['',]) # no data
        # tVar.addColumns(1990,['',]) # no data
        # tVar.addColumns(2000,['GBK020','GBK021']) #
        # tVar.addColumns(2010,['JSXE023',]) #
        # allVars[-1].addRange(tVar)

        #--------------------------------------------------
        allVars.append(distVariable('Occupation'))
        tVar=oneVariable('Administrative','Adm') 
        tVar.addColumns(1970,['C27001','C27002','C27003','C27004','C27005','C27006','C27007','C27008',
            'C27009','C27010','C27011','C27015','C27016','C27017','C27012','C27013','C27014',]) #
        tVar.addColumns(1980,['DIB001','DIB002','DIB003','DIB004','DIB005',]) #
        tVar.addColumns(1990,['E4Q001','E4Q002','E4Q003','E4Q004','E4Q005',]) #
        tVar.addColumns(2000,['GMJ001','GMJ003','GMJ007','GMJ009',]) #
        tVar.addColumns(2010,['JQ5E003','JQ5E027','JQ5E039','JQ5E063',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Laborers','Lab') 
        tVar.addColumns(1970,['C27018','C27019','C27020','C27021','C27022','C27023','C27024','C27025',
            'C27026','C27027','C27028','C27029','C27030','C27031','C27032','C27033','C27034','C27035',]) #
        tVar.addColumns(1980,['DIB009','DIB010','DIB011','DIB012','DIB013',]) #
        tVar.addColumns(1990,['E4Q009','E4Q010','E4Q011','E4Q012','E4Q013',]) #
        tVar.addColumns(2000,['GMJ004','GMJ005','GMJ006','GMJ010','GMJ011','GMJ012',]) #
        tVar.addColumns(2010,['JQ5E030','JQ5E034','JQ5E066','JQ5E070',]) #
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Service','Serv') 
        tVar.addColumns(1970,['C27036','C27037','C27038','C27039','C27040','C27041','C27042',]) #
        tVar.addColumns(1980,['DIB006','DIB007','DIB008',]) #
        tVar.addColumns(1990,['E4Q006','E4Q007','E4Q008',]) #
        tVar.addColumns(2000,['GMJ002','GMJ008',]) #
        tVar.addColumns(2010,['JQ5E019','JQ5E055',]) #
        allVars[-1].addRange(tVar)

    if kind=="CAUS":
        
        allVars.append(distVariable('Marital status'))
        tVar=oneVariable('Never married') 
        tVar.addColumns(1970,['COL0000000044','CII005','CII010','CII015','CII020','CII025','CII030','CII035','CII040','CII045','CII050','CII055','CII060','CII065','CII070',]) 
        tVar.addColumns(1980,['COL0000000036','C7F001','C7F006']) 
        tVar.addColumns(1990,['COL0000000042','ET6001','ET6006'])
        tVar.addColumns(2000,['COL0000000048','GIZ001','GIZ005']) 
        tVar.addColumns(2010,['COL0000000185','J0WE003','J0WE096'])
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Married (incl. separated)') 
        tVar.addColumns(1970,['COL0000000046','COL0000000047','CII001', 'CII006', 'CII011', 'CII016', 'CII021', 'CII026', 'CII031', 'CII036', 'CII041', 'CII046', 'CII051', 'CII056', 'CII061', 'CII066',
            'CII004','CII009','CII014','CII019','CII024','CII029','CII034','CII039','CII044','CII049','CII054','CII059','CII064','CII069'])
        tVar.addColumns(1980,['COL0000000038','C7F002','C7F007', 'C7F003','C7F008']) 
        tVar.addColumns(1990,['COL0000000043','COL0000000044','ET6002','ET6007','ET6003','ET6008']) 
        tVar.addColumns(2000,['COL0000000049','COL0000000050','GIZ002','GIZ006']) 
        tVar.addColumns(2010,['COL0000000181','COL0000000186','J0WE018','J0WE111']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Widowed') 
        tVar.addColumns(1970,['COL0000000048','CII002','CII007','CII012','CII017','CII022','CII027','CII032','CII037','CII042','CII047','CII052','CII057','CII062','CII067'])
        tVar.addColumns(1980,['COL0000000039','C7F004','C7F009']) 
        tVar.addColumns(1990,['COL0000000045','ET6004','ET6009']) 
        tVar.addColumns(2000,['COL0000000052','GIZ003','GIZ007']) 
        tVar.addColumns(2010,['COL0000000188','J0WE065','J0WE158']) 
        allVars[-1].addRange(tVar)

        tVar=oneVariable('Divorced') 
        tVar.addColumns(1970,['COL0000000049','CII003','CII008','CII013','CII018','CII023','CII028','CII033','CII038','CII043','CII048','CII053','CII058','CII063','CII068']) 
        tVar.addColumns(1980,['COL0000000040','C7F005','C7F010'])
        tVar.addColumns(1990,['COL0000000046','ET6005','ET6010']) 
        tVar.addColumns(2000,['COL0000000051','GIZ004','GIZ008']) 
        tVar.addColumns(2010,['COL0000000187','J0WE080','J0WE173']) 
        allVars[-1].addRange(tVar)
        


    return(allVars)
