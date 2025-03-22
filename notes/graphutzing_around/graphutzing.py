# Utilities supporting graphutzing doc.

import json
import graphviz
import requests

DEFAULT_COLLECTION = "reltest"
SERVER = "http://localhost:18983"
SOLR = f"{SERVER}/solr"

def generateViz(recs, id_highlight=[]):
    '''
    Visualize the data as a graph
    
    Nodes with id in id_ighlight will be outlined in red
    '''
    colors = {
        'subsample-of':'green',
        'analysis-of':'blue',
        'references': 'black',
    }
    g = graphviz.Digraph()
    g.attr('graph', rankdir='BT')
    for rec in recs:
        _label = f"{rec.get('id')}\n{rec.get('name_t')}"
        _color = "black"
        if rec.get('id') in id_highlight:
            _color='red'
        g.node(rec.get('id'), label=_label, color=_color)
        for rel in rec.get('related', {}):
            g.edge(
                rec.get('id'), 
                rel.get('target_s'), 
                label=rel.get('relation_type_s'),
                color=colors.get(rel.get('relation_type_s'),'black')
            )
    return g

def addField(collection_name, name, ftype="string", indexed="true", stored="true"):
    url = f"{SOLR}/{collection_name}/schema"
    data = {
        "add-field":{
            "name": name,
            "type": ftype,
            "indexed": indexed,
            "stored": stored
        }
    }
    headers = {"Content-Type":"application/json"}
    res = requests.post(url, headers=headers, data=json.dumps(data))
    print(res.text)


def createCollection(collection_name):
    url = f"{SOLR}/admin/collections"
    params = {
        "action":"CREATE",
        "name":collection_name,
        "numShards":1,
        "collection.configName":"_default",
    }
    res = requests.get(url, params=params)
    print(res.text)


def deleteCollection(collection_name):
    url = f'{SERVER}/api/c/{collection_name}'
    res = requests.delete(url)
    print(res.text)


def addDocument(doc, collection=DEFAULT_COLLECTION):
    url = f"{SOLR}/{collection}/update"
    headers = {
        "Content-type":"application/json"
    }
    add_doc = {
        "add":{
            "doc": doc
        }
    }
    data = json.dumps(add_doc, indent=2)
    params = {"commit":"true"}
    res = requests.post(url, headers=headers, data=data, params=params)
    if res.status_code != 200:
        print(res.status_code)
        print(res.text)
        return 0
    return 1
    

def query(q="*:*", fl="*", rows=100, collection=DEFAULT_COLLECTION):
    url = f"{SOLR}/{collection}/select"
    params = {
        "wt":"json",
        "omitHeader": "true",
        "q":q,
        "fl":fl,
        "rows":rows
    }
    headers = {
        "Accept": "application/json"
    }
    res = requests.get(url, params=params, headers=headers)
    return res.json()

def sendExpr(expr, collection=DEFAULT_COLLECTION):
    url = f'{SOLR}/{collection}/stream'
    headers = {
        "Accept": "application/json"
    }
    res = requests.post(url,data={"expr":expr}, headers=headers)
    return res.json()

def squery(q="*:*", fl="*", sort="id ASC", rows=100, collection=DEFAULT_COLLECTION):
    selection_method = "search"
    params = [
        f'q="{q}"',
        f'fl="{fl}"',
        f'rows={rows}',
    ]
    expr =  f'{selection_method}({collection},{",".join(params)},qt="/select")'
    return sendExpr(expr)
