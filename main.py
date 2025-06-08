import os
from dotenv import load_dotenv
from auswertung import Auswertung

path_csv:str = "bsbp_auswertung/Auswertung_Einsaetze.csv"
path_excel:str = "bsbp_auswertung/Auswertung_Einsaetze.xlsx"


if __name__ == '__main__':
    load_dotenv(dotenv_path="bsbp_auswertung/.env")
    if os.path.isfile(path_csv):
        os.remove(path_csv)
    if os.path.isfile(path_excel):
        os.remove(path_excel)
    con = Auswertung()
    con.start_auswertung()