import csv
import json

def get_background(filename):
    reader = csv.reader(open(filename, 'r'))
    for row in reader:
        if len(row) > 1:
            if 'background' in row[1]:
                background = [int(r) for r in row[2:]]
    return background


def get_images(filename, background):
    reader = csv.reader(open(filename, 'r'))
    images = {}
    for row in reader:
        if 'background' not in row[1] and row[0] == '' and row[1] != '':
            images[row[1]] = [int(r) for r in row[2:]]
            images[row[1]][0] = float(images[row[1]][0]) / float(background[2])
            images[row[1]][1] = float(images[row[1]][1]) / float(background[3])
            images[row[1]][2] = float(images[row[1]][2]) / float(background[2])
            images[row[1]][3] = float(images[row[1]][3]) / float(background[3])
    return images

images = {}
for world in range(1,6):
    filename = 'world_%d.csv' % world
    background = get_background(filename)
    images['network_%d' % world] = get_images(filename, background)

network = json.load(open('network.json', 'r'))

for network_name, data in images.items():
    for image_name, image_pos in data.items():
        image_file = image_name + '.png'

        for network_concepts in network[network_name]['concepts'].values():
            if image_file in network_concepts['image']:
                network_concepts['pos'] = '%2.3f, %2.3f' % (image_pos[0], 1.0 - image_pos[1])

json.dump(network, open('network_new.json', 'w'), separators=(',', ':'))