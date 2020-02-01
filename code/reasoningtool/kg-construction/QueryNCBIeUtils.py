__author__ = 'Stephen Ramsey'
__copyright__ = 'Oregon State University'
__credits__ = ['Stephen Ramsey', 'Finn Womack']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = ''
__email__ = ''
__status__ = 'Prototype'

# import requests
import urllib
import math
import sys
import time
from io import StringIO
import re
import pandas
import CachedMethods
# import requests_cache
from cache_control_helper import CacheControlHelper
# import requests

# requests_cache.install_cache('QueryNCBIeUtilsCache')
import numpy
import time

import sys

# MeSH Terms for Q1 diseases: (see git/q1/README.md)
#   Osteoporosis
#   HIV Infections
#   Cholera
#   Ebola Infection
#   Malaria
#   Osteomalacia
#   Hypercholesterolemia
#   Diabetes Mellitus, Type 2
#   Asthma
#   Pancreatitis, Chronic
#   Alzheimer Disease
#   Myocardial Infarction
#   Muscular Dystrophy, Duchenne
#   NGLY1 protein, human
#   Alcoholism
#   Depressive Disorder, Major
#   Niemann-Pick Disease, Type C
#   Huntington Disease
#   Alkaptonuria
#   Anemia, Sickle Cell
#   Stress Disorders, Post-Traumatic

class QueryNCBIeUtils:
    TIMEOUT_SEC = 120
    API_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

    '''runs a query against eUtils (hard-coded for JSON response) and returns the results as a ``requests`` object

    :param handler: str handler, like ``elink.fcgi``
    :param url_suffix: str suffix to be appended on the URL after the "?" character
    :param retmax: int to specify the maximum number of records to return (default here
                   is 1000, which is more useful than the NCBI default of 20)
    '''
    @staticmethod
    @CachedMethods.register
    def send_query_get(handler, url_suffix, retmax=1000, retry_flag = True):

        requests = CacheControlHelper()
        url_str = QueryNCBIeUtils.API_BASE_URL + '/' + handler + '?' + url_suffix + '&retmode=json&retmax=' + str(retmax)
#        print(url_str)
        try:
            res = requests.get(url_str, headers={'accept': 'application/json', 'User-Agent': 'Mozilla/5.0'}, timeout=QueryNCBIeUtils.TIMEOUT_SEC)
        except requests.exceptions.Timeout:
            print('HTTP timeout in QueryNCBIeUtils.py; URL: ' + url_str, file=sys.stderr)
            time.sleep(1)  ## take a timeout because NCBI rate-limits connections
            return None
        except requests.exceptions.ConnectionError:
            print('HTTP connection error in QueryNCBIeUtils.py; URL: ' + url_str, file=sys.stderr)
            time.sleep(1)  ## take a timeout because NCBI rate-limits connections
            return None
        except BaseException as e:
            print(url_str, file=sys.stderr)
            print('%s received in QueryMiRGate for URL: %s' % (e, url_str), file=sys.stderr)
            return None
        status_code = res.status_code
        if status_code != 200:
            if status_code == 429 and retry_flag:
                time.sleep(1)
                res = QueryNCBIeUtils.send_query_get(handler, url_suffix, retmax, False)
            else:
                print('HTTP response status code: ' + str(status_code) + ' for URL:\n' + url_str, file=sys.stderr)
                res = None
        return res

    @staticmethod
    #@CachedMethods.register
    def send_query_post(handler, params, retmax = 1000):

        requests = CacheControlHelper()
        url_str = QueryNCBIeUtils.API_BASE_URL + '/' + handler
        params['retmax'] = str(retmax)
        params['retmode'] = 'json'
#        print(url_str)
        try:
            res = requests.post(url_str, data=params, timeout=QueryNCBIeUtils.TIMEOUT_SEC)
        except requests.exceptions.Timeout:
            print('HTTP timeout in QueryNCBIeUtils.py; URL: ' + url_str, file=sys.stderr)
            time.sleep(1)  ## take a timeout because NCBI rate-limits connections
            return None
        except requests.exceptions.ConnectionError:
            print('HTTP connection error in QueryNCBIeUtils.py; URL: ' + url_str, file=sys.stderr)
            time.sleep(1)  ## take a timeout because NCBI rate-limits connections
            return None
        status_code = res.status_code
        if status_code != 200:
            print('HTTP response status code: ' + str(status_code) + ' for URL:\n' + url_str, file=sys.stderr)
            res = None
        return res

    @staticmethod
    @CachedMethods.register
    def get_clinvar_uids_for_disease_or_phenotype_string(disphen_str):
        res = QueryNCBIeUtils.send_query_get('esearch.fcgi',
                                             'term=' + disphen_str + '[disease/phenotype]')
        print("I'm in get_clinvar_uids")
        print(disphen_str)
        res_set = set()
        if res is not None:
            res_json = res.json()
            esr = res_json.get('esearchresult', None)
            if esr is not None:
                idlist = esr.get('idlist', None)
                if idlist is not None:
                    res_set |= set([int(uid_str) for uid_str in idlist])
        return res_set

    '''returns a set of mesh UIDs for a given disease name

    '''
    @staticmethod
    @CachedMethods.register
    def get_mesh_uids_for_disease_or_phenotype_string(disphen_str):
        res = QueryNCBIeUtils.send_query_get('esearch.fcgi',
                                             'db=mesh&term=' + urllib.parse.quote(disphen_str + '[disease/phenotype]',safe=''))
        res_set = set()
        if res is not None:
            res_json = res.json()
            esr = res_json.get('esearchresult', None)
            if esr is not None:
                idlist = esr.get('idlist', None)
                if idlist is not None:
                    res_set |= set([int(uid_str) for uid_str in idlist])
        return res_set


    '''returns a list of mesh UIDs for a given mesh tree number

    '''
    @staticmethod
    @CachedMethods.register
    def get_mesh_uids_for_mesh_tree(mesh_term):
        res = QueryNCBIeUtils.send_query_get('esearch.fcgi',
                                             'db=mesh&term=' +  urllib.parse.quote(mesh_term, safe=''))
        res_list = []
        if res is not None:
            res_json = res.json()
            res_esr = res_json.get('esearchresult', None)
            if res_esr is not None:
                res_idlist = res_esr.get('idlist', None)
                if res_idlist is not None:
                    res_list += res_idlist
        return res_list

    '''
        returns a list of mesh UIDs for a given mesh term query
    '''
    @staticmethod
    @CachedMethods.register
    def get_mesh_uids_for_mesh_term(mesh_term):
        res = QueryNCBIeUtils.send_query_get('esearch.fcgi',
                                             'db=mesh&term=' +  urllib.parse.quote(mesh_term + '[MeSH Terms]', safe=''))
        res_list = []
        if res is not None:
            res_json = res.json()
            res_esr = res_json.get('esearchresult', None)
            if res_esr is not None:
                res_idlist = res_esr.get('idlist', None)
                if res_idlist is not None:
                    res_list += res_idlist
        return res_list

    '''
        returns the mesh UID for a given medgen UID
        :param medgen_uid: integer
        :returns: set(integers) or ``None``
    '''
    @staticmethod
    @CachedMethods.register
    def get_mesh_uid_for_medgen_uid(medgen_uid):
        res = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                             'db=mesh&dbfrom=medgen&cmd=neighbor&id=' + str(medgen_uid))
        res_mesh_ids = set()
        if res is not None:
            res_json = res.json()
            res_linksets = res_json.get('linksets', None)
            if res_linksets is not None:
                for res_linkset in res_linksets:
                    res_linksetdbs = res_linkset.get('linksetdbs', None)
                    if res_linksetdbs is not None:
                        for res_linksetdb in res_linksetdbs:
                            res_meshids = res_linksetdb.get('links', None)
                            if res_meshids is not None:
                                for res_meshid in res_meshids:
                                    res_mesh_ids.add(int(res_meshid))
        return res_mesh_ids

    '''returns the mesh terms for a given MeSH Entrez UID

    :param mesh_uid: int (take the "D012345" form of the MeSH UID, remove the "D", convert to an integer, and add
                     68,000,000 to the integer; then pass that integer as "mesh_uid" to this function)
    :returns: list(str) of MeSH terms
    '''
    @staticmethod
    #@CachedMethods.register
    def get_mesh_terms_for_mesh_uid(mesh_uid):
        assert type(mesh_uid)==int
        # TODO: CAN DO THIS LOCALLY (Store UIDs from Descriptor name)
        res = QueryNCBIeUtils.send_query_get('esummary.fcgi',
                                             'db=mesh&id=' + str(mesh_uid))
        ret_mesh = []
        if res is not None:
            res_json = res.json()
            res_result = res_json.get('result', None)
            if res_result is not None:
                uids = res_result.get('uids', None)
                if uids is not None:
                    assert type(uids)==list
                    for uid in uids:
                        assert type(uid)==str
                        res_uid = res_result.get(uid, None)
                        if res_uid is not None:
                            res_dsm = res_uid.get('ds_meshterms', None)
                            if res_dsm is not None:
                                assert type(res_dsm)==list
                                ret_mesh += res_dsm
        return ret_mesh

    '''returns the NCBI MedGen UID for an OMIM ID

    :param omim_id: integer
    :returns: set(integers) or None
    '''
    @staticmethod
    @CachedMethods.register
    def get_medgen_uid_for_omim_id(omim_id):
        res = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                             'db=medgen&dbfrom=omim&cmd=neighbor&id=' + str(omim_id))
        ret_medgen_ids = set()

        if res is not None:
            res_json = res.json()
            res_linksets = res_json.get('linksets', None)
            if res_linksets is not None:
                for res_linkset in res_linksets:
                    res_linksetdbs = res_linkset.get('linksetdbs', None)
                    if res_linksetdbs is not None:
                        for res_linksetdb in res_linksetdbs:
                            res_medgenids = res_linksetdb.get('links', None)
                            if res_medgenids is not None:
                                ret_medgen_ids |= set(res_medgenids)
        return ret_medgen_ids

    @staticmethod
    @CachedMethods.register
    def get_mesh_terms_for_omim_id(omim_id):
        medgen_uids = QueryNCBIeUtils.get_medgen_uid_for_omim_id(omim_id)
        ret_mesh_terms = []
        for medgen_uid in medgen_uids:
            mesh_uids = QueryNCBIeUtils.get_mesh_uid_for_medgen_uid(medgen_uid)
            for mesh_uid in mesh_uids:
                mesh_terms = QueryNCBIeUtils.get_mesh_terms_for_mesh_uid(mesh_uid)
                ret_mesh_terms += list(mesh_terms)
        return ret_mesh_terms

    @staticmethod
    @CachedMethods.register
    def get_pubmed_hits_count(term_str, joint=False):
        term_str_encoded = urllib.parse.quote(term_str, safe='')
        res = QueryNCBIeUtils.send_query_get('esearch.fcgi',
                                             'db=pubmed&term=' + term_str_encoded)
        #print("this is my string in pub med")
        #print(term_str)
        res_int = None
        if res is not None:
            status_code = res.status_code
            if status_code == 200:
                res_int = int(res.json()['esearchresult']['count'])
                if joint:
                    res_int = [res_int]
                    if 'errorlist' in res.json()['esearchresult'].keys():
                        if 'phrasesnotfound' in res.json()['esearchresult']['errorlist'].keys():
                                if len(res.json()['esearchresult']['errorlist']['phrasesnotfound']) == 1:
                                    res_int += 2*res.json()['esearchresult']['errorlist']['phrasesnotfound']
                                else:
                                    res_int += res.json()['esearchresult']['errorlist']['phrasesnotfound']
                    else:
                        res_int += [int(res.json()['esearchresult']['translationstack'][0]['count'])]
                        res_int += [int(res.json()['esearchresult']['translationstack'][1]['count'])]
            else:
                print('HTTP response status code: ' + str(status_code) + ' for query term string {term}'.format(term=term_str))
        return res_int

    @staticmethod
    @CachedMethods.register
    def normalized_google_distance(mesh1_str, mesh2_str, mesh1=True, mesh2=True):
        """
        returns the normalized Google distance for two MeSH terms
        :param mesh1_str_decorated: mesh string
        :param mesh2_str_decorated: mesh string
        :param mesh1: flag if mesh1_str is a MeSH term
        :param mesh2: flag if mesh2_str is a MeSH term
        :returns: NGD, as a float (or math.nan if any counts are zero, or None if HTTP error)
        """

        if mesh1:  # checks mesh flag then converts to mesh term search
            mesh1_str_decorated = mesh1_str + '[MeSH Terms]'
        else:
            mesh1_str_decorated = mesh1_str

        if mesh2:  # checks mesh flag then converts to mesh term search
            mesh2_str_decorated = mesh2_str + '[MeSH Terms]'
        else:
            mesh2_str_decorated = mesh2_str

        if mesh1 and mesh2:
            [nij, ni, nj] = QueryNCBIeUtils.get_pubmed_hits_count('({mesh1}) AND ({mesh2})'.format(mesh1=mesh1_str_decorated,
                                                                                     mesh2=mesh2_str_decorated),joint=True)
            if type(ni) == str:
                if mesh1_str_decorated == ni:
                    mesh1_str_decorated = ni[:-12]
                if mesh2_str_decorated == nj:
                    mesh2_str_decorated = nj[:-12]
                [nij, ni, nj] = QueryNCBIeUtils.get_pubmed_hits_count('({mesh1}) AND ({mesh2})'.format(mesh1=mesh1_str_decorated,
                                                                                         mesh2=mesh2_str_decorated), joint=True)

        else:
            nij = QueryNCBIeUtils.get_pubmed_hits_count('({mesh1}) AND ({mesh2})'.format(mesh1=mesh1_str_decorated,
                                                                                         mesh2=mesh2_str_decorated))
            ni = QueryNCBIeUtils.get_pubmed_hits_count('{mesh1}'.format(mesh1=mesh1_str_decorated))
            nj = QueryNCBIeUtils.get_pubmed_hits_count('{mesh2}'.format(mesh2=mesh2_str_decorated))
            if (ni == 0 and mesh1) or (nj == 0 and mesh2):
                if (ni == 0 and mesh1):
                    mesh1_str_decorated = mesh1_str
                if (nj == 0 and mesh2):
                    mesh2_str_decorated = mesh2_str
                nij = QueryNCBIeUtils.get_pubmed_hits_count('({mesh1}) AND ({mesh2})'.format(mesh1=mesh1_str_decorated,
                                                                                         mesh2=mesh2_str_decorated))
                ni = QueryNCBIeUtils.get_pubmed_hits_count('{mesh1}'.format(mesh1=mesh1_str_decorated))
                nj = QueryNCBIeUtils.get_pubmed_hits_count('{mesh2}'.format(mesh2=mesh2_str_decorated))
        N = 2.7e+7 * 20  # from PubMed home page there are 27 million articles; avg 20 MeSH terms per article
        if ni is None or nj is None or nij is None:
            return math.nan
        if ni == 0 or nj == 0 or nij == 0:
            return math.nan
        numerator = max(math.log(ni), math.log(nj)) - math.log(nij)
        denominator = math.log(N) - min(math.log(ni), math.log(nj))
        ngd = numerator/denominator
        return ngd
    @staticmethod
    def multi_normalized_google_distance(name_list,  pmid_mesh_dict=None):
        """
        returns the normalized Google distance for a list of n MeSH Terms
        :param name_list: a list of strings containing search terms for each node
        :param mesh_flags: a list of boolean values indicating which terms need [MeSH Terms] appended to it.
        :returns: NGD, as a float (or math.nan if any counts are zero, or None if HTTP error)
        """
        """
            from PubMed home page there are 27 million articles;
            avg 20 MeSH terms per article
        """
        N = 2.7e+7 * 20
        count_scores  = []
        sets_of_pmids = []
        for mesh_term in name_list:
            if(mesh_term not in pmid_mesh_dict):
                count_scores.append(math.nan)
            else:
                pmids, hit_cnt = pmid_mesh_dict[mesh_term]
                count_scores.append(hit_cnt)
                sets_of_pmids.append(set(pmids))
        sets_intersection = len(set.intersection(*sets_of_pmids))
        if any(x == 0 for x in count_scores) or sets_intersection == 0:
            return math.nan
        if any(x == math.nan for x in count_scores):
            return math.nan
        numerator = max([math.log(x) for x in count_scores]) - math.log(sets_intersection)
        denominator = math.log(N) - min([math.log(x) for x in count_scores])
        return numerator / denominator

    @staticmethod
    @CachedMethods.register
    def get_pubmed_from_ncbi_gene(gene_id):
        '''
            Returns a list of pubmed ids associated with a given ncbi gene id
            :param gene_id: A string containing the ncbi gene id
        '''
        # CAN'T TO THIS LOCALLY
        res = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                             'db=pubmed&dbfrom=gene&id=' + str(gene_id))
        ret_pubmed_ids = set()
        pubmed_list = None

        if res is not None:
            res_json = res.json()
            res_linksets = res_json.get('linksets', None)
            if res_linksets is not None:
                for res_linkset in res_linksets:
                    res_linksetdbs = res_linkset.get('linksetdbs', None)
                    if res_linksetdbs is not None:
                        for res_linksetdb in res_linksetdbs:
                            res_pubmed_ids = res_linksetdb.get('links', None)
                            if res_pubmed_ids is not None:
                                ret_pubmed_ids |= set(res_pubmed_ids)
        if len(ret_pubmed_ids) > 0:
            pubmed_list = [ str(x) + '[uid]' for x in ret_pubmed_ids]
        return pubmed_list


    @staticmethod
    @CachedMethods.register
    def is_mesh_term(mesh_term):
        # Can do locally; cache plz
        ret_list = QueryNCBIeUtils.get_mesh_uids_for_mesh_term(mesh_term)
        return ret_list is not None and len(ret_list) > 0

    @staticmethod
    #@CachedMethods.register
    def get_mesh_terms_for_hp_id(hp_id):
        '''
        This takes a hp id and converts it into a list of mesh term strings with [MeSH Terms] appened to the end
        :param hp_id: a string containing the hp id formatted as follows: "HP:000000"
        '''
        if(hp_id[0])!='"':
            hp_id = '"' + hp_id + '"'
        hp_id+= "[Source ID]"
        # CAN"T DO LOCALLY
        res = QueryNCBIeUtils.send_query_get('esearch.fcgi',
                                             'db=medgen&term=' + str(hp_id))
        ret_medgen_ids = set()
        if res is not None:
            res_json = res.json()
            res_result = res_json.get('esearchresult', None)
            if res_result is not None:
                res_idlist = res_result.get('idlist', None)
                if res_idlist is not None:
                    ret_medgen_ids |= set(res_idlist)
        mesh_ids = set()
        for medgen_id in ret_medgen_ids:
            # CAN"T DO LOCALLY
            res = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                             'dbfrom=medgen&db=mesh&id=' + str(medgen_id))
            if res is not None:
                res_json = res.json()
                res_linksets = res_json.get('linksets', None)
                if res_linksets is not None:
                    for res_linkset in res_linksets:
                        res_linksetdbs = res_linkset.get('linksetdbs', None)
                        if res_linksetdbs is not None:
                            for res_linksetdb in res_linksetdbs:
                                res_mesh_ids = res_linksetdb.get('links', None)
                                if res_mesh_ids is not None:
                                    mesh_ids |= set(res_mesh_ids)
        mesh_terms = set()
        if len(mesh_ids) > 0:
            for mesh_id in mesh_ids:
                # CAN"T DO LOCALLY WITHOUT MEDGEN DB
                mesh_terms|= set(QueryNCBIeUtils.get_mesh_terms_for_mesh_uid(int(mesh_id)))
        if len(mesh_terms) > 0:
            mesh_terms = [mesh_term + '[MeSH Terms]' for mesh_term in mesh_terms]
            return mesh_terms
        else:
            return None

    @staticmethod
    def test_ngd():
        #mesh1_str = 'Anemia, Sickle Cell'
        #mesh2_str = 'Malaria'
        omim1_str = '219700'
        omim2_str = '219550'
        print(QueryNCBIeUtils.normalized_google_distance(mesh1_str, mesh2_str))

    @staticmethod
    @CachedMethods.register
    def get_uniprot_names(id):
        """
        Takes a uniprot id then return a string containing all synonyms listed on uniprot seperated by the deliminator |
        :param id: a string containing the uniprot id
        :returns: a string containing all synonyms uniprot lists for
        """
        # We want the actual uniprot name P176..., not the curie UniProtKB:P176...
        if "UniProtKB:" in id:
            id = ":".join(id.split(":")[1:])
        url = 'https://www.uniprot.org/uniprot/?query=id:' + id + '&sort=score&columns=entry name,protein names,genes&format=tab' # hardcoded url for uniprot data
        requests = CacheControlHelper()
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})  # send get request
        if r.status_code != 200:  # checks for error
            print('HTTP response status code: ' + str(r.status_code) + ' for URL:\n' + url, file=sys.stderr)
            return None
        if r.content.decode('utf-8') == '':
            return None
        df = pandas.read_csv(StringIO(r.content.decode('utf-8')), sep='\t')
        search = df.loc[0, 'Entry name']  # initializes search term variable
        if type(df.loc[0, 'Protein names']) == str:
            for name in re.compile("[()\[\]]").split(df.loc[0, 'Protein names']):  # checks for protein section
                if len(name) > 1:
                    if QueryNCBIeUtils.is_mesh_term(name):
                        search += '|' + name + '[MeSH Terms]'
                    else:
                        search += '|' + name
        if type(df.loc[0, 'Gene names']) == str:
            for name in df.loc[0, 'Gene names'].split(' '):
                if len(name) > 1:
                    if QueryNCBIeUtils.is_mesh_term(name):
                        search += '|' + name + '[MeSH Terms]'
                    else:
                        search += '|' + name
        return search

    @staticmethod
    @CachedMethods.register
    def get_reactome_names(id):
        '''
        Takes a reactome id then return a string containing all synonyms listed on reactome seperated by the deliminator |
        However, If it finds a MeSH terms in the list it will return the search term as a mesh term serach
        e.g. it will return something like '(IGF1R)[MeSH Terms]'

        This can be inputed into the google function as a non mesh term and will search as a mesh term.
        This is so that we do not need to handle the output of this function any differently it can all be input as non mesh terms

        Parameters:
            id - a string containing the reactome id

        Output:
            search - a string containing all synonyms of the reactome id or a mesh term formatted for the google distance function
        '''
        # We want the actual reactome name R-HSA..., not the curie REACT:R-HSA...
        if "REACT:" in id:
            id = ":".join(id.split(":")[1:])
        url = 'https://reactome.org/ContentService/data/query/'+id+'/name'  # hardcoded url for reactiome names
        requests = CacheControlHelper()
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})  # sends get request that returns a string
        if r.status_code != 200:
            print('HTTP response status code: ' + str(r.status_code) + ' for URL:\n' + url, file=sys.stderr)
            return None
        nameList = r.text.split('\n')  # splits returned string by line
        search = ''  # initializes search term variable
        for name in nameList:
            if len(name) > 0:  # removes blank lines at beginning and end of response
                if len(re.compile("[()]").split(name)) > 1:  # check for parenthesis
                    for n in re.compile("[()]").split(name):  # splits on either "(" or ")"
                        if len(n) > 0:  # removes banks generated by split
                            if QueryNCBIeUtils.is_mesh_term(n):  # check for mesh term
                                search += '|' + n + '[MeSH Terms]'
                            else:
                                search += '|' + n
                elif len(name.split('ecNumber')) > 1:  # checks for ec number
                    if QueryNCBIeUtils.is_mesh_term(name.split('ecNumber')[0]):
                        search += '|' + name.split('ecNumber')[0] + '[MeSH Terms]'
                    else:
                        search += '|' + name.split('ecNumber')[0]
                    search += '|' + name.split('ecNumber')[1][:-1] + '[EC/RN Number]'  # removes trailing "/" and formats as ec search term
                else:
                    if QueryNCBIeUtils.is_mesh_term(name):
                        search += '|' + name + '[MeSH Terms]'
                    else:
                        search += '|' + name
        search = search[1:]  # removes leading |
        return search
    '''
        Returns a set of mesh ids for a given clinvar id
    '''
    @staticmethod
    @CachedMethods.register
    def get_mesh_id_for_clinvar_uid(clinvar_id):
        # This checks for a straight clinvar id -> mesh id conversion:
        res = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                             'db=mesh&dbfrom=clinvar&id=' + str(clinvar_id))
        res_set = set()
        if res is not None:
            res_json = res.json()
            linksets = res_json.get('linksets', None)
            if linksets is not None:
                link = linksets[0]
                if link is not None:
                    dbs = link.get('linksetdbs', None)
                    if dbs is not None:
                        mesh_db = dbs[0]
                        if mesh_db is not None:
                            ids = mesh_db.get('links', None)
                            res_set |= set([int(uid_str) for uid_str in ids])

        # if there are no mesh ids returned above then this finds clinvar -> medgen -> mesh canversions:
        if len(res_set) == 0:
            res = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                             'db=medgen&dbfrom=clinvar&id=' + str(clinvar_id))
            if res is not None:
                res_json = res.json()
                linksets = res_json.get('linksets', None)
                if linksets is not None:
                    link = linksets[0]
                    if link is not None:
                        dbs = link.get('linksetdbs', None)
                        if dbs is not None:
                            medgen = dbs[0]
                            if medgen is not None:
                                ids = medgen.get('links', None)
                                if ids is not None:
                                    for medgen_id in ids:
                                        res2 = QueryNCBIeUtils.send_query_get('elink.fcgi',
                                            'db=mesh&dbfrom=medgen&id=' + str(medgen_id))
                                        res2_json = res2.json()
                                        linksets2 = res2_json.get('linksets', None)
                                        if linksets2 is not None:
                                            link2 = linksets2[0]
                                            if link2 is not None:
                                                dbs2 = link2.get('linksetdbs', None)
                                                if dbs2 is not None:
                                                    mesh_data = dbs2[0]
                                                    if mesh_data is not None:
                                                        mesh_ids = mesh_data.get('links', None)
                                                        res_set |= set([int(uid_str) for uid_str in mesh_ids])
        return res_set

    def test_phrase_not_found():
        print('----------')
        print('Result and time for 1st error (joint search):')
        print('----------')
        t0 = time.time()
        print(QueryNCBIeUtils.normalized_google_distance('lymph nodes','IL6'))
        print(time.time() - t0)
        print('----------')
        print('Result and time for 2nd error (individual search):')
        print('----------')
        t0 = time.time()
        print(QueryNCBIeUtils.normalized_google_distance('IL6','lymph nodes[MeSH Terms]',mesh2=False))
        print(time.time() - t0)
        print('Result and time for potential curve ball:')
        print('----------')
        t0 = time.time()
        print(QueryNCBIeUtils.normalized_google_distance('IL6','lymph node[MeSH Terms]|Naprosyn[MeSH Terms]|asdasdjkahfjkaf|flu|cold',mesh2=False))
        print(time.time() - t0)
        print('----------')
        print('Time with no error:')
        print('----------')
        t0 = time.time()
        QueryNCBIeUtils.normalized_google_distance('Naprosyn','lymph nodes')
        print(time.time() - t0)
