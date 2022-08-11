import model
from datetime import datetime

root = model.Root([],[],[])
def nalozi_datoteke():
    with open('uporabniki.txt', encoding='UTF-8') as dat:
        for vrstica in dat:
            atributi = vrstica.strip().split(';')
            root.uporabniki.append(model.Uporabnik((atributi[0], atributi[1]), atributi[2], atributi[3], int(atributi[4]), bool(atributi[5])))
    with open('predmeti.txt', encoding='UTF-8') as dat:
        for vrstica in dat:
            atributi = vrstica.strip().split(';')
            root.predmeti.append(model.Predmet(atributi[0], int(atributi[1]), int(atributi[2])))
    with open('ure.txt', encoding='UTF-8') as dat:
        for vrstica in dat:
            atributi = vrstica.strip().split(';')
            root.ure.append(model.Ura(datetime.fromisoformat(atributi[0]), int(atributi[1]), root.najdi_predmet(atributi[2]), root.najdi_uporabnika(atributi[3]), int(atributi[4])))

def dobrodoslica():
    print('Dobrodošli v Instructor-inator!\n')


def tekstovni_vmesnik():
    nalozi_datoteke()
    dobrodoslica()


