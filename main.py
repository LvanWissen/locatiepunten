from collections import defaultdict
import json
import datetime
import uuid
from unidecode import unidecode
import re

import rdflib
from rdflib import Dataset, URIRef, Literal, XSD, Namespace, RDFS, BNode, SKOS, OWL
from rdfalchemy import rdfSubject, rdfMultiple, rdfSingle

from shapely.geometry import Point, MultiPoint
from shapely import wkt

create = Namespace("https://data.create.humanities.uva.nl/")
schema = Namespace("http://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
bio = Namespace("http://purl.org/vocab/bio/0.1/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
void = Namespace("http://rdfs.org/ns/void#")
dcterms = Namespace("http://purl.org/dc/terms/")

rdflib.graph.DATASET_DEFAULT_GRAPH_ID = create
rdflib.NORMALIZE_LITERALS = False

juso = Namespace("http://rdfs.co/juso/")
qb = Namespace("http://purl.org/linked-data/cube#")
hg = Namespace("http://rdf.histograph.io/")
geo = Namespace("http://www.opengis.net/ont/geosparql#")

lp = Namespace("https://resolver.clariah.org/hisgis/lp/")
lpOnt = Namespace("https://resolver.clariah.org/hisgis/lp/ontology/")
lpGeo = Namespace("https://resolver.clariah.org/hisgis/lp/geometry/")
lpPlace = Namespace("https://resolver.clariah.org/hisgis/lp/place/")

lpAdres = Namespace("https://resolver.clariah.org/hisgis/lp/adres/")
lpStraat = Namespace("https://resolver.clariah.org/hisgis/lp/straat/")
lpBuurt = Namespace("https://resolver.clariah.org/hisgis/lp/buurt/")
lpPerceel = Namespace("https://resolver.clariah.org/hisgis/lp/perceel/")
lpSectie = Namespace("https://resolver.clariah.org/hisgis/lp/sectie/")

label2adres = dict()


class Entity(rdfSubject):
    rdf_type = URIRef('urn:entity')

    label = rdfMultiple(RDFS.label)
    name = rdfMultiple(schema.name)
    url = rdfSingle(schema.url)

    hasGeometry = rdfSingle(geo.hasGeometry)

    startDate = rdfSingle(schema.startDate)
    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)


class Geometry(Entity):
    rdf_type = geo.Geometry

    asWKT = rdfSingle(geo.asWKT)


class Huis(Entity):
    rdf_type = lpOnt.Huis

    adres = rdfMultiple(lpOnt.adres)


class Adres(Entity):
    rdf_type = lpOnt.Adres

    label = rdfSingle(RDFS.label)  # Literal
    prefLabel = rdfSingle(SKOS.prefLabel)  # Literal

    straat = rdfSingle(lpOnt.straat)  # URI
    huisnummer = rdfSingle(lpOnt.huisnummer)  # Literal
    huisnummertoevoeging = rdfSingle(lpOnt.huisnummertoevoeging)  # Literal

    buurt = rdfSingle(lpOnt.buurt)  # URI
    buurtnummer = rdfSingle(lpOnt.buurtnummer)  # Literal
    buurtnummertoevoeging = rdfSingle(lpOnt.buurtnummertoevoeging)  # Literal

    perceel = rdfSingle(lpOnt.perceel)  # URI


class Straat(Entity):
    rdf_type = lpOnt.Straat

    label = rdfSingle(RDFS.label)  # Literal


class Buurt(Entity):
    rdf_type = lpOnt.Buurt

    label = rdfSingle(RDFS.label)  # Literal


class Sectie(Entity):
    rdf_type = lpOnt.Sectie

    label = rdfSingle(RDFS.label)  # Literal


class Perceel(Entity):
    rdf_type = lpOnt.Perceel

    label = rdfSingle(RDFS.label)  # Literal

    sectie = rdfSingle(lpOnt.sectie)  # URI
    perceelnummer = rdfSingle(lpOnt.perceelnummer)  # Literal
    perceelnummertoevoeging = rdfSingle(
        lpOnt.perceelnummertoevoeging)  # Literal


def unique(*args):

    identifier = "".join(str(i) for i in args)  # order matters
    unique_id = uuid.uuid5(uuid.NAMESPACE_X500, identifier)

    return BNode(unique_id)


def getResource(*args, ns):
    identifier = "-".join(str(i) for i in args if i)  # order matters
    identifier = identifier.replace(' ', '-')
    identifier = identifier.replace('.', '')
    identifier = identifier.lower()
    identifier = unidecode(identifier)

    return ns.term(identifier)


def getAdresResource(name, years, lps):
    uniqueLabel = unidecode(name)

    name = name.replace('BUURT ', '').replace('SECTIE ', '')

    uniqueLabel = uniqueLabel.replace(' ', '-')
    uniqueLabel = uniqueLabel.replace('.', '')
    uniqueLabel = uniqueLabel.lower()

    uriLabel = re.sub(r'^(?:buurt-)|(?:sectie-)', '', uniqueLabel)

    adres = label2adres.get((uniqueLabel, years, lps))
    if adres is None:

        uri = lpAdres.term(f"{uriLabel}-{'-'.join(years)}")

        earliestBegin = Literal(f"{min(years)}-01-01", datatype=XSD.date)
        latestBegin = Literal(f"{min(years)}-12-31", datatype=XSD.date)

        earliestEnd = Literal(f"{max(years)}-01-01", datatype=XSD.date)
        latestEnd = Literal(f"{max(years)}-12-31", datatype=XSD.date)

        minYear, maxYear = min(years), max(years)
        if minYear == maxYear:
            label = f"{name} ({minYear})"
        else:
            label = f"{name} ({minYear}-{maxYear})"

        adres = Adres(
            uri,
            #   hasEarliestBeginTimeStamp=earliestBegin,
            hasLatestBeginTimeStamp=latestBegin,
            hasEarliestEndTimeStamp=earliestEnd,
            #   hasLatestEndTimeStamp=latestEnd,
            label=label,
            prefLabel=name)

        label2adres[(uniqueLabel, years, lps)] = adres

    return adres


def getAdres(adresData, label, point2wkt):

    # years = [int(i) for i in adresData.keys()]
    # earliestBegin = Literal(f"{min(years)}-01-01", datatype=XSD.date)
    # latestBegin = Literal(f"{min(years)}-12-31", datatype=XSD.date)

    # earliestEnd = Literal(f"{max(years)}-01-01", datatype=XSD.date)
    # latestEnd = Literal(f"{max(years)}-12-31", datatype=XSD.date)

    # adres = Adres(getAdresUri(label),
    #               hasEarliestBeginTimeStamp=earliestBegin,
    #               hasLatestBeginTimeStamp=latestBegin,
    #               hasEarliestEndTimeStamp=earliestEnd,
    #               hasLatestEndTimeStamp=latestEnd)

    years = tuple(sorted(adresData.keys()))

    addresses = []
    for year, data in adresData.items():

        points = []
        for lp in data['geometry']:
            lp = str(lp)
            point = Point(wkt.loads(point2wkt[lp]))
            points.append((lp, point))

        lps, geoms = zip(*points)

        if len(lps) > 1:
            p = MultiPoint(points=geoms).to_wkt()
        else:
            p = geoms[0].to_wkt()
        wktLiteral = Literal(p, datatype=geo.wktLiteral)

        adres = getAdresResource(label, years, lps)

        for lp in lps:
            huis = Huis(lpPlace.term(lp))
            huis.adres = [adres]

        geometry = Geometry(lpGeo.term("-".join(lps)),
                            asWKT=wktLiteral,
                            label=lps)

        adres.hasGeometry = geometry

        if year in ['1943', '1909', '1876']:

            if straatnaam := data['straat']['naam']:
                straatUri = URIRef(
                    data['straat']['adamlink']
                ) if data['straat']['adamlink'] else getResource(straatnaam,
                                                                 ns=lpStraat)
                adres.straat = Straat(straatUri, label=straatnaam)

            if huisnummer := data['huisnummer']:
                adres.huisnummer = huisnummer
            if huisnummertoevoeging := data['huisnummertoevoeging']:
                adres.huisnummer = huisnummertoevoeging

        if year in ['1876', '1853']:

            if buurtnaam := data['buurt']['naam']:
                buurtUri = URIRef(
                    data['buurt']['adamlink']
                ) if data['buurt']['adamlink'] else getResource(buurtnaam,
                                                                ns=lpBuurt)
                adres.buurt = Buurt(buurtUri, label=buurtnaam)

            if year == '1853':

                if buurtnummer := data['buurtnummer']:
                    adres.buurtnummer = buurtnummer
                if buurtnummertoevoeging := data['buurtnummertoevoeging']:
                    adres.buurtnummer = buurtnummertoevoeging

        if year in ['1832']:

            perceelsectie = data['perceelsectie']
            sectie = Sectie(getResource(perceelsectie, ns=lpSectie),
                            label=perceelsectie)

            perceelnummer = data['perceelnummer']
            perceelnummertoevoeging = data['perceelnummertoevoeging']

            perceelLabel = " ".join([
                str(i) for i in
                [perceelsectie, perceelnummer, perceelnummertoevoeging] if i
            ])
            perceel = Perceel(getResource(perceelsectie,
                                          perceelnummer,
                                          perceelnummertoevoeging,
                                          ns=lpPerceel),
                              perceelnummer=perceelnummer,
                              perceelnummertoevoeging=perceelnummertoevoeging,
                              sectie=sectie,
                              label=perceelLabel)

            adres.perceel = perceel

        addresses.append(adres)

    return addresses


def main(source, target, geometryfile='data/point2wkt.json'):
    with open(source) as infile:
        data = json.load(infile)

    with open(geometryfile) as infile:
        point2wkt = json.load(infile)

    ds = Dataset()
    dataset = lp.term('')

    g = rdfSubject.db = ds.graph(identifier=lp)

    ### Custom triples / Ontology

    g.add((lpOnt.Adres, OWL.equivalentClass, schema.PostalAddress))

    g.add((lpOnt.Straat, OWL.equivalentClass, hg.Street))
    g.add((lpOnt.Buurt, OWL.equivalentClass, hg.Neighbourhood))

    ########
    # Data #
    ########

    adres2locatie = defaultdict(lambda: defaultdict(list))

    for n, adresLabel in enumerate(data, 1):

        if n % 5000 == 0:
            print(f"{n}/{len(data)}", end='\r')
            # break

        # # geometry
        # wkt = point2wkt.get(locatiepunt)

        # wktLiteral = Literal(wkt, datatype=geo.wktLiteral)
        # geometry = Geometry(lpGeo.term(str(locatiepunt)),
        #                     asWKT=wktLiteral,
        #                     label=[str(locatiepunt)])

        addresses = getAdres(data[adresLabel], adresLabel, point2wkt)

        # adres2locatie[adres][year].append(geometry)

        # observations.append(locpdetail)
        # locp.observation = observations

        # addresses.append(
        #     Role(
        #         None,
        #         label=address.label,
        #         address=address,
        #         hasLatestBeginTimeStamp=locpdetail.hasLatestBeginTimeStamp,
        #         hasEarliestEndTimeStamp=locpdetail.hasEarliestEndTimeStamp,
        #         startDate=Literal(year, datatype=XSD.gYear)))

    ds.bind('create', create)
    ds.bind('schema', schema)
    ds.bind('sem', sem)
    ds.bind('geo', geo)
    ds.bind('juso', juso)
    ds.bind('qb', qb)
    ds.bind('void', void)

    print("Serializing!")
    ds.serialize(target, format='trig')


if __name__ == "__main__":
    main(source='concordans.json', target='locatiepunten2021.trig')