import os
from dotenv import load_dotenv
from auswertung import Auswertung





if __name__ == '__main__':
    load_dotenv(dotenv_path="bsbp_auswertung/.env")
    if os.path.isfile("bsbp_auswertung/test.csv"):
        os.remove("bsbp_auswertung/test.csv")
    con = Auswertung()
    con.start_auswertung()