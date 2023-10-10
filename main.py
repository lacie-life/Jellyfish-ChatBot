import re

node_1_start = "[E1]"
node_1_end = "[/E1]"

node_2_start = "[E2]"
node_2_end = "[/E2]"

i = 0


def edgeExtraction(sample):
    # print(sample)
    x = sample.replace('\t', ' ').replace('\n', '')
    tmp = x.split(" ")
    print(tmp)
    node_1 = ''
    node_1_label = ''
    node_2 = ''
    node_2_label = ''
    edge = tmp[0]

    if edge == 'OTHER':
        return

    # print(x.find(node_1_start))
    # print(x.find(node_2_start))

    if x.find(node_1_start) < x.find(node_2_start):
        node_1_label = tmp[5]
        node_2_label = tmp[6]
    else:
        node_1_label = tmp[6]
        node_2_label = tmp[5]

    node_1 = x[x.find(node_1_start) + len(node_1_start):x.find(node_1_end)]
    node_2 = x[x.find(node_2_start) + len(node_2_start):x.find(node_2_end)]

    print("index: " + str(i))
    print("edge: " + edge)
    print("node_1: " + node_1 + "| label: " + node_1_label)
    print("node_2: " + node_2 + "| label: " + node_2_label)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    f = open("train-readble.txt", "r")

    for x in f:
        if len(x) > 0:
            edgeExtraction(x)
        i = i + 1

    f.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
