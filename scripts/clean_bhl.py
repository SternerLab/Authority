from pymongo import MongoClient
from rich.progress import track
from rich.pretty   import pprint
from rich import print

def run():
    client = MongoClient('localhost', 27017)

    bhl = client.validation.bhl
    n = bhl.count_documents({})

    # Create a pipeline to identify the duplicates
    pipeline = [
        {"$group": {"_id": "$author_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]

    # Execute the pipeline to find the duplicates
    duplicates = list(bhl.aggregate(pipeline))

    # Iterate through the duplicates and remove them
    for duplicate in track(duplicates, total=len(duplicates), description='Removing BHL duplicates'):
        author_id = duplicate["_id"]
        bhl.delete_many({"author_id": author_id})

    bhl.create_index('author_id', unique=True)

    print(f'Found {n} BHL clusters')
    for doc in track(bhl.find(), total=n):
        key = doc['author']['key']
        unique = []
        seen = set()
        ids = doc.get('mongo_ids', [])
        for cluster in ids:
            key = '-'.join(sorted(map(str, cluster)))
            if key not in seen:
                unique.append([str(i) for i in cluster])
                seen.add(key)
        bhl.update_one({'_id' : doc['_id']},
                       {'$set' : {'mongo_ids' : unique}}, True)
