import bottle
import model

root = model.Root([], [], [], False, None)

root.nalozi_datoteke('predmeti.json', 'uporabniki.json', 'ure.json')

@bottle.get("/")
def zacetna_stran():
    return bottle.template('zacetna_stran.html')

bottle.run(reloader=True, debug=True)