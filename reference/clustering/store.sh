#!/usr/bin/env bash
for filename in "results/clusters/"*; do
    python store_clusters_to_db.py $filename;
done
