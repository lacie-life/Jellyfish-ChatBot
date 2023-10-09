import re

node_1_start = "[E1]"
node_1_end= "[/E1]"

node_2_start = "[E2]"
node_2_end= "[/E2]"

def edgeExtraction(sample):
    print(sample)
    x = sample.replace('\t', ' ').replace('\n', '')
    tmp = x.split(" ")
    print(tmp)
    node_1 = ''
    node_2 = ''
    edge = tmp[0]

    print(x.find(node_1_start))
    print(x.find(node_1_end))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    f = open("train-readble.txt", "r")
    edgeExtraction(f.readline())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
