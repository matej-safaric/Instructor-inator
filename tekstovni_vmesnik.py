import model
from datetime import datetime

root = model.Root([],[],[])
def nalozi_datoteke():
    with open('uporabniki.txt', encoding='UTF-8') as dat:
        for vrstica in dat:
            atributi = vrstica.strip().split(';')
            root.uporabniki.append(model.Uporabnik((atributi[0], atributi[1]), atributi[2], atributi[3], int(atributi[4]), True if atributi[5] == 'True' else False))
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

def izbira_ukaza(ukazi: list):
    for (i, ukaz) in enumerate(ukazi):
        print(f'{i + 1}) {ukaz[0]}')
    izbira = input('> ')
    while izbira not in [str(i) for i in range(1, len(ukazi) + 1)]:
        print(f'Vnesite število med 1 in {len(ukazi)}')
        izbira = input('> ')
    return ukazi[int(izbira) - 1][1]
        
    
def prijava_instruktor(nekdo_je_prijavljen):
    username = input('Vnesite svoj username. Če želite prekiniti postopek prijave vpišite "/back"\n > ')
    if username != '/back':
        password = input('Vnesite svoje geslo\n > ')
        if root.preveri_prijavo(username, password)[0] == None:
            print('Ta račun ne obstaja.') #ustvari nov racun ali poskusi ponovno ali nazaj
            prijava(nekdo_je_prijavljen)
        elif not root.preveri_prijavo(username, password)[0].instruktor:
            print('Tu se lahko prijavijo samo inštruktorji\n') #prijava za ucence ali prijava za instruktorje ali nazaj 
            prijava(nekdo_je_prijavljen)
        elif not root.preveri_prijavo(username, password)[1]:
            print('Napačno geslo.\n') #poskusi ponovno ali nazaj 
            prijava_instruktor(nekdo_je_prijavljen)
        elif root.preveri_prijavo(username, password)[1]:
            print('Prijava uspešna\n')  #Ponudi moznost Ustvari nov racun
            nekdo_je_prijavljen = True
            homepage_prijavljen(nekdo_je_prijavljen)

#DODAJ ATRIBUT .prijavljen v uporabnike

def prijava_ucenec(nekdo_je_prijavljen):
    username = input('Vnesite svoj username. Če želite prekiniti postopek prijave vpišite "/back"\n > ')
    if username != '/back':
        password = input('Vnesite svoje geslo\n > ')
        if root.preveri_prijavo(username, password)[0] == None:
            print('Ta račun ne obstaja.')
            prijava()
        elif root.preveri_prijavo(username, password)[0].instruktor:
            print('Tu se lahko prijavijo samo učenci\n')
            prijava()
        elif not root.preveri_prijavo(username, password)[1]:
            print('Napačno geslo.\n')
            prijava_ucenec()
        elif root.preveri_prijavo(username, password)[1]:
            print('Prijava uspešna\n')
            nekdo_je_prijavljen = True
            homepage_prijavljen(nekdo_je_prijavljen)

def odjava(nekdo_je_prijavljen):
    nekdo_je_prijavljen = False
    print('Odjava je bila uspešna.')
    homepage_neprijavljen(nekdo_je_prijavljen)

def ustvari_nov_racun(nekdo_je_prijavljen):
    pass    

def nazaj():
    pass

def ogled_urnika(nekdo_je_prijavljen):
    pass

def zakljucek(nekdo_je_prijavljen):
    pass


def prijava(nekdo_je_prijavljen):
    if nekdo_je_prijavljen:
        print('Nekdo je že prijavljen v sistem. Prosimo, da se najprej odjavite iz trenutnega računa')
        homepage_prijavljen()
    else:
        izbira_ukaza([('Prijava za inštruktorje', prijava_instruktor),('Prijava za učence', prijava_ucenec),('Ustvari nov račun', ustvari_nov_racun),('Nazaj', nazaj)])(nekdo_je_prijavljen)


def tekstovni_vmesnik():
    nalozi_datoteke()
    dobrodoslica()


