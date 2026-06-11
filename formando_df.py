import pandas as pd
import pycountry
import re

#funções 
import re

def limpar_governo(texto):

    if pd.isna(texto):
        return None
    
    if "Government of" not in texto:
        return None

    # Remove "Government of"
    texto = re.sub(
        r"Government of\s+",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
    r"dr\s+",
    "",
    texto,
    flags=re.IGNORECASE
    )
    # Correções específicas
    texto = texto.replace("South Vietnam", "Vietnam")
    texto = texto.replace("North Vietnam", "Vietnam")
    texto = texto.replace("South Yemen", "Yemen")
    texto = texto.replace("North Yemen", "Yemen")
    texto = texto.replace("Bosnia-Herzegovina", "Bosnia and Herzegovina")
    texto = texto.replace("Turkey", "Türkiye")
    texto = texto.replace("Czechoslovakia", "Czechia")
    # Remove tudo entre parênteses
    texto = re.sub(
        r"\(.*?\)",
        "",
        texto
    )

    # Remove espaços extras
    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto



#Abrir os arquivos dos dados dos países
df_Armas_importação = pd.read_csv("API_MS.MIL.MPRT.KD_DS2_en_csv_v2_283802.csv",skiprows=4)
df_pessoal_militar = pd.read_csv("API_MS.MIL.TOTL.P1_DS2_en_csv_v2_115556.csv",skiprows=4)
df_gastos_militar = pd.read_csv("API_MS.MIL.XPND.CD_DS2_en_csv_v2_280448.csv",skiprows=4)
df_armas_exportação = pd.read_csv("API_MS.MIL.XPRT.KD_DS2_en_csv_v2_175.csv",skiprows=4)
df_pib = pd.read_csv("API_NY.GDP.MKTP.CD_DS2_en_csv_v2_280770.csv",skiprows=4)
df_forca_de_trabalho = pd.read_csv("API_SL.TLF.TOTL.IN_DS2_en_csv_v2_280800.csv",skiprows=4)
#Abrir arquivo dos conplitos mudiais
df_conflitos = pd.read_csv("UcdpPrioConflict_v26_1.csv")


#Eliminar colunas desnecessárias
df_Armas_importação = df_Armas_importação.drop(columns=["Indicator Name", "Indicator Code", "Unnamed: 70"])

df_pessoal_militar = df_pessoal_militar.drop(columns=["Indicator Name", "Indicator Code", "Unnamed: 70"])

df_gastos_militar = df_gastos_militar.drop(columns=["Indicator Name", "Indicator Code", "Unnamed: 70"])

df_armas_exportação = df_armas_exportação.drop(columns=["Indicator Name", "Indicator Code", "Unnamed: 70"])

df_pib = df_pib.drop(columns=["Indicator Name", "Indicator Code", "Unnamed: 70"])

df_forca_de_trabalho = df_forca_de_trabalho.drop(columns=["Indicator Name", "Indicator Code", "Unnamed: 70"])

#Ajustar em uma coluna os valors que está por anos
df_long_armas_importação = df_Armas_importação.melt(id_vars=["Country Name","Country Code"],var_name="Ano",value_name="Armas Importação")
df_long_pessoal_militar = df_pessoal_militar.melt(id_vars=["Country Name","Country Code"],var_name="Ano",value_name="Pessoal Militar")
df_long_gastos_militar = df_gastos_militar.melt(id_vars=["Country Name","Country Code"],var_name="Ano",value_name="Gastos_Militar")
df_long_armas_exportação = df_armas_exportação.melt(id_vars=["Country Name","Country Code"],var_name="Ano",value_name="Armas Exportaçãor")
df_long_pib = df_pib.melt(id_vars=["Country Name","Country Code"],var_name="Ano",value_name="PIB")
df_long_forca_de_trabalho = df_pib.melt(id_vars=["Country Name","Country Code"],var_name="Ano",value_name="Força de Trabalho")

#Unir as tabelas
df_base = df_long_gastos_militar.merge(df_long_armas_importação,on=["Country Name","Country Code", "Ano"], how="outer")
df_base = df_base.merge(df_long_armas_exportação,on=["Country Name","Country Code", "Ano"], how="outer")
df_base = df_base.merge(df_long_pessoal_militar,on=["Country Name","Country Code", "Ano"], how="outer")
df_base = df_base.merge(df_long_forca_de_trabalho,on=["Country Name","Country Code", "Ano"], how="outer")
df_base = df_base.merge(df_long_pib,on=["Country Name","Country Code", "Ano"], how="outer")


#Ajustar para deixar apenas os países
codigos_paises = {pais.alpha_3 for pais in pycountry.countries}
df_base = df_base[df_base["Country Code"].isin(codigos_paises)]
#print(df_base["Country Name"].unique())
#print(df_base)

df_base["Ano"] = df_base["Ano"].astype(int)

#ajustando a tabela de conflitos
#Manter apenas conflitos de 1960+
df_conflitos = df_conflitos[df_conflitos["year"] >= 1960]

# Manter apenas linhas com Government no lado a e (b ou b2)
df_conflitos = df_conflitos[
    df_conflitos["side_a"].str.contains("government", case=False, na=False) &
    df_conflitos["side_b"].str.contains("government", case=False, na=False)|
    df_conflitos["side_b_2nd"].str.contains("government", case=False, na=False)]


df_conflito_limpo = pd.DataFrame()
df_conflito_limpo['Ano'] = df_conflitos['year']
df_conflito_limpo["side_a"] = df_conflitos["side_a"].apply(limpar_governo).str.split(",")
df_conflito_limpo["side_a_2nd"] = df_conflitos["side_a_2nd"].apply(limpar_governo).str.split(",")
df_conflito_limpo["side_b"] = df_conflitos["side_b"].apply(limpar_governo).str.split(",")
df_conflito_limpo["side_b_2nd"] = df_conflitos["side_b_2nd"].apply(limpar_governo).str.split(",")
df_conflito_limpo = df_conflito_limpo.explode("side_a")
df_conflito_limpo = df_conflito_limpo.explode("side_a_2nd")
df_conflito_limpo = df_conflito_limpo.explode("side_b")
df_conflito_limpo = df_conflito_limpo.explode("side_b_2nd")


df_long_conflitos = df_conflito_limpo.melt(id_vars="Ano",var_name="side",value_name="Países")
df_conflitos_final = df_long_conflitos.loc[df_long_conflitos["Países"].notna()]
df_conflitos_final=df_conflitos_final.drop_duplicates(subset=["Ano", "Países"])

df_conflitos_final["Country Code"] = df_conflitos_final["Países"].apply(lambda row: pycountry.countries.search_fuzzy(row)[0].alpha_3)
df_conflitos_final["Conflito"] = 1
print(df_conflitos_final)

df_base = df_base.merge(df_conflitos_final[["Country Code", "Ano", "Conflito"] ],on=["Country Code", "Ano"],how="left")
df_base["Conflito"] = df_base["Conflito"].fillna(0)

print(df_base.loc[df_base["Conflito"]==1])

print(len(df_base['Ano']))