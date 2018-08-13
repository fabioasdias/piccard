from varConf import getVariables
from subprocess import run, PIPE

vars=getVariables(kind='CA')

for A in vars:
    print("\\subsubsection{{{0}}}".format(A.getName()))
    for v in A._vars:
        print("\\paragraph{{{0}}}".format(v.getName()))
        print("\\begin{itemize}")

        for y in sorted(v._cols.keys()):
            line="   \\item{{\\textbf{{{0}}}: ".format(y)
            for c in v._cols[y]:
                if (c==''):
                    continue
                if (c[0]=='-'):
                    line=line+" (-) "
                    cc=c[1:]
                else:
                    cc=c
                res=run(['cat *{1}*.txt | grep {0}'.format(cc,y)], shell=True, stdout=PIPE)
                if (res.returncode==0):
                    colName=res.stdout.decode('utf-8').strip().replace("      "," ").replace("     "," ").replace(";",',')
                    colName=colName[len(cc)+1:].strip()
                    line=line+" "+colName.replace('$','\\$').replace('%','\\%').replace('&','\\&')+";"
            line=line+"}"
            print(line)
        print("\\end{itemize}\n")




#vars=getVariables(kind='US')