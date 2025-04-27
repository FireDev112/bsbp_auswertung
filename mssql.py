import pyodbc
from auswertung_classes import Einsatz, Fahrzeug, Einsatzkraft

class MsSQLConnector():
    def __init__(self, _server:str, _port:str, _user:str, _password:str, _db_name:str):
        self.server:str   = _server
        self.port:str     = _port
        self.user:str     = _user
        self.password:str = _password
        self.db_name:str  = _db_name
        self.connector = None
        self.cursor = None
        # Versuchen mit der DB zu verbinden
        self.__connect_to_db__()

    
    def __connect_to_db__(self):
        # Methode versucht sich mit der Datenbank zu verbinden
        connection_string = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.db_name};'
            f'UID={self.user};'
            f'PWD={self.password};'
            f'TrustServerCertificate=yes'
        )
        try:
            self.connector =  pyodbc.connect(connection_string)
            #pymssql.connect(self.server, self.user, self.password, self.db_name)
            self.cursor = self.connector.cursor()
        except Exception as e:
            print(f"Fehler beim Verbinden mit der Datenbank! Fehler: {e}")
            exit()
    
    def get_melder(self):
        query_string =(
            'select GFU_STAMM.GFU_ZUTEIL_NAME, GFU_STAMM.GFU_TYP, GFU_REPA.GFU_REPA_KURZ, GFU_STAMM.GFU_HERST_NR '
            'from GFU_STAMM '
            'left outer join GFU_REPA on GFU_STAMM.GFU_ID = GFU_REPA.GFU_INDEX '
            'where ' 
            "GFU_STAMM.GFU_TYP = 's.Quad X15' "
            'and ' 
            'GFU_REPA.GFU_REPA_KURZ is NULL '
            'and ' 
            'GFU_STAMM.GFU_ARCHIV_DAT is NULL'
        )

        print(query_string)
        self.cursor.execute(query_string)

        for element in self.cursor:
            print(element)

    
    def get_einsaetze_bsbp(self, start_zeit:str="2020-01-01", end_zeit:str="2025-01-01") -> list[Einsatz]:
        # exportiert eine Liste von Einsaetzen im genannten Zeitraum
        list_of_einsaetze:list[Einsatz] = []
        query_string = (
            "SELECT EIN_STAMM.EIN_ID, EIN_STAMM.EIN_NR, EIN_STAMM.EIN_ALARMSTICHWORT, EIN_STAMM.EIN_ERLAEUTERUNG, EIN_STAMM.EIN_ART, EIN_STAMM.EIN_ORT_ORT, EIN_STAMM.EIN_ORT_PLZ, EIN_STAMM.EIN_ORT_STRASSE, EIN_STAMM.EIN_ZEIT_V, EIN_STAMM.EIN_NOTRUF_EING "
            "from EIN_STAMM "
            f"WHERE EIN_STAMM.EIN_ZEIT_V < '{end_zeit}' "
            f"and EIN_STAMM.EIN_ZEIT_V >= '{start_zeit}' "
            "ORDER by EIN_STAMM.EIN_NR"
        )
        try:
            self.cursor.execute(query_string)

            for einsatz in self.cursor:
                new_einsatz = Einsatz(einsatz[0], einsatz[1], einsatz[3], einsatz[4], einsatz[8])
                new_einsatz.set_stichwort(einsatz[2])
                new_einsatz.set_adresse(einsatz[7],einsatz[6],einsatz[5])
                list_of_einsaetze.append(new_einsatz)

        except Exception as e:
            print(f"Fehler beim Ausführen der Query:{query_string}\nFehler:{e}")
        
        return list_of_einsaetze

    
    def get_fahrzeuge_im_einsatz(self, _einsatz:Einsatz):
        # exportiert die beteiligten Fahrzeuge in einem Einsatz
        query_string = (
            "SELECT EIN_FZG_INDEX, EIN_FZG_BEZEICHNUNG, EIN_FZG_ZEIT_AUS, EIN_FZG_ZEIT_ADE, EIN_FZG_BESATZUNG_ANZ, EIN_FZG_ATEMSCHUTZ_ANZ, EIN_FZG_ZUGF_ANZ, EIN_FZG_GRUPPF_ANZ "
            "from EIN_FAHRZ "
            f"WHERE EIN_INDEX like '{_einsatz.id}' "
        )
        try:
            self.cursor.execute(query_string)

            for fahrzeug in self.cursor:
                new_fahrzeug = Fahrzeug(fahrzeug[0])
                new_fahrzeug.bezeichnung = fahrzeug[1]
                new_fahrzeug.set_status_3(fahrzeug[2])
                new_fahrzeug.set_status_4(fahrzeug[3])
                new_fahrzeug.set_anzahl_kraefte(fahrzeug[4])
                new_fahrzeug.set_anzahl_as(fahrzeug[5])
                new_fahrzeug.set_anzahl_zf(fahrzeug[6])
                new_fahrzeug.set_anzahl_gf(fahrzeug[7])
                _einsatz.add_fahrzeug(new_fahrzeug)

        except Exception as e:
            print(f"Fehler beim Ausführen der Query:{query_string}\nFehler:{e}")

    
    def get_einsatzkraefte_im_einsatz(self, _einsatz:Einsatz):
        # exportiert die beteiligten Einsatzkraefte im Einsatz 

        for fahrzeug in _einsatz.list_fahrzeuge:

            query_string = (
                " SELECT EIN_PERS.EIN_PER_INDEX, PER_STAMM.PER_DIENSTSTELLUNG, PER_STAMM.PER_ASU_TAUGLICH "
                "from EIN_PERS "
                "left outer join PER_STAMM on EIN_PERS.EIN_PER_INDEX = PER_STAMM.PER_ID "
                f"WHERE EIN_INDEX like '{_einsatz.id}' "
                f"AND EIN_PERS.EIN_FZG_INDEX like '{fahrzeug.id}'"
            )
            try:
                self.cursor.execute(query_string)

                for einsatzkraft in self.cursor:
                    new_einsatzkraft = Einsatzkraft(einsatzkraft[0], einsatzkraft[1], einsatzkraft[2])
                    fahrzeug.add_einsatzkraft(new_einsatzkraft)

            except Exception as e:
                print(f"Fehler beim Ausführen der Query:{query_string}\nFehler:{e}")
        


            


