import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests

class FetchData(dml.Algorithm):
    contributor = 'asafer_vivyee'
    reads = []
    writes = ['asafer_vivyee.orchards', 'asafer_vivyee.corner_stores', 'asafer_vivyee.obesity', 'asafer_vivyee.nutrition_prog', 'asafer_vivyee.mbta_routes']

    @staticmethod
    def setup():
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asafer_vivyee', 'asafer_vivyee')
        return repo

    @staticmethod
    def store(repo, url, collection):
        response = requests.get(url)
        if response.status_code == 200:
            data = [response.json()]
            repo.dropPermanent(collection)
            repo.createPermanent(collection)
            repo[collection].insert_many(data)

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets'''
        startTime = datetime.datetime.now()

        repo = FetchData.setup()

        mbta_key = dml.auth['services']['mbtadeveloperportal']['key']
        cityofboston_token = dml.auth['services']['cityofbostondataportal']['token']
        cdc_token = dml.auth['services']['cdcdataportal']['token']

        datasets = {
            'asafer_vivyee.orchards': 'https://data.cityofboston.gov/resource/8tmm-wjbw.json$$app_token=' + cityofboston_token,
            'asafer_vivyee.corner_stores': 'https://data.cityofboston.gov/resource/ybm6-m5qd.json??app_token=' + cityofboston_token,
            'asafer_vivyee.obesity': 'https://chronicdata.cdc.gov/resource/a2ye-t2pa.json??app_token=' + cdc_token,
            'asafer_vivyee.nutrition_prog': 'https://data.cityofboston.gov/resource/ahjc-pw5e.json??app_token=' + cityofboston_token,
            'asafer_vivyee.mbta_routes': 'http://realtime.mbta.com/developer/api/v2/routes?api_key=' + mbta_key + '&format=json'
        }

        for collection, url in datasets.items():
            FetchData.store(repo, url, collection)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # IDK WHAT ANY OF THIS DOES LOLLLLLLL
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asafer_vivyee', 'asafer_vivyee')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        doc.add_namespace('cdc', 'https://chronicdata.cdc.gov/resource/') # CDC API
        doc.add_namespace('mbta', 'http://realtime.mbta.com/developer/api/v2/r') # MBTA API

        this_script = doc.agent('alg:asafer_vivyee#data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        orchards_resource = doc.entity('bdp:8tmm-wjbw', {'prov:label': 'Urban Orchard Locations', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        corner_stores_resource = doc.entity('bdp:ybm6-m5qd', {'prov:label': 'Healthy Corner Store Locations', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        obesity_resource = doc.entity('cdc:a2ye-t2pa', {'prov:label': 'Obesity Among Adults', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        nutrition_prog_resource = doc.entity('bdp:ahjc-pw5e', {'prov:label': 'Community Culinary and Nutrition Programs', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension': 'json'})
        mbta_routes_resource = doc.entity('mbta:routes', {'prov:label': 'MBTA Routes', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})

        get_orchards = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_corner_stores = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_obesity = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime) # LOL
        get_nutrition_prog = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_mbta_routes = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_orchards, this_script)
        doc.wasAssociatedWith(get_corner_stores, this_script)
        doc.wasAssociatedWith(get_obesity, this_script)
        doc.wasAssociatedWith(get_nutrition_prog, this_script)
        doc.wasAssociatedWith(get_mbta_routes, this_script)

        doc.usage(get_orchards, orchards_resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.usage(get_corner_stores, corner_stores_resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.usage(get_obesity, obesity_resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.usage(get_nutrition_prog, nutrition_prog_resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.usage(get_mbta_routes, mbta_routes_resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})

        orchards = doc.entity('dat:asafer_vivyee#orchards', {prov.model.PROV_LABEL:'Urban Orchard Locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(orchards, this_script)
        doc.wasGeneratedBy(orchards, get_orchards, endTime)
        doc.wasDerivedFrom(orchards, orchards_resource, get_orchards, get_orchards, get_orchards)

        corner_stores = doc.entity('dat:asafer_vivyee#corner_stores', {prov.model.PROV_LABEL:'Healthy Corner Store Locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(corner_stores, this_script)
        doc.wasGeneratedBy(corner_stores, get_corner_stores, endTime)
        doc.wasDerivedFrom(corner_stores, corner_stores_resource, get_corner_stores, get_corner_stores, get_corner_stores)

        obesity = doc.entity('dat:asafer_vivyee#obesity', {prov.model.PROV_LABEL:'Obesity Among Adults', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(obesity, this_script)
        doc.wasGeneratedBy(obesity, get_obesity, endTime)
        doc.wasDerivedFrom(obesity, obesity_resource, get_obesity, get_obesity, get_obesity)

        nutrition_prog = doc.entity('dat:asafer_vivyee#nutrition_prog', {prov.model.PROV_LABEL:'Community Culinary and Nutrition Programs', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nutrition_prog, this_script)
        doc.wasGeneratedBy(nutrition_prog, get_nutrition_prog, endTime)
        doc.wasDerivedFrom(nutrition_prog, nutrition_prog_resource, get_nutrition_prog, get_nutrition_prog, get_nutrition_prog)

        mbta_routes = doc.entity('dat:asafer_vivyee#mbta_routes', {prov.model.PROV_LABEL:'MBTA Routes', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(mbta_routes, this_script)
        doc.wasGeneratedBy(mbta_routes, get_mbta_routes, endTime)
        doc.wasDerivedFrom(mbta_routes, mbta_routes_resource, get_mbta_routes, get_mbta_routes, get_mbta_routes)

        repo.logout()

        return doc

FetchData.execute()
doc = FetchData.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof