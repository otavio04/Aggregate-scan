import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# Define o escopo de acesso
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Caminho para o seu arquivo .json de credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)

# Autentica e abre a planilha
client = gspread.authorize(creds)

# Abra pelo nome da planilha ou ID
spreadsheet = client.open("NOME DA PLANILHA")  # ou: client.open_by_key("ID_DA_PLANILHA")

# Pegue a aba desejada
worksheet = spreadsheet.worksheet("nome_da_aba")

# Converta para DataFrame
df = get_as_dataframe(worksheet, evaluate_formulas=True)

print(df.head())
