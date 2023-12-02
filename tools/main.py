from neo4j import GraphDatabase
from tools.Neo4jAPI import *
import glob

### Entity type:
# • Organization:
# • Time
# • Product
# • Promotion
# • Regulation
# • Location
# • Price
###

### Relation type
# Affiliation
# Regulation
# Location
# Price
###

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "1234678@!")

# node_1_start = "[E1]"
# node_1_end = "[/E1]"
#
# node_2_start = "[E2]"
# node_2_end = "[/E2]"

i = 0
test_max = 100


def edgeExtraction(sample, driver, store_name):
    # print(sample)
    x = sample.replace('\t', ' ').replace('\n', '')
    tmp = x.split(" ")
    # print(tmp)
    node_1 = ''
    node_1_label = ''
    node_2 = ''
    node_2_label = ''
    edge = tmp[0]

    if edge == 'OTHER':
        return

    node_1_start = 7 + int(tmp[1])
    node_1_end = 7 + int(tmp[2])

    node_2_start = 7 + int(tmp[3])
    node_2_end = 7 + int(tmp[4])

    node_1_label = tmp[5]
    node_2_label = tmp[6]

    # print("node_1_start: " + str(node_1_start))
    # print("node_1_end: " + str(node_1_end))
    #
    # print("node_2_start: " + str(node_2_start))
    # print("node_2_end: " + str(node_2_end))

    for i1 in range(node_1_start, node_1_end + 1):
        if tmp[i1] == '7' and i1 + 1 < len(tmp):
            if tmp[i1 + 1] == '-' and tmp[i1 + 2] == 'eleven':
                node_1 = '7 - eleven'
                break
        else:
            node_1 = node_1 + tmp[i1] + " "

    for i2 in range(node_2_start, node_2_end + 1):
        if tmp[i2] == '7' and i2 + 1 < len(tmp):
            if tmp[i2 + 1] == '-' and tmp[i2 + 2] == 'eleven':
                node_2 = '7 - eleven'
                break
        else:
            node_2 = node_2 + tmp[i2] + " "

    # if store_name == 'lotte':
    #     print("index: " + str(i))
    #     print("Sample: " + sample)
    #     print("edge: " + edge)
    #     print("node_1: " + node_1 + "| label: " + node_1_label)
    #     print("node_2: " + node_2 + "| label: " + node_2_label)

    # Add to neo4j
    add_node_3(node_1_label, node_1, driver, store_name)
    add_node_3(node_2_label, node_2, driver, store_name)
    add_relation(node_1_label, node_1, edge, node_2_label, node_2, driver)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    graph_paths = "../data/Graph_Create_new/"

    paths = [f for f in glob.glob(graph_paths + "**/*.txt", recursive=True)]

    try:
        neo4j_driver = GraphDatabase.driver(URI, auth=AUTH)
        initGraph(neo4j_driver)
        # make_sense(neo4j_driver)

        paths.sort()
        print(paths)

        store_name = ['711', 'aeon', 'ciclek', 'lotte', 'top_market', 'winmart']
        store_idx = 0

        for path in paths:

            print("Create graph for: " + store_name[store_idx])
            print("Path: " + path)

            f = open(path, "r")

            for x in f:
                if len(x) > 0:
                    edgeExtraction(x, neo4j_driver, store_name[store_idx])
                i = i + 1

            f.close()
            store_idx = store_idx + 1
        neo4j_driver.close()
    except Exception as e:
        print(e)


