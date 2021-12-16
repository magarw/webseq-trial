import pandas as pd
import sys
import os

df1=pd.read_csv(sys.argv[1])
df2=pd.read_csv(sys.argv[2])
df3=pd.merge(df1,df2,on="Gene.refGene", how="inner")
filename1 = os.path.basename(sys.argv[1])
filename2 = os.path.basename(sys.argv[2])
df3.to_csv("{}_{}.csv".format(filename1[0:-4],filename2[0:-4]),index=False)
