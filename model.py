#Root class (INS) bo class ki vsebuje vse podatke, ki so na voljo:
#   ure, uporabnike (ucence in ucitelje), predmete, ?dneve?, 
#

from dataclasses import dataclass
from datetime import datetime
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

@dataclass
class Predmet:
    ime: str
    stopnja: int
    #0 - OŠ
    #1 - SŠ
    #2 - FK
    
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

    def __str__(self):
        if self.stopnja_zasedenosti == 0:
            return f'{self.cas}: za to uro ni razpisanih instrukcij'
        elif self.stopnja_zasedenosti == 1:
            return f'{self.cas}: prost termin'
        else:
            return f'{self.cas}: {self.predmet.ime} {self.predmet.stopnja} - {self.ucenec.ime_priimek[1]} {self.ucenec.ime_priimek[0]}'

    def pocisti(self):
        self.stopnja_zasedenosti = 0
        self.predmet = None
        self.ucenec = None

        
    def razpolozi(self):
        self.stopnja_zasedenosti = 1

    def rezerviraj(self, predmet:Predmet, ucenec:Uporabnik):
        self.stopnja_zasedenosti = 2
        self.predmet = predmet
        self.ucenec = ucenec

        
@dataclass
class INS:
    ure: List[Ura]
    uporabniki: List[Uporabnik]
    predmeti: List[Predmet]

    
primer = INS(
    [
        Ura(datetime.now(), 1, Predmet('matematika', 1), Uporabnik(('Safaric', 'Matej'), 'Prof', '1234', 1, True)),
        Ura(datetime(2022, 8, 9, 8), 1, Predmet('fizika', 2), Uporabnik(('Alfi', 'Snific'), 'Ucko', '4321', 2, False))
    ],
    [
        Uporabnik(('Safaric', 'Matej'), 'Prof', '1234', 1, True),
        Uporabnik(('Alfi', 'Snific'), 'Ucko', '4321', 2, False)
    ],
    [
        Predmet('matematika', 1),
        Predmet('fizika', 2)
    ]
)

# Ustvari funkcijo ki naredi dovolj ur za en dan od 8ih do 20ih npr
# Razmisli ali je bolje dodati se en class Dan za organizacijo ur

for i in primer.ure:
    print(i)

print('\n')
primer.ure[0].spremeni_stopnjo_zasedenosti(0)

for i in primer.ure:
    print(i)



    




