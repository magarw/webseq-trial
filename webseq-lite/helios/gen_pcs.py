
###################################################################
# Script Name	  : gen_pcs.py
# Description	  : Generates PCs for ancestry visualziation
# Args          : none
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################



import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
import plotly.io as plio
import argparse

parser = argparse.ArgumentParser(description='Generate the PC plot the user queries for')
parser.add_argument('pc_num1', type=int)
parser.add_argument('pc_num2', type=int)
args = parser.parse_args()
PC1 = args.pc_num1
PC2 = args.pc_num2

df = pd.read_excel('./Datasets/20130606_sample_info.xlsx')

q = df['Sample']
r = df['Population']
df = pd.concat([q,r], axis=1)

pops = list(df['Population'].values)

eigenvecs = pd.read_csv('./Datasets/ancestry_data/merge3_pca.eigenvec', sep = ' ', header = -1)
# 'HG00096' is the first sample in 1000G.. That's how many samples the researcher uploaded.
num_samples = list(eigenvecs[0]).index('HG00096')

#and key dictionaries for 1000G Ancestry Plots.
cdict = {
'GBR':'#1eedd4', # GBR	British in England and Scotland
'TSI':'#185b7a', # TSI	Toscani in Italia
'FIN':'#4414db', # FIN	Finnish in Finland
'CEU':'#91dfb7', # CEU	Utah Residents (CEPH) with Northern and Western European Ancestry

'IBS':'#9b224a', # IBS	Iberian Population in Spain
'MXL':'#610625', # MXL	Mexican Ancestry from Los Angeles USA
'PUR':'#991404', # PUR	Puerto Ricans from Puerto Rico
'CLM':'#dc4e54', # CLM	Colombians from Medellin, Colombia
'PEL':'#cc6fca', # PEL	Peruvians from Lima, Peru

'GIH':'#196b04', # GIH	Gujarati Indian from Houston, Texas
'BEB':'#414127', # BEB	Bengali from Bangladesh
'ITU':'#60db82', # ITU	Indian Telugu from the UK
'PJL':'#8ccd0c', # PJL	Punjabi from Lahore, Pakistan
'STU':'#068b81', # STU	Sri Lankan Tamil from the UK

'CDX':'#d6b3da', # CDX	Chinese Dai in Xishuangbanna, China
'CHB':'#c59b88', # CHB	Han Chinese in Beijing, China
'CHS':'#c29d44', # CHS	Southern Han Chinese
'KHV':'#4a2014', # KHV	Kinh in Ho Chi Minh City, Vietnam
'JPT':'#44886e', # JPT	Japanese in Tokyo, Japan


'LWK':'#40E0D0', # LWK	Luhya in Webuye, Kenya
'MSL':'#F08080', # MSL	Mende in Sierra Leone
'YRI':'#4d575f', # YRI	Yoruba in Ibadan, Nigeria
'GWD':'#543252', # GWD	Gambian in Western Divisions in the Gambia
'ESN':'#4a5650', # ESN	Esan in Nigeria
'ASW':'#ef831e', # ASW	Americans of African Ancestry in SW
'ACB':'#4fd988'  # ACB	African Caribbeans in Barbados
}
key_dict = {
'GBR':'British in England and Scotland',
'TSI':'Toscani in Italia',
'FIN':'Finnish in Finland',
'CEU':'Utah Residents (CEPH) with Northern and Western European Ancestry',

'IBS':'Iberian Population in Spain',
'MXL':'Mexican Ancestry from Los Angeles USA',
'PUR':'Puerto Ricans from Puerto Rico',
'CLM':'Colombians from Medellin, Colombia',
'PEL':'Peruvians from Lima, Peru',

'GIH':'Gujarati Indian from Houston, Texas',
'BEB':'Bengali from Bangladesh',
'ITU':'Indian Telugu from the UK',
'PJL':'Punjabi from Lahore, Pakistan',
'STU':'Sri Lankan Tamil from the UK',

'CDX':'Chinese Dai in Xishuangbanna, China',
'CHB':'Han Chinese in Beijing, China',
'CHS':'Southern Han Chinese',
'KHV':'Kinh in Ho Chi Minh City, Vietnam',
'JPT':'Japanese in Tokyo, Japan',


'LWK':'Luhya in Webuye, Kenya',
'MSL':'Mende in Sierra Leone',
'YRI':'Yoruba in Ibadan, Nigeria',
'GWD':'Gambian in Western Divisions in the Gambia',
'ESN':'Esan in Nigeria',
'ASW':'Americans of African Ancestry in SW',
'ACB':'African Caribbeans in Barbados'
}


sample = eigenvecs.iloc[:num_samples,:].iloc[:,1:]
ref = pd.concat([eigenvecs.iloc[num_samples:,:][0], eigenvecs.iloc[num_samples:,:].iloc[:,2:]], axis= 1)
ref.columns = list(range(0,ref.shape[1]))
sample.columns = list(range(0, sample.shape[1]))

mask = []
for i in range(0,df.shape[0]):
    mask.append(df['Sample'][i] in list(eigenvecs[0].values))

df = df.loc[mask, :]
df = df.reset_index(drop=True)


data = []
for g in np.unique(df['Population']):
    ix = np.where(df['Population'] == g)
    trace = go.Scatter(x=ref.iloc[ix[0],PC1], y=ref.iloc[ix[0],PC2],mode = 'markers', marker=dict(color = cdict[g]),name=g, text=key_dict[g])
    data.append(trace)

for j in range(0, sample.shape[0]):
    sample_trace = go.Scatter(x = np.array(sample[PC1][j]), y = np.array(sample[PC2][j]), mode='markers',marker=dict(color = 'yellow', size = 7,line = dict(
            width = 2,
        )), name= sample[0][j], text=sample[0][j])
    data.append(sample_trace)

layout= go.Layout(
    title= 'Population Inference: Reference + Study Samples',
    hovermode= 'closest',
    xaxis= dict(
        title= 'PC ' + str(PC1),
        ticklen= 5,
        zeroline= False,
        gridwidth= 2,
    ),
    yaxis=dict(
        title= 'PC ' + str(PC2),
        ticklen= 5,
        gridwidth= 2,
    ),
)

fig= go.Figure(data=data, layout=layout)


plot_div = plot(fig, auto_open=False, filename="./static/temp-plot.html")
plio.to_html(fig)
