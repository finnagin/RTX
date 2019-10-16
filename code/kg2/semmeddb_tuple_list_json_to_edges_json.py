#!/usr/bin/env python3
'''semmeddb_tuple_list_json_to_edges_json.py: extracts all the predicate triples from SemMedDB, in the RTX KG2 JSON format

   Usage: semmeddb_tuple_list_json_to_edges_json.py --inputFile <inputFile.json> --outputFile <outputFile.json>
'''

__author__ = 'Stephen Ramsey'
__copyright__ = 'Oregon State University'
__credits__ = ['Stephen Ramsey']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = ''
__email__ = ''
__status__ = 'Prototype'


import argparse
import json
import kg2_util
import re


SEMMEDDB_IRI = 'https://skr3.nlm.nih.gov/SemMedDB'
NEG_REGEX = re.compile('^NEG_', re.M)
EDGE_LABELS_EXCLUDE_FOR_LOOPS = {'same_as', 'higher_than', 'lower_than', 'different_from', 'compared_with'}


def make_rel(preds_dict: dict,
             subject_curie: str,
             object_curie: str,
             predicate: str,
             pmid: str,
             pub_date: str,
             sentence: str,
             subject_score: str,
             object_score: str,
             negated: bool):
    key = subject_curie + '-' + predicate + '-' + object_curie
    key_val = preds_dict.get(key, None)
    publication_curie = 'PMID:' + pmid
    publication_info_dict = {
        'publication date': pub_date,
        'sentence': sentence,
        'subject score': subject_score,
        'object score': object_score}
    if key_val is None:
        relation_type = predicate.lower()
        relation_iri = kg2_util.convert_snake_case_to_camel_case(relation_type.replace(' ','_'))
        relation_iri = relation_iri[0].lower() + relation_iri[1:]
        relation_iri = SEMMEDDB_IRI + '#' + relation_iri
        edge_dict = kg2_util.make_edge(subject_curie,
                                       object_curie,
                                       relation_iri,
                                       'SEMMEDDB:' + relation_type,
                                       relation_type,
                                       SEMMEDDB_IRI,
                                       curr_timestamp)
        edge_dict['publications'] = [publication_curie]
        edge_dict['publications info'] = {publication_curie: publication_info_dict}
        edge_dict['negated'] = negated
        preds_dict[key] = edge_dict
    else:
        key_val['publications info'][publication_curie] = publication_info_dict
        key_val['publications'] = key_val['publications'] + [publication_curie]


def make_arg_parser():
    arg_parser = argparse.ArgumentParser(description='semmeddb_mysql_to_json.py: extracts all the predicate triples from SemMedDB, in the RTX KG2 JSON format')
    arg_parser.add_argument('--test', dest='test', action='store_true', default=False)
    arg_parser.add_argument('--inputFile', type=str, nargs=1)
    arg_parser.add_argument('--outputFile', type=str, nargs=1)
    return arg_parser


def get_remapped_cuis():
    """
    Creates a dictionary of retired CUIs and the current CUIs they map to in UMLS; currently only includes remappings
    labeled as a 'synonym' (vs. 'broader', 'narrower', or 'other related').
    """
    remapped_cuis = dict()
    with open('/home/ubuntu/kg2-build/umls/META/MRCUI.RRF', 'r') as retired_cui_file:
        # Line format in MRCUI file: retired_cui|release|map_type|||remapped_cui|is_current|
        for line in retired_cui_file:
            row = line.split('|')
            map_type = row[2]
            is_current = row[6]
            old_cui = row[0]
            new_cui = row[5]
            # Only include the remapping if it's a 'synonym' (and is current)
            if map_type == 'SY' and is_current == 'Y' and new_cui != '':
                remapped_cuis[old_cui] = new_cui
    return remapped_cuis


if __name__ == '__main__':
    args = make_arg_parser().parse_args()
    input_file_name = args.inputFile[0]
    output_file_name = args.outputFile[0]
    test_mode = args.test
    remapped_cuis = get_remapped_cuis()
    input_data = json.load(open(input_file_name, 'r'))
    edges_dict = dict()
    nodes_dict = dict()
    row_ctr = 0
    for (pmid, subject_cui_str, predicate, object_cui_str, pub_date, sentence,
         subject_score, object_score, curr_timestamp) in input_data['rows']:
        row_ctr += 1
        if row_ctr % 100000 == 0:
            print("Have processed " + str(row_ctr) + " rows out of " + str(len(input_data['rows'])) + " rows")
        if test_mode and row_ctr > 10000:
            break
        subject_cui_split = subject_cui_str.split("|")
        subject_cui = subject_cui_split[0]
        subject_cui = remapped_cuis.get(subject_cui, subject_cui)  # Use remapped CUI if one exists
        if len(subject_cui_split) > 1:
            subject_entrez_id = subject_cui_split[1]
        else:
            subject_entrez_id = None
        object_cui_split = object_cui_str.split("|")
        object_cui = object_cui_split[0]
        object_cui = remapped_cuis.get(object_cui, object_cui)  # Use remapped CUI if one exists
        if len(object_cui_split) > 1:
            object_entrez_id = object_cui_split[1]
        else:
            object_entrez_id = None
        if NEG_REGEX.match(predicate):
            negated = True
            predicate = NEG_REGEX.sub('', predicate, 1)
        else:
            negated = False
        if subject_cui == object_cui and predicate.lower() in EDGE_LABELS_EXCLUDE_FOR_LOOPS:
            continue
        make_rel(edges_dict, 'CUI:' + subject_cui, 'CUI:' + object_cui, predicate, pmid,
                 pub_date, sentence, subject_score, object_score, negated)
        if subject_entrez_id is not None:
            make_rel(edges_dict, 'NCBIGene:' + subject_entrez_id, 'CUI:' + object_cui,
                     predicate, pmid, pub_date, sentence, subject_score, object_score, negated)
        if object_entrez_id is not None:
            make_rel(edges_dict, 'CUI:' + subject_cui, 'NCBIGene:' + object_entrez_id,
                     predicate, pmid, pub_date, sentence, subject_score, object_score, negated)
        if predicate not in nodes_dict:
            relation_iri = kg2_util.convert_snake_case_to_camel_case(predicate.lower().replace(' ','_'))
            relation_iri = SEMMEDDB_IRI + '#' + relation_iri
            nodes_dict[predicate] = kg2_util.make_node(id='SEMMEDDB:' + predicate.lower(),
                                                        iri=relation_iri,
                                                        name=predicate.lower(),
                                                        category_label="relationship type", 
                                                        update_date=curr_timestamp, 
                                                        provided_by=SEMMEDDB_IRI)
    out_graph = {'edges': [rel_dict for rel_dict in edges_dict.values()],
                 'nodes': [node_dict for node_dict in nodes_dict.values()]}
    for rel_dict in out_graph['edges']:
        if len(rel_dict['publications']) > 1:
            rel_dict['publications'] = list(set(rel_dict['publications']))

    output_file_name = args.outputFile[0]

    kg2_util.save_json(out_graph, output_file_name, test_mode)
