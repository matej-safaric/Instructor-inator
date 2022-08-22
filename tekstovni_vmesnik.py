import model
from datetime import datetime, date, timedelta
import json


root = model.Root([],[],[], False, None)

def nalozi_datoteke():
    with open('uporabniki.json', encoding='UTF-8') as dat:
        root.uporabniki.extend([model.Uporabnik.iz_slovarja(slovar) for slovar in json.load(dat)])
    with open('predmeti.json', encoding='UTF-8') as dat:
        root.predmeti.extend([model.Predmet.iz_slovarja(slovar) for slovar in json.load(dat)])
    with open('ure.json', encoding='UTF-8') as dat:
        root.ure.extend([model.Ura.iz_slovarja(slovar) for slovar in json.load(dat)])
            

def pripravi_ure():
    trenutni_teden = datetime.today().isocalendar()[1]
    trenutno_leto = datetime.today().isocalendar()[0]
    zadnji_datum_v_sistemu = root.ure[-1].cas.date()
    if zadnji_datum_v_sistemu < date.today():
        for i in range(0, 28):
            zadnji_ponedeljek = datetime.fromisocalendar(trenutno_leto, trenutni_teden, 1)
            root.ustvari_dan_praznih_ur(zadnji_ponedeljek + timedelta(days=i))
    else:
        razlika_v_tednih = abs(zadnji_datum_v_sistemu.isocalendar()[1] - trenutni_teden)
        for i in range(0, 28 - 7 * (razlika_v_tednih + 1)):
            zadnji_ponedeljek = datetime.fromisocalendar(zadnji_datum_v_sistemu.isocalendar()[0], zadnji_datum_v_sistemu.isocalendar()[1], 1)
            root.ustvari_dan_praznih_ur(zadnji_ponedeljek + timedelta(days=i))
    root.shrani_ure('ure.json')

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
    izbira = izbira_ukaza([('Prijava', prijava), ('Ogled urnika', ogled_urnika), ('Zaključek', zakljucek)])
    if izbira == ogled_urnika:
        print('Katerega inštruktorja želite?')
        instruktor = izbira_ukaza([(f'{uporabnik}', uporabnik) for uporabnik in root.uporabniki if uporabnik.instruktor])
        ogled_urnika(date.today().isocalendar()[1], instruktor)
    else: 
        izbira()

def homepage_prijavljen_ucenec():
    print('HOMEPAGE')
    print('Kaj želite storiti')
    izbira = izbira_ukaza([('Odjava', odjava), ('Ogled urnika', ogled_urnika), ('Zaključek', zakljucek)])
    if izbira == ogled_urnika:
        print('Katerega inštruktorja želite?')
        instruktor = izbira_ukaza([(f'{uporabnik}', uporabnik) for uporabnik in root.uporabniki if uporabnik.instruktor])
        ogled_urnika(date.today().isocalendar()[1], instruktor)
    else: 
        izbira()

def homepage_prijavljen_instruktor():
    print('HOMEPAGE')
    print('Kaj želite storiti')
    izbira = izbira_ukaza([('Odjava', odjava), ('Ogled urnika', ogled_urnika), ('Razpoloži ure', razpolozi_ure), ('Ustvari predmet', ustvari_predmet), ('Zaključek', zakljucek), ('Pregled morebitnih inštruktorjev', morebitni_instruktorji)])
    if izbira == ogled_urnika:
        print('Katerega inštruktorja želite?')
        instruktor = izbira_ukaza([(f'{uporabnik}', uporabnik) for uporabnik in root.uporabniki if uporabnik.instruktor])
        ogled_urnika(date.today().isocalendar()[1], instruktor)
    else:
        izbira()

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
            root.prijavljenec = root.najdi_uporabnika_username(username)
            homepage_prijavljen_instruktor()

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
            root.prijavljenec = root.najdi_uporabnika_username(username)
            homepage_prijavljen_ucenec()

def odjava():
    root.prijavljenost = False
    root.prijavljenec = None
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
            if username in [uporabnik.username for uporabnik in root.uporabniki]:
                    print('To uporabniško ime je že zasedeno. Prosimo poskusite znova.')
                    ustvari_nov_racun()
            else:
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


def natisni_urnik(teden: int, instruktor: model.Uporabnik):
    seznam_instruktorjevih_ur = [ura for ura in root.ure if ura.instruktor == instruktor]
    seznam_instruktorjevih_ur_v_tem_tednu = [ura for ura in seznam_instruktorjevih_ur if ura.cas.isocalendar()[1] == teden]
    print(f'Urnik instruktorja: {instruktor}')
    print('-----------------------------------------------------------------------------------------------------------')
    for i in range(8, 20):
        vrstica = f'| {i:>2}:00 |'
        for ura in seznam_instruktorjevih_ur_v_tem_tednu:
            if ura.cas.hour == i:
                if ura.stopnja_zasedenosti == 0:
                    vrstica += '     ###     |'
                elif ura.stopnja_zasedenosti == 1:
                    vrstica += ' prost termin |'
                else:
                    vrstica += '   zasedeno   |'
        print(vrstica)
        print('-----------------------------------------------------------------------------------------------------------')

def rezervacija_izberi_datum(predmet, instruktor):
    datum = input('Vpišite datum, v katerem bi radi rezervirali uro/ure, v obliki "YYYY-MM-DD"\nČe želite prekiniti postopek, vnesite /back\n> ')
    if datum != '/back':
        seznam_instruktorjevih_ur = [ura for ura in root.ure if ura.instruktor == instruktor]
        datum = date.fromisoformat(datum)
        ure_v_izbranem_dnevu = [ura for ura in seznam_instruktorjevih_ur if ura.cas.date() == datum]
        while True:
            ura = input('Vpišite željeno uro, tako da vnesete celo število na zaprtem intervalu od 8 do 19\nČe želite izbrati drug datum vpišite /back\n> ')
            if ura not in [str(i) for i in range(8, 20)] + ['/back']:
                print('Vnesti morate število med 8 in 19 ali /back!')
            elif ura == '/back':
                rezervacija_izberi_datum(predmet, instruktor)
            else:
                izbrana_ura = ure_v_izbranem_dnevu[int(ura) - 8]
                if izbrana_ura.stopnja_zasedenosti == 0:
                    print('Ta ura ni na voljo. Prosimo izberite drugo uro.')
                elif izbrana_ura.stopnja_zasedenosti == 2:
                    print('Ta ura je že zasedena. Prosimo izberite drugo uro.')
                else:
                    izbrana_ura.rezerviraj(predmet, root.prijavljenec)
                    print('Ura uspešno rezervirana!')
                    root.shrani_ure('ure.json')
    else:
        homepage_prijavljen_ucenec()            

def rezervacija():
    print('Izberite predmet, pri katerem želite inštrukcije.')
    predmet = izbira_ukaza([(f'{predmet}', predmet) for predmet in root.predmeti] + [('Nazaj', None)])
    if predmet != None:
        print('Izberite inštruktorja, pri katerem želite inštrukcije.')
        instruktor = izbira_ukaza([(f'{uporabnik}', uporabnik) for uporabnik in root.uporabniki if uporabnik.instruktor])
        rezervacija_izberi_datum(predmet, instruktor)
    else:
        homepage_prijavljen_ucenec()


def prikaz_osebnih_ur():
    trenuten_cas = datetime.today()
    ure_uporabnika = [ura for ura in root.ure if ura.ucenec == root.prijavljenec]
    prihajajoce_ure = [ura for ura in ure_uporabnika if ura.cas > trenuten_cas]
    pretekle_ure = [ura for ura in ure_uporabnika if ura.cas < trenuten_cas]
    print('PRIHAJAJOČE URE:\n')
    for ura in prihajajoce_ure:
        print(ura)
    print('\n')
    for ura in pretekle_ure:
        print(ura)
    print('\n')

def odpoved_ucenec():
    trenuten_cas = datetime.today()
    seznam_ur_uporabnika = [ura for ura in root.ure if ura.ucenec == root.prijavljenec]
    seznam_prihajajocih_ur = [ura for ura in seznam_ur_uporabnika if ura.cas > trenuten_cas + timedelta(days=2)]
    print('Če želite odpovedati uro, morate to storiti vsaj dva dni vnaprej.\nKatero uro bi radi odpovedali?')
    izbira = izbira_ukaza([(f'{ura}', ura) for ura in seznam_prihajajocih_ur] + [('Nazaj', None)])
    if izbira != None:
        izbira.pocisti()
        root.shrani_ure('ure.json')
        print('Ura je bila uspešno odpovedana.')

def odpoved_instruktor():
    trenuten_cas = datetime.today()
    seznam_ur_uporabnika = [ura for ura in root.ure if ura.instruktor == root.prijavljenec and ura.stopnja_zasedenosti == 2]
    seznam_prihajajocih_ur = [ura for ura in seznam_ur_uporabnika if ura.cas > trenuten_cas]
    print('Katero uro bi radi odpovedali?')
    izbira = izbira_ukaza([(f'{ura}', ura) for ura in seznam_prihajajocih_ur] + [('Nazaj', None)])
    if izbira != None:
        izbira.pocisti()
        root.shrani_ure('ure.json')
        print('Ura je bila uspešno odpovedana.')

def nazaj():
    pass

def naslednji_teden(teden, instruktor):
    ogled_urnika(teden, instruktor)

def prejsnji_teden(teden, instruktor):
    ogled_urnika(teden, instruktor)


def ogled_urnika(teden: int, instruktor: model.Uporabnik):
    natisni_urnik(teden, instruktor)
    if root.prijavljenec == None:
        izbira = izbira_ukaza([('Prijava', prijava), ('Naslednji teden', naslednji_teden), ('Prejšnji teden', prejsnji_teden), ('Nazaj', nazaj)])        
    elif root.prijavljenec.instruktor:
        izbira = izbira_ukaza([('Prikaži moje ure', prikaz_osebnih_ur), ('Odpovej uro', odpoved_instruktor), ('Naslednji teden', naslednji_teden), ('Prejšnji teden', prejsnji_teden), ('Nazaj', nazaj)])
    else:
        izbira = izbira_ukaza([('Rezerviraj uro', rezervacija), ('Prikaži moje ure', prikaz_osebnih_ur), ('Odpovej uro', odpoved_ucenec), ('Naslednji teden', naslednji_teden), ('Prejšnji teden', prejsnji_teden), ('Nazaj', nazaj)])
    if izbira == naslednji_teden:
        izbira(teden + 1, instruktor)
    elif izbira == prejsnji_teden:
        izbira(teden - 1, instruktor)
    else:
        izbira()

def ustvari_predmet():
    ime_predmeta = input('Vnesite ime predmeta\n> ')
    stopnja = input('Vnesite stopnjo predmeta\n> ')
    if stopnja not in ['OŠ', 'SŠ', 'FK']:
        print('Ta stopnja predmeta ne obstaja. Prosimo poskusite ponovno.')
        ustvari_predmet()
    else:
        root.ustvari_predmet(ime_predmeta, ['OŠ', 'SŠ', 'FK'].index(stopnja))
        root.shrani_predmete('predmeti.json')
        print('Predmet je bil uspešno ustvarjen.')


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
            
            root.shrani_uporabnike('uporabniki.json')

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

def razpolozi_ure(): 
    seznam_instruktorjevih_ur = [ura for ura in root.ure if ura.instruktor == root.prijavljenec]
    while True:
        datum = input('Vpišite datum, v katerem bi radi razpoložili ure, v obliki "YYYY-MM-DD"\nČe želite prekiniti postopek, vnesite /back\n> ')
        if datum != '/back':
            datum = date.fromisoformat(datum)
            ure_v_izbranem_dnevu = [ura for ura in seznam_instruktorjevih_ur if ura.cas.date() == datum]
            while True:
                ura = input('Vpišite željeno uro, tako da vnesete celo število na zaprtem intervalu od 8 do 19\nČe želite izbrati drug datum vpišite /back\n> ')
                if ura not in [str(i) for i in range(8, 20)].append('/back'):
                    print('Vnesti morate število med 8 in 19!') 
                else:
                    ure_v_izbranem_dnevu[int(ura) - 8].razpolozi(root.prijavljenec)
                    print('Ura je uspešno razpoložena!')
                    root.shrani_ure('ure.json')
        else:
            homepage_prijavljen_instruktor()

def zakljucek():
    root.shrani_predmete('predmeti.json')
    root.shrani_uporabnike('uporabniki.json')
    root.shrani_ure('ure.json')
    exit()


def prijava():
    if root.prijavljenost:
        print('Nekdo je že prijavljen v sistem. Prosimo, da se najprej odjavite iz trenutnega računa')
    else:
        izbira_ukaza([('Prijava za inštruktorje', prijava_instruktor),('Prijava za učence', prijava_ucenec),('Ustvari nov račun', ustvari_nov_racun),('Nazaj', homepage_neprijavljen)])()


def tekstovni_vmesnik():
    nalozi_datoteke()
    pripravi_ure()
    dobrodoslica()
    while True:
        if root.prijavljenost:
            if root.prijavljenec.instruktor:
                homepage_prijavljen_instruktor()
            else:
                homepage_prijavljen_ucenec()
        else:
            homepage_neprijavljen()


tekstovni_vmesnik()