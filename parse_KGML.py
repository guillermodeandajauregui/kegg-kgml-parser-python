#!/usr/bin/env python
"""
Parse a KGML file and put in a PyNetworkX graph

>>> graphfile = 'data/hsa00510.xml'

>>> graph = KGML2Graph(graphfile)
"""

import xml.etree.ElementTree as ET
import networkx
import logging
import pylab
logging.basicConfig(level=logging.DEBUG)


def KGML2Graph(xmlfile, filetype = 'organism'):
    """
    Parse a KGML file and return a PyNetworkX graph object

    You can retrieve kgml files from ftp://ftp.genome.jp/pub/kegg/xml/
    (the ko folder is for generic pathways, the organism folder is per species)

    >>> graphfile = 'data/hsa00510.xml'
    >>> graph = KGML2Graph(graphfile)[1]

    the filetype option is used to distinguish between ko files (general and containin ortholog entries) 
    and files which are specific to an organism (e.g. file beginning with hsa etc..)

    >>> graph.nodes()[0:5]
    ['ALG8', 'ALG9', 'GCS1', 'ST6GAL1', 'ALG2']

    >>> len(graph.nodes())
    36

    >>> graph.edges()[0:5]
    [('ALG8', 'ALG10B'), ('ALG8', 'ALG6'), ('ALG9', 'ALG3'), ('ALG9', 'ALG12'), ('ALG9', 'ALG6')]
 
    """
    graph = networkx.Graph()
    nodes = {}
    genes = []
    reactions = {}

    tree = ET.parse(xmlfile)

    if filetype in ('organism', 'o'):
        entriestype = ('gene', 'compound', 'map')
    else:
        entriestype = ('ortholog', 'map', 'compound',)

    # Get pathway title (store it in graph.title)
    graph.title = tree.find('/').attrib['title']
    
    # parse and add nodes
    for el in tree.getiterator('entry'):
        # get all genes or compounds, and associate ids to names
        logging.debug(el.attrib['type'] + ' ' + el.attrib['id'])
        if el.attrib['type'] in entriestype:       # something else?
            name = el.attrib['name']
            id = el.attrib['id']
#            if nodes.has_key(id):
#                raise TypeError('over writing a key')
            title = el.find('graphics').attrib['name']

            # some nodes refer to more than a gene, and have a title in the form
            # 'nameofthefirstgene...', e.g. 'ALG2...'
            # As a temporary solution (to investigate more), I am just taking the name
            # of the first gene/entity
            if title[-3:] == '...':
                title = title[:-3]

            nodes[id] = (name, title, el.attrib['type'])
            if el.attrib['type'] == 'gene':
                graph.add_node(title)
#    logging.debug(nodes)

    # parse and add relations
    for rel in tree.getiterator('relation'):
        e1 = rel.attrib['entry1']
        e2 = rel.attrib['entry2']
#        print e1, e2
#        print 'e1 ', nodes[e1]
#        print 'e2 ', nodes[e2] 

#        for node in nodes[e1][0].split():
#            print e1, node
#        for node in nodes[e2][0].split():
#            print e2, node
        graph.add_edge(nodes[e1][1], nodes[e2][1])
   
    return tree, graph, nodes, genes, reactions

def plot_starlike(graph):
    networkx.draw_circular(graph)
    pylab.title(graph.title)
    title = graph.title.replace('/', '-') # TODO: which is the proper way to remove / in a filename?
    pylab.savefig(title + '.png')
    pylab.show()

def convert_to_gml(graph):
    """
    write the pathway to the gml format
    - http://www.infosun.fim.uni-passau.de/Graphlet/GML/
    """
    networkx.write_gml(graph, graph.title + '.gml')

if __name__ == '__main__':
    import sys
    import argparse
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='parse a KGML pathway file and convert it to python/gml/image')
    parser.add_argument('-pathwayfile', '--pathway', dest='pathwayfile', type=str, default='data/hsa00510.xml')
    parser.add_argument('-type', dest='pathwaytype', type=str, choices=['ko', 'k', 'generic', 'general', 'organism', 'o'], 
                    default='o', help='type of the pathway (ko or specific to an organism?)')
    parser.add_argument('-d', '-draw', dest='draw_to_image', action='store_true', default=False)
    parser.add_argument('-c', '-draw_circular', dest='draw_circular', action='store_true', default=False)
    parser.add_argument('-g', '-write_gml', dest='write_gml', action='store_true', default=False)
    args = parser.parse_args()
    logging.debug(args)

    pathwayfile = args.pathwayfile
    pathwaytype = args.pathwaytype

    (tree, graph, nodes, genes, reactions) = KGML2Graph(pathwayfile, pathwaytype)

    if args.draw_circular:
        logging.debug('plotting')
        plot_starlike(graph)    
    
    if args.write_gml:
        logging.debug('plotting')
        convert_to_gml(graph)
