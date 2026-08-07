
# ALERT DNW ATM 




# NOTE: sexpdata.Symbol()==string evaluates True AS DOES Symbol()==str; must check for sexpdata.Symbol first, then str
from utils import *

class MySexprParser(): # Convert .kicad_sym objects into .xml objects. 
    
    @staticmethod
    def load(sexpr_file):
        with open(sexpr_file) as fo: 
            lines = [line.strip(r"\n") for line in fo.readlines()]
            sexpression = ''.join(lines)
            sexpression = sexpdata.loads(sexpression) # Lop off the headers, which i don't care about -- now we have list of kicad symbols
            # print('ONE BIG SEXPRESSION:', sexpression)
        return sexpression
                
    @staticmethod
    def extract_symbols(sexpression): 
        symbols = []
        symbol_names = []
        for sexpr in sexpression: 
            # print("SEXPR[0]:", sexpr[0]) # symbol
            # print("STR(SEXPR[0]):", str(sexpr[0])) # symbol
            token = str(sexpr[0])
            if token == 'symbol':
                symbols.append(sexpr)
                symbol_names.append(sexpr[1])
        print('FOUND THESE SYMBOLS:', symbol_names)
        print("SYMBOLS:", symbols)
        return (symbol_names, symbols)
        
    @staticmethod
    def parse(sexpr: str, parent: etree.Element = None): 
        
        token = str(sexpr[0]) 
        print()
        print("TOKEN:", token)
        elem = None # We might not need to create a new elem; often we just add to parent's attributes
        if parent == None: 
            parent = etree.Element(token)

        strs = [s for s in sexpr[1:] if isinstance(s, str)] # sexpr[1:] needed bc sexpr[0] is something like Symbol('kicad_symbol_lib') -- and sexpdata.Symbol == str evaluates True -- but idontwanna consider the 0th here
        count = 0
        
        print("STRS", strs)
        if len(strs) == 1 : # If there is 1 string, slap its token:value pair into parent -- it doesn't need its own element
            parent.set(token, str(sexpr[1])) 
            count = 2
        elif len(strs) >= 2: # If there are 2 strings or more, we need to know the name of their keys. Then, we may give them their own element depending. For example, (at x y ) should go in parent, while (pad number style type) should have its own element)
            keys = get_keys(token)
            print("KEYS:",keys)
            if not keys: 
                pass 
            for count, s in enumerate(sexpr[1:] , start=1):
                key = keys[count-1]
                value = sexpr[count]
                print("KEY:", key , "VALUE:", value)
                parent.set(key , value )
            count += 1 
        elif len(strs) == 0: 
            print('NO STRINGS DETECTED')
            elem = etree.Element(token)
            parent.append(elem)
            count = 1
        print('COUNT:',count)
        return MySexprParser.parse(sexpr[count:], parent= parent)

sexpression = MySexprParser.load("graphics\\kicad_symbols\\STM32C092RBT6.kicad_sym")
symbol_names, symbols = MySexprParser.extract_symbols(sexpression)

syms = []
for symbol in symbols: 
    syms.append(MySexprParser.parse(symbol))

print('SYMS[0]', syms[0])

    

# parent = MySexprParser.parse(sexpression)
# print("PARENT:", parent)
# print(etree.tostring(parent, encoding=str, pretty_print = True ))
