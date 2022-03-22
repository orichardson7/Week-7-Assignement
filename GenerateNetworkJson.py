import pandas as pd
import networkx as nx
import json
from networkx.readwrite import json_graph

#Obtain Data
dataFrame = pd.read_csv('https://raw.githubusercontent.com/umassdgithub/Week-7-ForceLayout/main/data/data_scopus.csv')

#Fill empty publishers as Unkown
dataFrame['Publisher'] = dataFrame['Publisher'].fillna('Unknown')

#Get Publisher names
publisherNames = set(dataFrame['Publisher'].values)

#Get number of different publisher papers
numberOfPublisherPapers = dataFrame.groupby('Publisher').agg(count_col=pd.NamedAgg(column='Publisher', aggfunc="count"))

#INitialize counter and array
currentPublisher = 0
publishers = []

#iterater through publishers
for publisherName in publisherNames:
    #Can't map sizes to Unknown publishers
    if publisherName != 'Unknown':
        publisherSize = 1
        #Check if Publisher name is in publisher names. If so, get the number of papers by that publisher
        if publisherName in numberOfPublisherPapers.index:
            publisherSize = int(numberOfPublisherPapers.loc[publisherName]['count_col'])

        #Add current publisher to array with Name and Size
        publishers.append((currentPublisher, {"name": publisherName, "size": publisherSize}))
        currentPublisher += 1

links = {}
#Iterate through dataframe rows
for row in dataFrame.iterrows():
    currentPaper = row[1]

    #Split on AuthorIDs and ignore Unknown Publishers
    if ";" in currentPaper['Author(s) ID'] and currentPaper['Publisher'] != 'Unknown': 
        authorIDs = currentPaper['Author(s) ID'][:-1].split(";")

        #Iterate through each Author to create edges between publishers
        for authorID in authorIDs:
            otherPapers = dataFrame[dataFrame['Author(s) ID'].str.contains(authorID)]['Publisher'].values
            if len(otherPapers) > 0:

                #Compare ID against each other paper that includes that ID
                for otherPaper in otherPapers:
                    if otherPaper != currentPaper['Publisher'] and otherPaper != 'Unknown':
                        currentPublisher = next(x for x in publishers if x[1]['name'] == currentPaper['Publisher'])[0]
                        otherPublisher = next(x for x in publishers if x[1]['name'] == otherPaper)[0]

                        #If both publisher exist in links increase the weight, otherwise add the pair and set the weight to 1.
                        if (currentPublisher, otherPublisher) in links:
                            link = links.get((currentPublisher, otherPublisher))
                            link[2]['weight'] += 1
                        else:
                            links[(currentPublisher, otherPublisher)] = (currentPublisher, otherPublisher, {"weight": 1})
    else:
        continue

#Assign nodes and links values to our graph object
G = nx.Graph()
G.add_nodes_from(publishers)
G.add_edges_from(links.values())

#write the JSON to a file.
with open("Publisher_Network.json",'w') as f:
      json.dump(json_graph.node_link_data(G),f)