#Root class (INS) bo class ki vsebuje vse podatke, ki so na voljo:
#   ure, uporabnike (ucence in ucitelje), predmete, ?dneve?, 
#

from dataclasses import dataclass
from datetime import date, datetime
import json
from typing import List







@dataclass
class Uporabnik:
    ime_priimek: tuple #oblike (priimek, ime)
    username: str
    password: str
    id: int
    instruktor: bool

    def __str__(self):
        return f'{self.ime_priimek[1]} {self.ime_priimek[0]}'

    def __repr__(self):
        return f'Uporabnik({self.ime_priimek}, {self.username}, {self.password}, {self.id}, {self.instruktor})'

    def v_slovar(self):
        return {
            'ime_priimek': self.ime_priimek,
            'username': self.username,
            'password': self.password,
            'id': self.id,
            'instruktor': self.instruktor
        }

    @staticmethod
    def iz_slovarja(slovar: dict):
        return Uporabnik(
            slovar['ime_priimek'],
            slovar['username'],
            slovar['password'],
            slovar['id'],
            slovar['instruktor']
            )

@dataclass
class Predmet:
    ime: str
    stopnja: int
    id: int
    #0 - OŠ
    #1 - SŠ
    #2 - FK
    
    def __str__(self):
        moznosti = [(0, 'OŠ'),(1, 'SŠ'),(2, 'FK')]
        for (stopnja, ime_stopnje) in moznosti:
            if self.stopnja == stopnja:
                return f'{self.ime} {ime_stopnje}'

    def __repr__(self):
        return f'Predmet({self.ime}, {self.stopnja}, {self.id})'

    def v_slovar(self):
        return {
            'ime': self.ime,
            'stopnja': self.stopnja,
            'id': self.id
        }

    @staticmethod
    def iz_slovarja(slovar: dict):
        return Predmet(
            slovar['ime'],
            slovar['stopnja'],
            slovar['id']
            )
    

@dataclass
class Ura:
    cas: datetime
    stopnja_zasedenosti: int 
    #vrednosti so stevila od 0 dalje: 
    #   0 - obstoj ure;
    #   1 - ura je razpisana
    #   2 - ura je rezervirana
    #   3 - ura je opravljena/izvedena ????
    predmet: Predmet
    ucenec: Uporabnik #ID stevilka ucencu prirejenega racuna
    instruktor: Uporabnik
    id: int

    def __str__(self):
        if self.stopnja_zasedenosti == 0:
            return f'{self.cas}: za to uro ni razpisanih instrukcij'
        elif self.stopnja_zasedenosti == 1:
            return f'{self.cas}: prost termin'
        else:
            return f'{self.cas}: {self.predmet.ime} {self.predmet.stopnja} - {self.ucenec.ime_priimek[1]} {self.ucenec.ime_priimek[0]}'

    def __repr__(self):
        return(f'Ura({self.cas}, {self.stopnja_zasedenosti}, {self.predmet}, {self.ucenec}, {self.instruktor}, {self.id})')

    def v_slovar(self):
        return {
            'cas': self.cas.isoformat(),
            'stopnja_zasedenosti': self.stopnja_zasedenosti,
            'predmet': self.predmet.v_slovar() if self.predmet != None else None,
            'ucenec': self.ucenec.v_slovar() if self.ucenec != None else None,
            'instruktor': self.instruktor.v_slovar() if self.instruktor != None else None,
            'id': self.id
        }

    @staticmethod
    def iz_slovarja(slovar: dict):
        return Ura(
        datetime.fromisoformat(slovar['cas']),
        slovar['stopnja_zasedenosti'],
        Predmet.iz_slovarja(slovar['predmet']) if slovar['predmet'] != None else None,
        Uporabnik.iz_slovarja(slovar['ucenec']) if slovar['ucenec'] != None else None,
        Uporabnik.iz_slovarja(slovar['instruktor']) if slovar['instruktor'] != None else None,
        slovar['id']
        )

    def pocisti(self):
        self.stopnja_zasedenosti = 0
        self.predmet = None
        self.ucenec = None
        self.instruktor = None

    def razpolozi(self, instruktor: Uporabnik):
        self.stopnja_zasedenosti = 1
        self.instruktor = instruktor
        self.ucenec = None
        self.predmet = None

    def rezerviraj(self, predmet:Predmet, ucenec:Uporabnik, instruktor:Uporabnik):
        self.stopnja_zasedenosti = 2
        self.predmet = predmet
        self.ucenec = ucenec
        self.instruktor = instruktor

@dataclass
class Root:
    ure: List[Ura]
    uporabniki: List[Uporabnik]
    predmeti: List[Predmet]
    prijavljenost: bool
    prijavljenec: Uporabnik

    def v_slovar(self):
        return {
            'ure': [ura.v_slovar() for ura in self.ure],
            'uporabniki': [uporabnik.v_slovar() for uporabnik in self.uporabniki],
            'predmeti': [predmet.v_slovar() for predmet in self.predmeti],
            'prijavljenost': self.prijavljenost,
            'prijavljenec': self.prijavljenec.v_slovar() if self.prijavljenec != None else None
        }


        
    def v_datoteko(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump(self.v_slovar, dat, indent=4)

    def shrani_ure(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump([ura.v_slovar() for ura in self.ure], dat, indent=4)

    def shrani_uporabnike(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump([uporabnik.v_slovar() for uporabnik in self.uporabniki], dat, indent=4)

    def shrani_predmete(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump([predmet.v_slovar() for predmet in self.predmeti], dat, indent=4)

    def ustvari_prazno_uro(self, cas:datetime):
        zadnji_id = self.ure[-1].id
        self.ure.append(Ura(cas, 0, None, None, None, zadnji_id + 1))
        self.shrani_ure('ure.json')

    def ustvari_dan_praznih_ur(self, datum:date):
        zadnji_id = self.ure[-1].id
        seznam_instruktorjev = [uporabnik for uporabnik in self.uporabniki if uporabnik.instruktor]
        for i in range(8, 20):
            pretvorba_v_datetime = datetime(datum.year, datum.month, datum.day, i )
            for j, instruktor in enumerate(seznam_instruktorjev):
                self.ure.append(Ura((pretvorba_v_datetime), 0, None, None, instruktor, zadnji_id + (i - 8) * len(seznam_instruktorjev) + j))
        self.shrani_ure('ure.json')

    def ustvari_uporabnika(self, ime:str, priimek:str, username:str, password:str, instruktor_bool:bool):
        zadnji_id = self.uporabniki[-1].id
        self.uporabniki.append(Uporabnik((priimek, ime), username, password, zadnji_id + 1, instruktor_bool))
        self.shrani_uporabnike('uporabniki.json')

    def ustvari_predmet(self, ime:str, stopnja:int):
        zadnji_id = self.predmeti[-1].id
        self.predmeti.append(Predmet(ime, stopnja, zadnji_id + 1))
        self.shrani_predmete

    def najdi_uporabnika_id(self, id: int):
        for uporabnik in self.uporabniki:
            if uporabnik.id == id:
                return uporabnik

    def najdi_uporabnika_username(self, username: str):
        for uporabnik in self.uporabniki:
            if uporabnik.username == username:
                return uporabnik

    def preveri_prijavo(self, username: str, password: str):
        for uporabnik in self.uporabniki:
            if uporabnik.username == username:
                if uporabnik.password == password:
                    return (uporabnik, True)
                else:
                    return (uporabnik, False)
        return (None, False)

    def najdi_predmet(self, id: int):
        id = int(id)
        for predmet in self.predmeti:
            if predmet.id == id:
                return predmet

    def najdi_uro(self, id: int):
        id = int(id)
        for ura in self.ure:
            if ura.id == id:
                return ura 
    

# Ustvari funkcijo ki naredi dovolj ur za en dan od 8ih do 20ih npr         X
# Razmisli ali je bolje dodati se en class Dan za organizacijo ur   NE

# Podatki naj se sproti shranjujejo na zunanji file ki se prebere ob zagonu programa
# V funkciji za ustvarjanje novih ur dodaj shranjevanje ur v zunanji .txt file      X
# Razmisli/naredi enako za uporabnike in predmete
# Nadaljuj z implementacijo log-in in uporabe id-jev
# Koncaj metodo find(id)        X

# Podatki se morajo sproti shranjevati ker bo v nasprotnem primeru ob crashu vse novo izgubljeno!!!
# Ko spremenis atribut objekta se mora spremeniti tudi zapis v txt file-u
# PAZI NA ID stevilke ker se zacnejo z 1

#Preden s podatkom kaj naredis, preveri ali sploh obstaja v txt.file-u / root-u

# primer = Root(    
#     [
#         Ura(datetime(2022, 8, 9, 8), 2, Predmet('fizika', 2, 2), Uporabnik(('Alfi', 'Snific'), 'Ucko', '4321', 2, False), Uporabnik(('Safaric', 'Matej'), 'Prof', '1234', 1, True), 2),
#         Ura(datetime(1, 1, 1, 10), 0, None, None, None, 3)
#     ],
#     [
#         Uporabnik(('Safaric', 'Matej'), 'Prof', '1234', 1, True),
#         Uporabnik(('Alfi', 'Snific'), 'Ucko', '4321', 2, False)
#     ],
#     [
#         Predmet('matematika', 1, 1),
#         Predmet('fizika', 2, 2)
#     ],
#     False,
#     None
# )

# # primer = Root(
# #     [
# #         Ura(datetime(1, 1, 1, 9), 1, Predmet('matematika', 1, 1), Uporabnik(('Safaric', 'Matej'), 'Prof', '1234', 1, True), 1)
# #     ],
# #     [
# #         Uporabnik(('Safaric', 'Matej'), 'Prof', '1234', 1, True)
# #     ],
# #     [
# #         Predmet('matematika', 1, 1)
# #     ]
# #     )

# for i in primer.ure:
#     print(i)

# print('\n')
# primer.ustvari_dan_praznih_ur(date(2022,12,25))
# print('\n')
# #primer.najdi_uro(1).pocisti()
# print('\n')



# for i in primer.ure:
#     print(i)

# primer.shrani_predmete('predmeti.json')
# primer.shrani_uporabnike('uporabniki.json')
# primer.shrani_ure('ure.json')

    




