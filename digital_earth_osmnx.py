# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 19:32:48 2020

@author: Peet
"""

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import pyproj

# Defináljuk a lekérdezendő területet
place_name = "XI. kerület, Budapest, Közép-Magyarország, Magyarország"

# graph_from_place - terület alapú gráflekérdezés
# Hálózat típus - biciklizhető utak 
graph = ox.graph_from_place(place_name ,network_type = 'bike' , simplify=False)

# Hálózat szűrése 
# Nem bicikliutak szűrése 
# u, v - gráf kezdő és végpontja
# k - key, OSM térképi elem key 
# d - dtype, OSM térképi elem (key=value) key értéke
non_cycleways = [(u, v, k) for u, v, k, d in graph.edges(keys=True, data=True) if not ('cycleway' in d or d['highway']=='cycleway')]
graph.remove_edges_from(non_cycleways) # élek törlése
graph.remove_nodes_from(list(nx.isolates(graph))) # szabad csúcsok törlése
graph = ox.simplify_graph(graph) # hálózat egyszerűsítése 

# Hálózat bővítése más típusú (pl. buszsávban haladó) bicikliutakkal
graph2 = ox.graph_from_place(place_name,custom_filter='["cycleway"~"opposite|opposite_lane|lane|shared_lane|shared_busway"]',simplify=True)
graph = nx.compose(graph,graph2) # gráfok egyesítése - networkx.compose

# A hálózat megjelenítése
fig1, ax = ox.plot_graph(graph,bgcolor='white',node_color='red',node_edgecolor='black',edge_color='blue')

# Befoglaló terület
area = ox.geocode_to_gdf(place_name)
#area.plot()

# Point of Interest lekérdezés a területen belül
poi = ox.geometries_from_place(place_name, tags = {'building':['university','college','transportation']})

# Hálózat GeoDataFrame (gdf) konverziója
# gráf csúcsai (nodes) és élei (edges)
nodes, edges = ox.graph_to_gdfs(graph)

# GDF plot
# Élek és POI-k  megjelenítése
fig2, ax = plt.subplots()
edges.plot(ax=ax)
poi.plot(ax=ax, facecolor = 'red')

# Hálózat vetítése HD72 rendszerbe
graph_proj = ox.project_graph(graph,to_crs=23700) 

# Élek és csúcsok leválogatása
nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)

# Hálózati statisztikák számítása
stats_basic = ox.basic_stats(graph_proj, circuity_dist='euclidean')

# A hálózat befoglaló területe
convex_hull = edges_proj.unary_union.convex_hull

# Befogadó terület számítása 
area = convex_hull.area

# Statisztikák számítása
stats = ox.basic_stats(graph_proj, area=area)
extended_stats = ox.extended_stats(graph_proj, ecc=True, cc=True)

# Alapstatisztikák kiterjesztett statisztikákkal való bővítése
for key, value in extended_stats.items():
    stats[key] = value
    
# Könyvtár Panda Series típusú változóvá alakítása
stats_pd = pd.Series(stats)

# Gráfhálózat kimentése shapefile-ba
ox.save_graph_shapefile(graph_proj,filepath='C:/Users/Peet/Documents/BME MSC/Digital Earth/XI_ker_cycleway_graph.shp')

# NetworkX hálózatelemzés
# Gráf tulajdonságok
N,K = graph.order(), graph.size()
avg_deg = float(K)/N
print ("Nodes: ", N)
print ("Edges: ", K)
print ("Average degree: ", avg_deg)

graph_ud = nx.to_undirected(graph)


