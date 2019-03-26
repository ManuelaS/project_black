import json


def get_color(index):
    return {
        'Defect_2': '#e31a1c',
        'PASS': '#1f78b4'
    }[index[3]]


def create_links(index, value, source_zone=1):
    return {'source': 'Zone{}Position{}'.format(source_zone, index[source_zone-1]),
            'target': 'Zone{}Position{}'.format(source_zone+1, index[source_zone]),
            'value': value,
            'type': '_'.join(index),
            'color': get_color(index)}


def get_node_order(paths, zone):
    return ['Zone{}Position{}'.format(zone, n)
            for n in paths.index.get_level_values('Zone{}Position'.format(zone)).categories]


def get_nodes(paths, zone):
    return [{'id': 'Zone{}Position{}'.format(zone, n), 'title': 'P{}'.format(n)}
            for n in paths.index.get_level_values('Zone{}Position'.format(zone)).categories]


def get_group(paths, zone):
    return {
        'id': 'Zone{}'.format(zone),
        'title': 'Zone{}'.format(zone),
        'nodes': get_node_order(paths, zone),
    }


def make_sankey(data):
    paths = data.groupby(['Zone1Position', 'Zone2Position', 'Zone3Position', 'Result_Type']).size()

    with open('opportunity1_sankey.json', 'w') as f:
        json.dump({
            'nodes': get_nodes(paths, 1) + get_nodes(paths, 2) + get_nodes(paths, 3),
            'groups': [
                get_group(paths, 1),
                get_group(paths, 2),
                get_group(paths, 3),
            ],
            'links': [create_links(index, value, 1) for (index, value) in paths.iteritems()] +
                     [create_links(index, value, 2) for (index, value) in paths.iteritems()],
            'alignLinkTypes': True,
            'order': [
                [get_node_order(paths, 1)],
                [get_node_order(paths, 2)],
                [get_node_order(paths, 3)]
            ]
        }, f, indent=2)

    # npm install  svg-sankey@0.1.1
    # ./node_modules/.bin/svg-sankey ./opportunity1_sankey.json > figures/opportunity1_sankey.svg
    # Remove order at the top of .svg file
