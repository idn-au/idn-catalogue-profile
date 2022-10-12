from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class SCORES(DefinedNamespace):
    _NS = Namespace("https://linked.data.gov.au/def/scores/")

    # http://www.w3.org/2002/07/owl#Class
    Score: URIRef
    CareScore: URIRef
    FairScore: URIRef
    LcLabelsScore: URIRef
    ScoreForTime: URIRef

    # http://www.w3.org/2002/07/owl#ObjectProperty
    hasScore: URIRef
    hasScoreForTime: URIRef

    refResource: URIRef
    refTime: URIRef

    scoreValue: URIRef

    fairScoreValue: URIRef
    fairFScore: URIRef
    fairAScore: URIRef
    fairIScore: URIRef
    fairRScore: URIRef

    carScoreValue: URIRef
    careCScore: URIRef
    careAScore: URIRef
    careRScore: URIRef
    careEScore: URIRef
