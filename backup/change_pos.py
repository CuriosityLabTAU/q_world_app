import csv
import json

def get_background(filename):
    reader = csv.reader(open(filename, 'r'))
    for row in reader:
        if len(row) == 1:
            row = row[0].split('\t')
        if len(row) > 1:
            if 'background' in row[1]:
                background = [int(r) for r in row[2:]]
                background[0] -= background[2] / 2 # shift from middle to bottom-left
                background[1] -= background[3] / 2 # shift from middle to bottom-left
    return background


def get_images(filename, background, world):
    reader = csv.reader(open(filename, 'r'))
    images = {}
    for row in reader:
        if len(row) == 1:
            row = row[0].split('\t')
        if 'background' not in row[1] and row[0] == '' and row[1] != '':
            print(row)
            img_name = row[1]
            images[img_name] = [int(r) for r in row[2:]]
            images[img_name][0] -= images[img_name][2] / 2 # shift from middle to bottom-left
            images[img_name][1] += images[img_name][3] / 2 # shift from middle to bottom-left

            images[img_name][0] = float(images[img_name][0] - background[0]) / float(background[2])
            images[img_name][1] = float(images[img_name][1] - background[1]) / float(background[3])
            images[img_name][2] = float(images[img_name][2]) / float(background[2])
            images[img_name][3] = float(images[img_name][3]) / float(background[3])
    return images

images = {}
for world in range(1,6):
    filename = 'world_%d.csv' % world
    print(filename)
    background = get_background(filename)
    images['network_%d' % world] = get_images(filename, background, world)

network = json.load(open('network.json', 'r'))

for network_name, data in images.items():
    for image_name, image_pos in data.items():
        image_file = image_name + '.png'

        for network_concepts in network[network_name]['concepts'].values():
            if image_file in network_concepts['image']:
                network_concepts['pos'] = '%2.3f, %2.3f' % (image_pos[0], 1.0 - image_pos[1])
                network_concepts['size'] = '%2.3f, %2.3f' % (image_pos[2], image_pos[3])

json.dump(network, open('../items/network_new.json', 'w'), separators=(',', ':'))