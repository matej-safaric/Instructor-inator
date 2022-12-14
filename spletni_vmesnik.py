import bottle
import model
from datetime import date, timedelta, datetime




def vrni_instruktor_bool():
    return bool(int(bottle.request.get_cookie('instruktor_bool')))

def poskusi_vrniti_id_instruktorja():
    try:
        id_instruktorja = bottle.request.query['instruktorji']
    except KeyError:
        id_instruktorja = 1
    return id_instruktorja




root = model.Root([], [], [])
root.nalozi_datoteke('predmeti.json', 'uporabniki.json', 'ure.json')
root.pripravi_ure()


#Prijava-odjava
@bottle.get("/")
def zacetna_stran():
    return bottle.template(
        "zacetna_stran.html",
        uporabnik_ne_obstaja = False,
        napacno_geslo = False
        )

@bottle.post('/prijava/')
def prijava():
    username = bottle.request.forms.getunicode('username')
    password = bottle.request.forms.getunicode('password')
    (uporabnik, uspesnost_prijave) = root.preveri_prijavo(username, password)
    if uporabnik == None:
        return bottle.template(
            'zacetna_stran.html',
            uporabnik_ne_obstaja = True,
            napacno_geslo = False
            )
    elif not uspesnost_prijave:
        return bottle.template(
            'zacetna_stran.html',
            uporabnik_ne_obstaja = False,
            napacno_geslo = True
            )
    else:
        instruktor_bool = '1' if uporabnik.instruktor else '0'
        bottle.response.set_cookie('username', username, path='/')
        bottle.response.set_cookie('instruktor_bool', instruktor_bool, path='/')
        bottle.redirect('/urnik/')

@bottle.post("/odjava")
def odjava():
    bottle.response.delete_cookie('username', path="/")
    bottle.response.delete_cookie('instruktor_bool', path="/")
    bottle.redirect("/")



#Urnik
@bottle.get("/urnik/")
def urnik():
    id_instruktorja = poskusi_vrniti_id_instruktorja()
    bottle.redirect(f"/urnik/{id_instruktorja}/{model.date.today().isocalendar()[0]}/{model.date.today().isocalendar()[1]}/")

@bottle.get("/urnik/<id_instruktorja:int>/<leto:int>/<teden:int>/")
def urnik2(id_instruktorja, leto=model.date.today().isocalendar()[0], teden=model.date.today().isocalendar()[1]):
    if isinstance(bottle.request.get_cookie('username'), str):
        return bottle.template(
            "urnik.html",
            #Spremenljivke potrebne za tabelo z urnikom
            vrstice = root.pripravi_urnik_instruktorja(leto, teden, root.najdi_uporabnika_id(id_instruktorja)),
            seznam_instruktorjev = root.seznam_instruktorjev(),
            #Spremenljivke potrebne za gumbe Naslednji teden in Prejsnji teden
            naslednji_teden = (date.fromisocalendar(leto, teden, 1) + timedelta(weeks=1)).isocalendar()[1],
            leto_naslednjega_tedna = (date.fromisocalendar(leto, teden, 1) + timedelta(weeks=1)).isocalendar()[0],
            prejsnji_teden = (date.fromisocalendar(leto, teden, 1) - timedelta(weeks=1)).isocalendar()[1],
            leto_prejsnjega_tedna = (date.fromisocalendar(leto, teden, 1) - timedelta(weeks=1)).isocalendar()[0],
            #Spremenljivke potrebne za preusmeritve na druge strani
            id_instruktorja = id_instruktorja,
            instruktor_bool = vrni_instruktor_bool(),
            teden = teden,
            leto = leto,
            #Spremenljivke potrebne za prikaz datumov v tednu
            datum_ponedeljka = date.fromisocalendar(leto, teden, 1),
            datum_nedelje = date.fromisocalendar(leto, teden, 7)
        )
    else:
        return bottle.template('niste_prijavljeni.html')



#Ustvarjanje novega predmeta
@bottle.get("/ustvari_predmet/")
def ustvari_predmet_form():
    if isinstance(bottle.request.get_cookie('username'), str):
        return bottle.template(
            "ustvari_predmet.html",
            napaka_pri_vnosu = False,
            predmet_ze_obstaja = False,
            uspesnost = False,
            instruktor_bool = vrni_instruktor_bool()
            )
    else:
        return bottle.template('niste_prijavljeni.html')

@bottle.post("/ustvari_predmet/0/")
def ustvari_predmet():
    try:
        ime_predmeta = bottle.request.forms.getunicode('ime_predmeta')
        stopnja = int(bottle.request.forms['stopnja'])
        try:
            root.ustvari_predmet(ime_predmeta, stopnja)
            return bottle.template(
                'ustvari_predmet.html',
                #Boolove spremenljivke dolocajo odziv .html strani na vnesene podatke
                napaka_pri_vnosu = False,
                predmet_ze_obstaja = False,
                uspesnost = True,
                instruktor_bool = vrni_instruktor_bool()
            )
        except:
            return bottle.template(
                'ustvari_predmet.html',
                napaka_pri_vnosu = False,
                predmet_ze_obstaja = True,
                uspesnost = True,
                instruktor_bool = vrni_instruktor_bool()
            )
    except KeyError:
        return bottle.template(
        "ustvari_predmet.html",
        napaka_pri_vnosu = True,
        predmet_ze_obstaja = False,
        uspesnost = True,
        instruktor_bool = vrni_instruktor_bool()
        )



#Razpolaganje terminov 
@bottle.get("/razpolaganje/<leto:int>/<teden:int>/")
def razpolozi_ure(leto=model.date.today().isocalendar()[0], teden=model.date.today().isocalendar()[1]):
    if isinstance(bottle.request.get_cookie('username'), str):
        username_instruktorja = bottle.request.get_cookie('username')
        instruktor = root.najdi_uporabnika_username(username_instruktorja)
        return bottle.template(
            'razpolaganje.html',
            #Spremenljivka za tvorjenje tabele z urnikom
            vrstice = root.pripravi_urnik_instruktorja(leto, teden, instruktor),
            #Spremenljivke za preusmeritve na druge strani
            leto = leto,
            teden = teden,
            )
    else:
        return bottle.template('niste_prijavljeni.html')


@bottle.post("/razpolozi/")
def razpolozi():
    ure = bottle.request.forms.getall('ure')
    for ura in ure:
        root.najdi_uro(int(ura)).razpolozi()
    root.shrani_ure('ure.json')
    bottle.redirect("/urnik/")



#Odpovedovanje ur
@bottle.get("/odpoved/<leto:int>/<teden:int>/")
def odpoved_ur(leto=model.date.today().isocalendar()[0], teden=model.date.today().isocalendar()[1]):
    if isinstance(bottle.request.get_cookie('username'), str):
        username_uporabnika = bottle.request.get_cookie('username')
        uporabnik = root.najdi_uporabnika_username(username_uporabnika)
        instruktor_bool = vrni_instruktor_bool()
        return bottle.template(
            'odpoved.html',
            vrstice = root.pripravi_urnik_instruktorja(leto, teden, uporabnik) if instruktor_bool else root.pripravi_urnik_ucenca(leto, teden, uporabnik),
            leto = leto,
            teden = teden,
            instruktor_bool = instruktor_bool,
            id_instruktorja = poskusi_vrniti_id_instruktorja()
            )
    else:
        return bottle.template('niste_prijavljeni.html')

@bottle.post("/odpovej/")
def odpovej():
    ure = bottle.request.forms.getall('ure')
    try:
        izbris = bottle.request.forms['izbris']
    except:
        izbris = False
    if izbris:
        for ura in ure:
            root.najdi_uro(ura).pocisti(True)
    else:
        for ura in ure:
            root.najdi_uro(ura).pocisti(False)
    root.shrani_ure('ure.json')
    bottle.redirect("/urnik/")



#Osebne ure
@bottle.get("/osebne_ure/")
def osebne_ure():
    if isinstance(bottle.request.get_cookie('username'), str):
        uporabnik_username = bottle.request.get_cookie('username')
        uporabnik = root.najdi_uporabnika_username(uporabnik_username)
        trenuten_cas = datetime.today()
        instruktor_bool = vrni_instruktor_bool()
        if instruktor_bool:
            seznam_rezerviranih_uporabnikovih_ur = [ura for ura in root.ure if ura.instruktor == uporabnik and ura.stopnja_zasedenosti == 2]
        else:
            seznam_rezerviranih_uporabnikovih_ur = [ura for ura in root.ure if ura.ucenec == uporabnik and ura.stopnja_zasedenosti == 2]
        pretekle_ure = [ura for ura in seznam_rezerviranih_uporabnikovih_ur if ura.cas + timedelta(hours=1) <= trenuten_cas]
        prihajajoce_ure = [ura for ura in seznam_rezerviranih_uporabnikovih_ur if ura.cas + timedelta(hours=1) > trenuten_cas]
        return bottle.template(
                'osebne_ure.html',
                prihajajoce_ure = prihajajoce_ure,
                pretekle_ure = pretekle_ure,
                instruktor_bool = instruktor_bool
                )
    else:
        return bottle.template('niste_prijavljeni.html')



#Ustvarjanje novega racuna
@bottle.get('/ustvari_racun/')
def ustvari_nov_racun_form():
    return bottle.template(
        'ustvari_racun.html',
        uporabnik_ze_obstaja = False
        )

@bottle.post('/ustvari_racun/0/')
def ustvari_racun():
    ime = bottle.request.forms['ime']
    priimek = bottle.request.forms['priimek']
    username = bottle.request.forms['new_username']
    password = bottle.request.forms['new_password']
    instruktor_bool = bool(int(bottle.request.forms.getall('instruktor_bool')[0]))
    if root.ustvari_uporabnika(ime, priimek, username, password, instruktor_bool):
        bottle.response.set_cookie('username', username, path='/')
        bottle.response.set_cookie('instruktor_bool', str(int(instruktor_bool)), path='/')
        bottle.redirect('/urnik/')
    else:
        return bottle.template(
        'ustvari_racun.html',
        uporabnik_ze_obstaja = True
        )



#Rezervacija
@bottle.get('/rezervacija/<id_instruktorja:int>/<leto:int>/<teden:int>/')
def rezervacija(id_instruktorja, leto, teden):
    instruktor = root.najdi_uporabnika_id(id_instruktorja)
    return bottle.template(
        'rezervacija.html',
        vrstice = root.pripravi_urnik_instruktorja(leto, teden, instruktor),
        predmeti = root.predmeti,
        )

@bottle.post('/rezerviraj/')
def rezerviraj():
    ure = bottle.request.forms.getall('ure')
    predmet = root.najdi_predmet(bottle.request.forms['predmeti'])
    ucenec = root.najdi_uporabnika_username(bottle.request.get_cookie('username'))
    for ura in ure:
        root.najdi_uro(ura).rezerviraj(predmet, ucenec)
    root.shrani_ure('ure.json')
    bottle.redirect('/urnik/')
    


#Ostalo
@bottle.get("/cancel/")
def cancel():
    bottle.redirect("/urnik/")



bottle.run(reloader=True, debug=True)