import sqlite3
import sys

cnx = sqlite3.connect('../database/jstor-authority.db')
cursor = cnx.cursor()

cluster_file_path = sys.argv[1]
print(cluster_file_path)

with open(cluster_file_path, 'r') as f:
    clusters = f.readlines()
#     print(clusters[10])
print(len(clusters))

create_table_query = "CREATE TABLE IF NOT EXISTS clusters_all (first_initial_last_name VARCHAR(255) NOT NULL, total_records INTEGER not null ,clusters LONGTEXT NOT NULL, total_clusters INTEGER not null, authors LONGTEXT NOT NULL, author_count INTEGER NOT NULL, CONSTRAINT PK PRIMARY KEY(first_initial_last_name))"
cursor.execute(create_table_query)

insert_query = "INSERT INTO clusters_all (first_initial_last_name , total_records, clusters, total_clusters, authors, author_count) values (?,?,?,?,?,?)"
for cluster in clusters:
#     print(cluster)
    cluster_split = cluster.split(':')
    try:
        cursor.execute(insert_query,(cluster_split[0],int(cluster_split[1]),cluster_split[2],int(cluster_split[3]),cluster_split[4],len(cluster_split[4].split(','))))
        cnx.commit()
        print("added cluster to db")
        print(cluster)
    except Exception as e:
        print("Exception while inserting cluster")
        print(str(e))
        if('UNIQUE constraint failed' in str(e)):
            print(str(e))
#             print(file)
        else:
            with open('results/exceptions.txt', 'a+') as f:
                f.write(cluster)
                f.write('\n')
            sleep(20)
            print("")

