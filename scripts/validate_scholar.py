# for i, cluster in enumerate(inferred_blocks.find(query)):
#     try:
#         gid = cluster['group_id']
#         key = f'{gid["first_initial"]}{gid["last"]}'
#         name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
#         print(gid)
#         print(key)
#         print(name)
#
#         # can resolve by author.key, title, or mongo_ids
#         # use key:
#         reference_clusters = []
#         resolved = 0
#         for doc in scholar.find({'author.key' : key}):
#             reference_clusters.append([str(_id) for _id in doc['mongo_ids']])
#             resolved += 1
#         if resolved > 0:
#             print('resolved', resolved)
#
#         unique = set(s for cluster in reference_clusters for s in cluster)
#         print(unique)
#
#         print(name)
#         print(reference_clusters)
#         print(cluster['cluster_labels'])
#         shared_predictions = {k : v for k, v in cluster['cluster_labels'].items()
#                               if k in unique}
#
