import bottle
import model
from datetime import date

root = model.Root([], [], [], False, None)
print('Nalagam datoteke...')
root.nalozi_datoteke('predmeti.json', 'uporabniki.json', 'ure.json')
print('Ustvarjam ure...')
root.pripravi_ure()
print('Pripravljeno!')

@bottle.get("/")
def zacetna_stran(teden: int=date.today().isocalendar()[1]):
    try:
        pristevek_tednu = bottle.request.forms['teden']
    except:
        naslednji_teden = 0
        prejsnji_teden = 0
    instruktor_bool = bottle.request.get_cookie('instruktor_bool')
    if instruktor_bool == None:
        return bottle.template(
            'home.html',
            uporabniki=root.uporabniki,
            vrstice = root.pripravi_urnik_html_tabela(teden, root.seznam_instruktorjev()[0])
            )
    elif int(instruktor_bool):
        return bottle.template('home_instruktor.html')
    else:
        return bottle.template('home_ucenec.html')
    

@bottle.post('/prijava')
def prijava():
    username = bottle.request.forms['username']
    password = bottle.request.forms['password']
    (uporabnik, uspesnost_prijave) = root.preveri_prijavo(username, password)
    if uporabnik == None:
        return 'Ta uporabnik ne obstaja'
    elif not uspesnost_prijave:
        return 'Vpisali ste napacno geslo'
    else:
        instruktor_bool = '1' if uporabnik.instruktor else '0'
        bottle.response.set_cookie('username', username, path='/')
        bottle.response.set_cookie('instruktor_bool', instruktor_bool, path='/')
        bottle.redirect('/')

@bottle.get("/urnik")
def urnik():
    return bottle.template(
        'urnik.html',
        vrstice = root.pripravi_urnik_html_tabela(model.date.today().isocalendar()[1], root.seznam_instruktorjev()[0])
        )

@bottle.get("/urnik/<id_instruktorja: int>")
def urnik_instruktor(id_instruktorja):
    return bottle.template(
        'urnik.html',
        seznam_instruktorjev = root.seznam_instruktorjev(),
        vrstice = root.pripravi_urnik_html_tabela(model.date.today().isocalendar()[1], root.najdi_uporabnika_id(id_instruktorja))
    )

@bottle.get("/log-in")
def log_in():
    return bottle.template(
        'log-in.html'
    )

@bottle.post("/odjava")
def odjava():
    bottle.response.delete_cookie('username', path="/")
    bottle.response.delete_cookie('instruktor_bool', path="/")
    bottle.redirect("/")


@bottle.get("/")
def zacetna_stran():
    return bottle.template(
        "zacetna_stran.html",
        seznam_instruktorjev = root.seznam_instruktorjev()
        )

@bottle.get("/urnik")
def urnik():
    try:
        id_instruktorja = bottle.request.query['instruktorji']
    except KeyError:
        id_instruktorja = 1
    bottle.redirect(f"/urnik/{id_instruktorja}/{model.date.today().isocalendar()[0]}/{model.date.today().isocalendar()[1]}/")
    # return bottle.template(
    #     "urnik.html",
    #     vrstice = root.pripravi_urnik_html_tabela(model.date.today().isocalendar()[1], root.najdi_uporabnika_id(id_instruktorja)),
    #     seznam_instruktorjev = root.seznam_instruktorjev()
    # )

@bottle.get("/urnik/<id_instruktorja:int>/<leto:int>/<teden:int>/")
def urnik2(id_instruktorja, leto=model.date.today().isocalendar()[0], teden=model.date.today().isocalendar()[1]):
    return bottle.template(
        "urnik.html",
        vrstice = root.pripravi_urnik_html_tabela(leto, teden, root.najdi_uporabnika_id(id_instruktorja)),
        seznam_instruktorjev = root.seznam_instruktorjev(),
        naslednji_teden = (date.fromisocalendar(leto, teden, 1) + timedelta(weeks=1)).isocalendar()[1],
        leto_naslednjega_tedna = (date.fromisocalendar(leto, teden, 1) + timedelta(weeks=1)).isocalendar()[0],
        id_instruktorja = id_instruktorja,
        prejsnji_teden = (date.fromisocalendar(leto, teden, 1) - timedelta(weeks=1)).isocalendar()[1],
        leto_prejsnjega_tedna = (date.fromisocalendar(leto, teden, 1) - timedelta(weeks=1)).isocalendar()[0],
        instruktor_bool = bool(int(bottle.request.get_cookie('instruktor_bool'))),
    )



@bottle.get("/ustvari_predmet/")
def ustvari_predmet_form():
    return bottle.template(
        "ustvari_predmet.html",
        napaka_pri_vnosu = False,
        predmet_ze_obstaja = False
        )

@bottle.post("/ustvari_predmet/0/")
def ustvari_predmet():
    try:
        ime_predmeta = bottle.request.forms.getunicode('ime_predmeta')
        stopnja = int(bottle.request.forms['stopnja'])
        try:
            root.ustvari_predmet(ime_predmeta, stopnja)
            return f'''Predmet {ime_predmeta} je bil uspešno ustvarjen!
                <a href="/urnik/">Nazaj</a>'''
        except:
            return bottle.template(
                'ustvari_predmet.html',
                napaka_pri_vnosu = False,
                predmet_ze_obstaja = True
            )
    except KeyError:
        return bottle.template(
        "ustvari_predmet.html",
        napaka_pri_vnosu = True,
        predmet_ze_obstaja = False
        )

    
bottle.run(reloader=True, debug=True)