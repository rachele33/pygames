#!/usr/bin/env python2.7

import sys
import xml.etree.ElementTree as et
import json

tag_layer = '{http://www.w3.org/2000/svg}g'
tag_label = '{http://www.inkscape.org/namespaces/inkscape}label'
tag_rect = '{http://www.w3.org/2000/svg}rect'
tag_path = '{http://www.w3.org/2000/svg}path'
tag_type = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}type'
tag_cx = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'
tag_cy = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'
tag_rx = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}rx'
tag_ry = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}ry'
tag_r1 = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}r1'

class s:
    ''' global state '''
    maps = []

def maps_load (ibn):
    n = 0
    while (True):
        ifn = ibn + str(n) + ".svg"
        if not map_load (ifn):
            break
        n += 1

    print(json.dumps (s.maps))

def map_load (ifn):
    global path_d

    try:
        tree = et.parse (ifn)
    except:
        return False

    root = tree.getroot ()

    found = 0
    for layer in root.iter (tag_layer):
        if layer.get (tag_label) == 'hid':
            found = 1
            break

    if 0 == found:
        print('error: can\'t locate hidden layer')
        return False

    layer_trans = (0, 0)
    tform = layer.get ('transform')
    if tform and tform.find ('translate') > -1:
        trans = eval (tform.strip ('translate'))
        layer_trans = (float (trans[0]), float (trans[1]))

    doors = {'begin': [], 'end': []}
    rects = []
    for rect in layer.iter (tag_rect):
        _id = rect.get ('id')

        rect_trans = (0, 0)
        tform = rect.get ('transform')
        if tform and tform.find ('translate') > -1:
            trans = eval (tform.strip ('translate'))
            rect_trans = (float (trans[0]), float (trans[1]))

        rect_x = int(float(rect.get ('x')) + layer_trans[0] + rect_trans[0])
        rect_y = int(float(rect.get ('y')) + layer_trans[1] + rect_trans[1])
        rect_w = int(float(rect.get ('width')))
        rect_h = int(float(rect.get ('height')))

        if (_id == 'begin') | (_id == 'end'):
            doors[_id] = {
                'pos': (rect_x, rect_y), 'siz': (rect_w, rect_h) }
        else:
            rects += [{
                'pos': (rect_x, rect_y), 'siz': (rect_w, rect_h) }]

    if doors['begin'] == [] or doors['end'] == []:
        print('error: can\'t locate doors')
        return False

    arcs = []
    for path in layer.iter (tag_path):
        if path.get (tag_type) != 'arc':
            continue

        path_trans = (0, 0)
        tform = path.get ('transform')
        if tform and tform.find ('translate') > -1:
            trans = eval (tform.strip ('translate'))
            path_trans = (float (trans[0]), float (trans[1]))

        arc_x = int(float(path.get (tag_cx)) + layer_trans[0] + path_trans[0])
        arc_y = int(float(path.get (tag_cy)) + layer_trans[1] + path_trans[1])
        arc_w = int(float(path.get (tag_rx)))
        arc_h = int(float(path.get (tag_ry)))

        arcs += [{
            'pos': (arc_x, arc_y), 'siz': (arc_w, arc_h)}]

    items = []
    for path in layer.iter (tag_path):
        if path.get (tag_type) != 'star':
            continue

        item_id = path.get ('id')
        if not item_id:
            print('missing item id')
            return False

        path_trans = (0, 0)
        tform = path.get ('transform')
        if tform and tform.find ('translate') > -1:
            trans = eval (tform.strip ('translate'))
            path_trans = (float (trans[0]), float (trans[1]))

        item_x = int(float(path.get (tag_cx)) + layer_trans[0] + path_trans[0])
        item_y = int(float(path.get (tag_cy)) + layer_trans[1] + path_trans[1])
        item_r = int(path.get (tag_r1))

        items += [{
            'id': item_id, 'pos': (item_x, item_y), 'rad': item_r}]

    beings = []
    for path in layer.iter (tag_path):
        if path.get ('id') != 'being':
            continue

        path_label = path.get (tag_label)
        if not path_label:
            print('missing being label')
            return False

        being_data = eval (path_label)
        if len (being_data) < 4:
            print('invalid being label')
            return False

        being_img_s = being_data[0]
        being_img_sets_n = being_data[1]
        being_img_len = being_data[2]
        being_path_rate = being_data[3]

        path_trans = (0, 0)
        tform = path.get ('transform')
        if tform and tform.find ('translate') > -1:
            trans = eval (tform.strip ('translate'))
            path_trans = (float (trans[0]), float (trans[1]))

        path_d = path.get ('d')
        if not path_d:
            print('missing being path')
            return False

        path_d = path_d.split()
        path_d.remove ('M')
        path_d.remove ('C')
        path_d.remove ('z')

        curve_n = len (path_d) // 3
        being_path_data = []
        for c in range (curve_n):
            c2 = c * 3

            curve_pt1 = list (eval (path_d[c2]))
            curve_pt1[0] += layer_trans[0] + path_trans[0]
            curve_pt1[1] += layer_trans[1] + path_trans[1]

            curve_pt2 = list (eval (path_d[c2 + 1]))
            curve_pt2[0] += layer_trans[0] + path_trans[0]
            curve_pt2[1] += layer_trans[1] + path_trans[1]

            curve_pt3 = list (eval (path_d[c2 + 2]))
            curve_pt3[0] += layer_trans[0] + path_trans[0]
            curve_pt3[1] += layer_trans[1] + path_trans[1]

            curve_pt4 = list (eval (path_d[c2 + 3]))
            curve_pt4[0] += layer_trans[0] + path_trans[0]
            curve_pt4[1] += layer_trans[1] + path_trans[1]

            being_path_data += [curve_pt1, curve_pt2, curve_pt3, curve_pt4]

        beings += [{
            'img_s': being_img_s,
            'img_sets_n': being_img_sets_n,
            'img_len': being_img_len,
            'path_rate': being_path_rate,
            'path_data': being_path_data }]

    _map = {
        'doors': doors,
        'rects': rects,
        'arcs': arcs,
        'items': items,
        'beings': beings }

    s.maps += [_map]
    return True

if __name__ == '__main__':
    if len (sys.argv) != 2:
        print("usage: " + sys.argv[0] + " [input base name]")
    else:
        maps_load (sys.argv[1])

