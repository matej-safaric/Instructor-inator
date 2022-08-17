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

def pripravi_ure():
    trenutni_teden = datetime.today().isocalendar()[1]
    trenutno_leto = datetime.today().isocalendar()[0]
    zadnji_datum_v_sistemu = root.ure[-1].cas.date()
    print(zadnji_datum_v_sistemu)
    if zadnji_datum_v_sistemu < date.today():
        for i in range(0, 28):
            zadnji_ponedeljek = datetime.fromisocalendar(trenutno_leto, trenutni_teden, 1)
            root.ustvari_dan_praznih_ur(zadnji_ponedeljek + timedelta(days=i))
    else:
        razlika_v_tednih = abs(zadnji_datum_v_sistemu.isocalendar()[1] - trenutni_teden)
        for i in range(0, 28 - 7 * (razlika_v_tednih + 1)):
            zadnji_ponedeljek = datetime.fromisocalendar(zadnji_datum_v_sistemu.isocalendar()[0], zadnji_datum_v_sistemu.isocalendar()[1], 1)
            root.ustvari_dan_praznih_ur(zadnji_ponedeljek + timedelta(days=i))
        

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
                        dat.write(f'{priimek};{ime};{username};{password};{root.najdi_uporabnika_username(username).id}\n')
                else:
                    print('Račun je bil uspešno ustvarjen. Sedaj se lahko prijavite v sistem.')
                    homepage_neprijavljen()


def natisni_urnik():
    pass

def ogled_urnika():
    natisni_urnik()
    izbira_ukaza([('Rezerviraj uro', rezervacija), ('Prikaži moje ure', prikaz_osebnih_ur), ('Odpovej uro', odpoved), ('Nazaj', nazaj), ('Naslednji teden', naslednji_teden), ('Prejšnji teden', prejsnji_teden)])()

def potrdi_zavrni_instruktorja(uporabnik: model.Uporabnik or None):
    if uporabnik == None:
        homepage_prijavljen_instruktor()
    else:
        potrditev_ali_zavrnitev = input(f'Ali želite, da se uporabnik {uporabnik.ime_priimek[1].upper()} {uporabnik.ime_priimek[0].upper()} doda v seznam inštruktorjev? \n Vpišite DA za potrditev in NE za zavrnitev \n > ')
        if potrditev_ali_zavrnitev not in ['DA', 'NE']:
            print('Vpisati morate ali DA ali NE')
            potrdi_zavrni_instruktorja(uporabnik)
        elif potrditev_ali_zavrnitev == 'DA':
            uporabnik.instruktor = True             #DODAJ brisanje uporabnika iz seznama morebitnih instruktorjev!!!
            with open('stand-by_instruktorji.txt', encoding='UTF-8') as dat:
                vrstice = dat.readlines()
            with open('stand-by_instruktorji.txt', 'w', encoding='UTF-8') as dat:
                for vrstica in vrstice:
                    if vrstica.strip() != f'{uporabnik.ime_priimek[0]};{uporabnik.ime_priimek[1]};{uporabnik.username};{uporabnik.password};{uporabnik.id}':
                        dat.write(vrstica)
            
            with open('uporabniki.txt', encoding='UTF-8') as dat:
                vrstice = dat.readlines()
            with open('uporabniki.txt', 'w', encoding='UTF-8') as dat:
                for vrstica in vrstice:
                    if f'{uporabnik.ime_priimek[0]};{uporabnik.ime_priimek[1]};{uporabnik.username};{uporabnik.password};{uporabnik.id}' in vrstica.strip():
                        dat.write(vrstica)
                    else:
                        dat.write(f'{uporabnik.ime_priimek[0]};{uporabnik.ime_priimek[1]};{uporabnik.username};{uporabnik.password};{uporabnik.id};True\n')

            print('Sprejeto!')
        else:                                       #DODAJ txt file AKTIVNOST PROGRAMA.txt ki prepreci prijavo ce nekdo odpre se eno okno s programom
            uporabnik.instruktor = False
            with open('stand-by_instruktorji.txt', encoding='UTF-8') as dat:
                vrstice = dat.readlines()
            with open('stand-by_instruktorji.txt', 'w', encoding='UTF-8') as dat:
                for vrstica in vrstice:
                    if vrstica.strip() != f'{uporabnik.ime_priimek[0]};{uporabnik.ime_priimek[1]};{uporabnik.username};{uporabnik.password};{uporabnik.id}':
                        dat.write(vrstica)
            print('Uspešno zavrnjeno!')

def morebitni_instruktorji():
    with open('stand-by_instruktorji.txt', encoding='UTF-8') as dat:
        vrstice = dat.readlines()
    izbira = izbira_ukaza([(f'{vrstica.strip().split(";")[1]} {vrstica.strip().split(";")[0]}', root.najdi_uporabnika_id(int(vrstica.strip().split(";")[-1]))) for vrstica in vrstice] + [('Nazaj', None)])
    potrdi_zavrni_instruktorja(izbira)

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
    pripravi_ure()
    dobrodoslica()
    while True:
        if root.prijavljenost:
            homepage_prijavljen()
        else:
            homepage_neprijavljen()


tekstovni_vmesnik()