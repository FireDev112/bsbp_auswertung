import os
import pandas as pd
from mssql import MsSQLConnector
from auswertung_classes import Einsatz, Fahrzeug, Einsatzkraft

class Auswertung():
    def __init__(self):
        # Datenbankzugang MS SQL 
        self.mssql_server  = str( os.getenv("MS_SQL_SERVER")  )
        self.mssql_uid     = str( os.getenv("MS_SQL_UID")     )
        self.mssql_pwd     = str( os.getenv("MS_SQL_PWD")     ) 
        self.mssql_db_name = str( os.getenv("MS_SQL_DB_NAME") ) 
        self.mssql_port    = str( os.getenv("MS_SQL_PORT")    )
        self.db:MsSQLConnector = MsSQLConnector(self.mssql_server, self.mssql_port, self.mssql_uid, self.mssql_pwd, self.mssql_db_name)
        self.list_of_einsaetze:list[Einsatz] = []
        self.path_csv:str = "bsbp_auswertung/Auswertung_Einsaetze.csv"
        self.path_excel:str = "bsbp_auswertung/Auswertung_Einsaetze.xlsx"


    
    def start_auswertung(self):
        # 1. Liste der Einsätze aus DB exportieren
        self.list_of_einsaetze = self.db.get_einsaetze_bsbp("2020-01-01","2025-01-01")
        # self.list_of_einsaetze = self.db.get_einsaetze_bsbp("2024-01-01","2024-01-03")
        # self.list_of_einsaetze = self.db.get_einsaetze_bsbp("2024-01-01","2025-01-03")
        # 2. Fahrzeuge zum Einsatz exportieren
        self.get_fahrzeuge_and_einsatzkraefte()
        # 3. Auswertung der Daten 
        self.write_head_to_csv()
        self.auswertung_der_daten()
        self.convert_to_excel()
    

    def get_fahrzeuge_and_einsatzkraefte(self):
        # Fragt die Fahrzeuge und Einsatzkraefte in der DB an 
        for einsatz in self.list_of_einsaetze:
            self.db.get_fahrzeuge_im_einsatz(einsatz)
            self.db.get_einsatzkraefte_im_einsatz(einsatz)
    

    def auswertung_der_daten(self):
        for einsatz in self.list_of_einsaetze:
            self.validate_data(einsatz)

    def validate_data(self, _einsatz:Einsatz) -> list[str]:
        print("\n-------------------------------------------------")
        self.write_to_csv(_einsatz)
        print(f"Stichwort: {_einsatz.stichwort}")
        print(f"Einsatzort: {_einsatz.get_einsatzort()}")
        for fzg in _einsatz.list_fahrzeuge:
            print(f"Fahrzeug: {fzg.bezeichnung}")
            time_stp = fzg.get_eintreffzeit(_einsatz.startzeit)
            fahrzeit = fzg.get_fahrzeit()
            print(f"Eintreffzeit nach Alarmierung: {time_stp}")
            print(f"Fahrzeit: {fahrzeit}\n")
            # print(f"Anfahrt und Ummziehen: {time_stp-fahrzeit}")
        print("-------------------------------------------------\n")
    

    def write_to_csv(self, _einsatz:Einsatz):
        with open(self.path_csv, "a") as file:
            # Einsatz Nr; Stichwort; Einsatzmittel; ZF; GF; AGT; FM; Strasse; PLZ; ORT; Datum; Uhrzeit; Staus3; Status4; Eintreffzeit
            for fahrzeug in _einsatz.list_fahrzeuge:
                line:str = (
                    f"{_einsatz.nr};"
                    f"{self.get_stichwort(_einsatz)};"
                    f"{fahrzeug.bezeichnung};"
                    f"{fahrzeug.anzahl_zf};"
                    f"{fahrzeug.anzahl_gf};"
                    f"{fahrzeug.anzahl_as};"
                    f"{fahrzeug.anzahl_kraefte};"
                    f"{_einsatz.strasse};"
                    f"{_einsatz.plz};"
                    f"{_einsatz.ort};"
                    f"{_einsatz.startzeit.date()};"
                    f"{_einsatz.startzeit.time()};"
                    f"{fahrzeug.get_status3()};"
                    f"{fahrzeug.get_status4()};"
                    f"{fahrzeug.get_eintreffzeit(_einsatz.startzeit)}\n"
                )
                file.write(line)
    
    def get_stichwort(self, _einsatz:Einsatz) -> str:
        if _einsatz.stichwort != None and _einsatz.stichwort != "-":
            return self.correct_stichwort( _einsatz.stichwort)
        if _einsatz.art != None and _einsatz.art != "-":
            return self.correct_stichwort( _einsatz.art)
        if _einsatz.erlaueterung != None and _einsatz.erlaueterung != "-":
            return self.correct_stichwort( _einsatz.erlaueterung)
        
        # Ansonsten: 
        return "-"
    
    def correct_stichwort(self, _wrong_stichwort:str) -> str:
        # Methode ersetzt falsche Schreibweisen für Einheitlichkeit
        corrected:str = _wrong_stichwort
        corrected = corrected.replace("Person hinter verschloss. Tür", "P_Verschlossene_Tür")
        corrected = corrected.replace("Brandmeldeanlage", "Brandmeldeanlagen")
        corrected = corrected.replace("PKW Brand", "PKW-Brand")
        corrected = corrected.replace("Tiere in Not", "Tierettung")
        corrected = corrected.replace("Öl auf Straße", "Öl_Straße")
        corrected = corrected.replace("Kleinbrand  (bis 1 C-Rohr)", "Brand_klein")
        corrected = corrected.replace("Mittelbrand (bis 3 C-Rohre)", "Brand_mittel")
        corrected = corrected.replace("Wassereinsatz", "P_Wasser/Eis")

        return corrected


    
    def write_head_to_csv(self):
         with open( self.path_csv, "a") as file:
            # Einsatz Nr; Stichwort; Einsatzmittel; ZF; GF; AGT; FM; Strasse; PLZ; ORT; Datum; Uhrzeit; Staus3; Status4; Eintreffzeit
            #Kopfzeile
            _head:str = (
                "EinsatzNr;"
                "Stichwort;"
                "Einsatzmittel;"
                "ZF;"
                "GF;"
                "AGT;"
                "FM;"
                "Strasse;"
                "PLZ;"
                "Ort;"
                "Alarm Datum;"
                "Alarm Zeit;"
                "Status3;"
                "Status4;"
                "Eintreffzeit\n"
            )
            # Header schreiben
            file.write(_head)
    
    def convert_to_excel(self):
        pass
        # read_file = pd.read_csv(self.path_csv)
        # read_file.to_excel(self.path_excel, index=None, header=True)



