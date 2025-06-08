from datetime import datetime, timedelta

class Einsatzkraft():
    def __init__(self, _id:str, _dienststellung:str, _atemschutz_tauglich:bool):
        self.id:str = _id
        self.dienststellung:str = _dienststellung
        self.atemschutz_tauglich:bool = _atemschutz_tauglich

class Fahrzeug():
    def __init__(self, _id:str):
        self.id:str = _id
        self.bezeichnung:str = ""
        self.status_3:datetime = None
        self.status_4:datetime = None
        self.anzahl_kraefte:int = 0
        self.anzahl_gf:int = 0
        self.anzahl_zf:int = 0
        self.anzahl_as:int = 0
        self.einsatzkraefte:list[Einsatzkraft] = []
    
    def add_einsatzkraft(self, _einsatzkraft:Einsatzkraft):
        self.einsatzkraefte.append(_einsatzkraft)
    
    def get_anzahl_gruppenfuehrer_stamm(self) -> int:
        # Bestimmt die Anzhal über die Stammdaten einer Einsatzkraft
        anzahl:int = 0
        for einsatzkraft in self.einsatzkraefte:
            if einsatzkraft.dienststellung == "Gruppenführer":
                anzahl+=1
        return anzahl
    
    def get_anzahl_zugfuehrer_stamm(self) -> int:
        # Bestimmt die Anzhal über die Stammdaten einer Einsatzkraft
        anzahl:int = 0
        for einsatzkraft in self.einsatzkraefte:
            if einsatzkraft.dienststellung == "Zugführer" or  einsatzkraft.dienststellung == "Verbandsführer":
                anzahl+=1
        return anzahl

    def get_status3(self):
        if type(self.status_3) == datetime:
            return self.status_3.time()
        else:
            return "-"

    def get_status4(self):
        if type(self.status_4) == datetime:
            return self.status_4.time()
        else:
            return "-"

    def get_eintreffzeit(self, _startzeit):
        if type(self.status_4) == datetime:
            return self.status_4 - _startzeit
        else:
            return "-"
    
    def get_fahrzeit(self):
        if type(self.status_3) == datetime and type(self.status_4) == datetime:
            return self.status_4 - self.status_3
    
    def get_anzahl_kraefte(self) -> int:
        return len(self.einsatzkraefte)
    
    def set_status_3(self, _status3:datetime):
        if _status3 == None:
            self.status_3 = "-"
        else:
            self.status_3 = _status3.replace(microsecond=0)
    
    def set_status_4(self, _status4:datetime):
        if _status4 == None:
            self.status_4 = "-"
        else:
            self.status_4 = _status4.replace(microsecond=0)
    
    def set_anzahl_kraefte(self, _anz_kraefte:int):
        if _anz_kraefte == None:
            self.anzahl_kraefte = 0
        else:
            self.anzahl_kraefte = _anz_kraefte
    
    def set_anzahl_zf(self, _anz_zf:int):
        if _anz_zf == None:
            self.anzahl_zf = 0
        else:
            self.anzahl_zf = _anz_zf
    
    def set_anzahl_gf(self, _anz_gf:int):
        if _anz_gf == None:
            self.anzahl_gf = 0
        else:
            self.anzahl_gf = _anz_gf
    
    def set_anzahl_as(self, _anz_as:int):
        if _anz_as == None:
            self.anzahl_as = 0
        else:
            self.anzahl_as = _anz_as
    
 

class Einsatz():
    def __init__(self, _id:str, _nr:int, _erlaueterung:str, _art:str, _start_zeit:datetime):
        self.id:str = _id
        self.nr:int = _nr
        self.stichwort:str = "-"
        self.erlaueterung:str = _erlaueterung
        self.art:str = _art
        self.ort:str = "-"
        self.plz:str = "-"
        self.strasse:str = "-"
        self.startzeit:datetime = _start_zeit
        self.list_fahrzeuge:list[Fahrzeug]=[]
    
    def add_fahrzeug(self, _fahrzeug:Fahrzeug):
        self.list_fahrzeuge.append(_fahrzeug)
    
    def add_einsatzkraft_to_fahrzeug(self, _einsatzkraft:Einsatzkraft, _id_fahrzeug:str) -> bool:
        # Methode fügt einem Fahrzeug eine Person hinzu
        # @return war das hinzufügen erfolgreich?
        isFound:bool = False
        for fahrzeug in self.list_fahrzeuge:
            if fahrzeug.id == _id_fahrzeug:
                fahrzeug.add_einsatzkraft(_einsatzkraft)
                isFound = True
        return isFound

    def get_einsatzort(self):
        return f"{self.strasse}, {self.plz} {self.ort}"
    
    def set_stichwort(self, _stichwort:str):
        if _stichwort != None:
            if "," in _stichwort:
                self.stichwort = _stichwort.split(",")[0]
            else:
                self.stichwort = _stichwort
    
    def set_adresse(self, _strasse, _plz, _ort):
        # Methode setzt die Adresse und manipuliert die Daten

        if _plz != None:
            self.plz = _plz
        
        if _ort != None:
            self.ort = _ort

        # Fall Strasse Divera
        if _strasse != None:
            if " / -" in _strasse:
                splitted = _strasse.split(",")
                self.strasse = splitted[0]
                self.plz = splitted[1].split(" ")[1]
                self.ort = splitted[1].split(" ")[2]
            else:
                self.strasse = _strasse
        
    
    
    # def correct_data(self):
    #     # Diese Methode passt die Daten an, sodass diese in die Auswertung passen
    #     # Strasse
    #     if self.strasse != None:
    #         if " / -" in self.strasse:
    #             splitted = self.strasse.split(",")
    #             self.strasse = splitted[0]
    #             self.plz = splitted[1].split(" ")[1]
    #             self.ort = splitted[1].split(" ")[2]

    #     # PLZ
    #     if self.plz != None:
    #         if not self.plz.isdigit():
    #             self.plz = "48485"
    #             self.ort = "Neuenkirchen"
        
    #     # Stichwort
    #     if self.stichwort != None:
    #         if "," in self.stichwort:
    #             self.stichwort = self.stichwort.split(",")[0]
        
        