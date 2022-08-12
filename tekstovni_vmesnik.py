import model
from datetime import datetime


root = model.Root([],[],[], False)
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
            root.ure.append(model.Ura(datetime.fromisoformat(atributi[0]), int(atributi[1]), root.najdi_predmet(atributi[2]), root.najdi_uporabnika_id(atributi[3]), int(atributi[4])))

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

def homepage_neprijavljen():
    print('HOMEPAGE')
    print('Kaj želite storiti')
    izbira_ukaza([('Prijava', prijava), ('Ogled urnika', ogled_urnika), ('Zaključek', zakljucek)])()

def homepage_prijavljen():
    print('HOMEPAGE')
    print('Kaj želite storiti')
    izbira_ukaza([('Odjava', odjava), ('Ogled urnika', ogled_urnika), ('Zaključek', zakljucek)])()

def prijava_instruktor():
    username = input('Vnesite svoj username. Če želite prekiniti postopek prijave vpišite "/back"\n > ')
    if username != '/back':
        password = input('Vnesite svoje geslo\n > ')
        if root.preveri_prijavo(username, password)[0] == None:
            print('Ta račun ne obstaja.') #ustvari nov racun ali poskusi ponovno ali nazaj
            prijava()
        elif not root.preveri_prijavo(username, password)[0].instruktor:
            print('Tu se lahko prijavijo samo inštruktorji\n') #prijava za ucence ali prijava za instruktorje ali nazaj 
            prijava()
        elif not root.preveri_prijavo(username, password)[1]:
            print('Napačno geslo.\n') #poskusi ponovno ali nazaj 
            prijava_instruktor()
        elif root.preveri_prijavo(username, password)[1]:
            print('Prijava uspešna\n')  #Ponudi moznost Ustvari nov racun
            root.prijavljenost = True
            homepage_prijavljen()

#DODAJ ATRIBUT .prijavljen v uporabnike

def prijava_ucenec():
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
            root.prijavljenost = True
            homepage_prijavljen()

def odjava():
    root.prijavljenost = False
    print('Odjava je bila uspešna.')
    homepage_neprijavljen()

def ustvari_nov_racun():
    ime = input('Vpišite svoje ime\nČe želite prekiniti postopek registracije vpišite "/back"\n > ')
    if ime != '/back':
        priimek = input('Vpišite svoj priimek\n > ')
        username = input('Vpišite željeno uporabniško ime\n > ')
        if username == '/back':
            print('To uporabniško ime ni dovoljeno. Prosimo poskusite znova.')
            ustvari_nov_racun()
        else:
            for uporabnik in root.uporabniki:
                if username == uporabnik.username:
                    print('To uporabniško ime je že zasedeno. Prosimo poskusite znova.')
                    ustvari_nov_racun()
            password = input('Vpišite željeno geslo\n > ')
            print('Ali ste učenec ali inštruktor?')
            instruktor = izbira_ukaza([('Inštruktor', True), ('Učenec', False)])
            root.ustvari_uporabnika(ime, priimek, username, password, False)
            if instruktor:
                print('Vaš inštruktorski račun je na čakanju dokler osebno ne preverimo vaših podatkov. Do takrat lahko račun uporabljate le kot učenec')
                with open('stand-by_instruktorji.txt', 'a', encoding='UTF-8') as dat:
                    dat.write(f'{priimek};{ime};{username};{password};{root.najdi_uporabnika_username(username).id};\n')


def ogled_urnika():
    pass

def zakljucek():
    exit()


def prijava():
    if root.prijavljenost:
        print('Nekdo je že prijavljen v sistem. Prosimo, da se najprej odjavite iz trenutnega računa')
        homepage_prijavljen()
    else:
        izbira_ukaza([('Prijava za inštruktorje', prijava_instruktor),('Prijava za učence', prijava_ucenec),('Ustvari nov račun', ustvari_nov_racun),('Nazaj', homepage_neprijavljen)])()


def tekstovni_vmesnik():
    nalozi_datoteke()
    dobrodoslica()
    while True:
        if root.prijavljenost:
            homepage_prijavljen()
        else:
            homepage_neprijavljen()


tekstovni_vmesnik()