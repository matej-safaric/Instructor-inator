from dataclasses import dataclass
from datetime import date, datetime, timedelta
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
    stopnja: int    #0 - OŠ, 1 - SŠ, 2 - FK
    id: int
    
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
    predmet: Predmet
    ucenec: Uporabnik
    instruktor: Uporabnik
    id: int

    def __str__(self):
        if self.stopnja_zasedenosti == 0:
            return ''
        elif self.stopnja_zasedenosti == 1:
            return 'Prost termin'
        else:
            return 'Zasedeno'

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

    def pocisti(self, izbris: bool):
        if izbris:
            self.stopnja_zasedenosti = 0
        else:
            self.stopnja_zasedenosti = 1
        self.predmet = None
        self.ucenec = None

    def razpolozi(self):
        self.stopnja_zasedenosti = 1
        self.ucenec = None
        self.predmet = None

    def rezerviraj(self, predmet:Predmet, ucenec:Uporabnik):
        self.stopnja_zasedenosti = 2
        self.predmet = predmet
        self.ucenec = ucenec





@dataclass
class Root:
    ure: List[Ura]
    uporabniki: List[Uporabnik]
    predmeti: List[Predmet]

    #Funkcije ob zagonu programa
    def nalozi_datoteke(self, predmeti: str, uporabniki: str, ure: str):
        """Ta funkcija prenese podatke iz .json datotek v root"""
        with open(uporabniki, encoding='UTF-8') as dat:
            self.uporabniki.extend([Uporabnik.iz_slovarja(slovar) for slovar in json.load(dat)])
        with open(predmeti, encoding='UTF-8') as dat:
            self.predmeti.extend([Predmet.iz_slovarja(slovar) for slovar in json.load(dat)])
        with open(ure, encoding='UTF-8') as dat:
            self.ure.extend([Ura.iz_slovarja(slovar) for slovar in json.load(dat)])


    def ustvari_dan_praznih_ur(self, datum:date):
        '''V root doda 12 praznih ur dolgih 60min, ki skupaj tvorijo en delovni dan.'''
        zadnji_id = self.ure[-1].id
        seznam_instruktorjev = self.seznam_instruktorjev()
        for i in range(8, 20):
            pretvorba_v_datetime = datetime(datum.year, datum.month, datum.day, i )
            for j, instruktor in enumerate(seznam_instruktorjev):
                self.ure.append(Ura((pretvorba_v_datetime), 0, None, None, instruktor, zadnji_id + (i - 8) * len(seznam_instruktorjev) + j + 1))
        self.shrani_ure('ure.json')


    def pripravi_ure(self):
        """Ta funkcija zagotovi, da so ure za naslednje 4 tedne generirane ko se program zažene"""
        trenutni_teden = datetime.today().isocalendar()[1]
        trenutno_leto = datetime.today().isocalendar()[0]
        zadnji_datum_v_sistemu = self.ure[-1].cas.date()
        if zadnji_datum_v_sistemu < date.today():
            for i in range(0, 28):
                zadnji_ponedeljek = datetime.fromisocalendar(trenutno_leto, trenutni_teden, 1)
                self.ustvari_dan_praznih_ur(zadnji_ponedeljek + timedelta(days=i))
        else:
            razlika_v_tednih = abs(zadnji_datum_v_sistemu.isocalendar()[1] - trenutni_teden)
            for i in range(0, 28 - 7 * (razlika_v_tednih + 1)):
                zadnji_ponedeljek = datetime.fromisocalendar(zadnji_datum_v_sistemu.isocalendar()[0], zadnji_datum_v_sistemu.isocalendar()[1], 1)
                self.ustvari_dan_praznih_ur(zadnji_ponedeljek + timedelta(days=i, weeks=1))
        self.shrani_ure('ure.json')



    #Funkcije za pripravo html urnikov
    def pripravi_urnik_instruktorja(self, leto: int, teden: int, instruktor: Uporabnik):
        """Ta funkcija naredi seznam celic za html tabelo ki prikazuje urnik enega tedna za enega instruktorja"""
        seznam_instruktorjevih_ur = [ura for ura in self.ure if ura.instruktor.username == instruktor.username]
        seznam_instruktorjevih_ur_v_tem_tednu = [ura for ura in seznam_instruktorjevih_ur if ura.cas.isocalendar()[1] == teden and ura.cas.isocalendar()[0] == leto]
        celice_urnika = [[] for _ in range(12)]
        for i in range(8, 20):
            celice_urnika[i - 8].append(f'{i:>2}:00')
            for ura in seznam_instruktorjevih_ur_v_tem_tednu:
                if ura.cas.hour == i:
                    celice_urnika[i - 8].append(ura)
        return celice_urnika


    def pripravi_urnik_ucenca(self, leto: int, teden: int, ucenec: Uporabnik):
        '''Pripravi seznam celic za html tabelo, ki prikazuje vse rezervirane ure enega učenca'''
        seznam_ucencevih_ur = []
        for ura in self.ure:
            try:
                if ura.ucenec.username == ucenec.username:
                    seznam_ucencevih_ur.append(ura)
            except:
                continue
        seznam_ucencevih_ur_ta_teden = [ura for ura in seznam_ucencevih_ur if ura.cas.isocalendar()[1] == teden and ura.cas.isocalendar()[0] == leto]
        celice_urnika = [['', '', '', '', '', '', '', ''] for _ in range(12)]
        for i in range(8, 20):
            celice_urnika[i - 8][0] = f'{i:>2}:00'
            for j in range(1, 9):
                for ura in seznam_ucencevih_ur_ta_teden:
                    if ura.cas.hour == i and ura.cas.isocalendar()[2] == j:
                        celice_urnika[i - 8][j] = ura
        return celice_urnika


    def seznam_instruktorjev(self):
        return [uporabnik for uporabnik in self.uporabniki if uporabnik.instruktor]


    #Funkcije za shranjevanje v .json
    def shrani_ure(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump([ura.v_slovar() for ura in self.ure], dat, indent=4)

    def shrani_uporabnike(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump([uporabnik.v_slovar() for uporabnik in self.uporabniki], dat, indent=4)

    def shrani_predmete(self, datoteka: str):
        with open(datoteka, 'w', encoding='UTF-8') as dat:
            json.dump([predmet.v_slovar() for predmet in self.predmeti], dat, indent=4)


    #Funkcije za preverjanje obstoja objektov v sistemu
    def preveri_obstoj_uporabnika(self, username):
        for uporabnik in self.uporabniki:
            if uporabnik.username == username:
                return True
        return False

    def preveri_obstoj_predmeta(self, ime: str, stopnja:int):
        for predmet in self.predmeti:
            if predmet.ime.lower().strip() == ime.lower().strip() and predmet.stopnja == stopnja:
                return True
        return False 


    #Funkcije za ustvarjanje objektov
    def ustvari_uporabnika(self, ime:str, priimek:str, username:str, password:str, instruktor_bool:bool):
        if not self.preveri_obstoj_uporabnika(username):
            zadnji_id = self.uporabniki[-1].id
            self.uporabniki.append(Uporabnik((priimek, ime), username, password, zadnji_id + 1, instruktor_bool))
            self.shrani_uporabnike('uporabniki.json')
            return True
        else:
            return False

    def ustvari_predmet(self, ime:str, stopnja:int):
        if not self.preveri_obstoj_predmeta(ime, stopnja):
            zadnji_id = self.predmeti[-1].id
            self.predmeti.append(Predmet(ime, stopnja, zadnji_id + 1))
            self.shrani_predmete('predmeti.json')
        else:
            raise Exception('Predmet že obstaja')


    #Funkcije za iskanje objektov v sistemu
    def najdi_uporabnika_id(self, id: int):
        for uporabnik in self.uporabniki:
            if uporabnik.id == id:
                return uporabnik

    def najdi_uporabnika_username(self, username: str):
        for uporabnik in self.uporabniki:
            if uporabnik.username == username:
                return uporabnik

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


    #Preverjanje prijave
    def preveri_prijavo(self, username: str, password: str):
        for uporabnik in self.uporabniki:
            if uporabnik.username == username:
                if uporabnik.password == password:
                    return (uporabnik, True)
                else:
                    return (uporabnik, False)
        return (None, False)
