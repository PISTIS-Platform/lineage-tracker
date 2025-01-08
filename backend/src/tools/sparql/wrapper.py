import http.client as http_client
import logging
import os
import re
from SPARQLWrapper import SPARQLWrapper, JSON

from tools.sparql.groundlevel_tools.regex_query_builder import re_convert_insert, re_get_namespaces_rdf_query
from tools.rdf.graph_builder import namespaces, Document
from tools.error_handler import CustomError

http_client.HTTPConnection.debuglevel = 1
logger = logging.getLogger('wrapper')

virtuoso_host = os.getenv('VIRTUOSO_HOST', 'http://lineage-information-store:8890')

sparql = SPARQLWrapper(
    virtuoso_host + '/sparql-auth')
sparql.setHTTPAuth('DIGEST')
sparql.setCredentials('dba', 'dba')
sparql.setReturnFormat(JSON)

# Actual SPARQL queries  
def insert_SPARQL(document:Document):
    '''
    Inserts document into rdf graph
    '''
    rdf_string = document.get_serialized_rdf_graph()
    pattern = r'((@prefix)( \S+: <\S+> ).(\n+))+?(\{(?s).*\})?'
    query = re.sub(pattern, re_convert_insert, rdf_string)
    
    logger.debug(
        'INSERT_SPARQL - QUERY:\n\n%s', query
    )

    # Sets the sparql query
    sparql.setQuery(query)

    try:
        # Executes the query and retrieves results
        result = sparql.queryAndConvert()
        return result
    except Exception as e:
        logger.error('500 - ERROR - INSERT_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e))
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def get_name_by_uuid_SPARQL(uuid:str):
    '''
    Queries rdf graph for dataset name given uuid
    '''
    #the generation of an empty document to only access the namespaces for _creation unrelated_ SPARQL queries
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query = '''
    SELECT ?name
    FROM <pistisGraph:v3> 
    {
	    ?d a prov:Entity;
        %1;
        dct:title ?name.
    }
    '''
    query = namespaces_rdf_query + re.sub(r'%1', 'dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>'.format(uuid), query)  
    logger.debug(
        'GET_NAME_BY_UUID_SPARQL - QUERY:\n\n%s', query
        )
    
    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
        
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_NAME_TYPE_UUID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def select_dataset_history_by_uuid_SPARQL(uuid: str, user_group=None):
    '''
    Queries RDF graph for dataset history given uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    # Base query
    query = '''
    SELECT ?operationDescription ?timestamp ?associatedUser ?associatedUserGroup ?previousUUID ?nextUUID

    FROM <pistisGraph:v3> 
    WHERE
    {{
        {{
            ?operation a prov:Activity;
                prov:used ?dataset;
                prov:wasAssociatedWith ?User.
        }}
        UNION
        {{
            ?operation a prov:Activity;
                prov:used ?nextDataset;
                prov:wasAssociatedWith ?User;
                dcterms:description ?desc.
            FILTER(CONTAINS(LCASE(STR(?desc)), "update"))
            ?nextDataset prov:wasDerivedFrom ?dataset.
        }}

        ?operation dct:description ?operationDescription;
            dct:issued ?timestamp.
        ?dataset dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>.
        ?User foaf:nick ?associatedUser.
        ?User pistisUserGroup:id ?associatedUserGroup.
'''.format(uuid)  # Note: Do not close the WHERE clause here

    # If user_group is provided, add a FILTER inside the WHERE clause
    if user_group:
        query += '''
        FILTER(STR(?associatedUserGroup) = "{}")
        '''.format(user_group)
    
    # Append optional clauses and close the WHERE clause
    query += '''
        OPTIONAL {
            ?dataset prov:wasDerivedFrom ?previousDataset.
            ?previousDataset dct:identifier ?previousUUID.
        }

        OPTIONAL {
            ?nextDataset prov:wasDerivedFrom ?dataset.
            ?nextDataset dct:identifier ?nextUUID.
        }
    }
    '''

    # Combine namespaces and query
    query = namespaces_rdf_query + query

    logger.debug('SELECT_HISTORY_UUID_SPARQL - QUERY:\n\n%s', query)
    
    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            '500 - ERROR - SELECT_HISTORY_UUID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(str(e), 'Virtuoso Triple Store', 500)




def select_user_history_by_uuid_SPARQL(username:str):
    '''
    Queries rdf graph for user history given username
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    # SPARQL query template
    query = '''
    SELECT ?operationDescription ?timestamp ?datasetUUID ?datasetTitle ?previousDataset ?previousUUID ?associatedUserGroup

    FROM <pistisGraph:v3> 
    WHERE
    {
        ?operation a prov:Activity;
            prov:used ?dataset;
            prov:wasAssociatedWith ?User.
                        
        ?operation dct:description ?operationDescription;
            dct:issued ?timestamp.
        ?dataset dct:identifier ?datasetUUID;
            dct:title ?datasetTitle.
        ?User pistisUserGroup:id ?associatedUserGroup.

        # Check if the User variable contains the username
        ?User foaf:nick ?associatedUser.
        FILTER(CONTAINS(LCASE(STR(?associatedUser)), LCASE("%1")))

        OPTIONAL {
            ?dataset prov:wasDerivedFrom ?previousDataset.
            ?previousDataset dct:identifier ?previousUUID
        }
    }
    '''

    # String replace to insert the username into the query
    query = namespaces_rdf_query + query.replace("%1", username)
    
    logger.debug(
        'GET_USER_HISTORY_UUID_SPARQL - QUERY:\n\n%s', query
        )
    
    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_USER_HISTORY_UUID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def select_lineage_by_lineage_id_SPARQL(lineage_id:str):
    '''
    Queries rdf graph for lineage given a lineage_id
    '''
    logger.info("*** Inside select_lineage_by_lineage_id_SPARQL")
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query ='''
    SELECT ?id ?title ?operationDescription ?operationBy ?associatedUserGroup ?titleFrom ?timestamp ?previousUUID
    FROM <pistisGraph:v3> 
    WHERE 
    {
        ?d a prov:Entity;
        prov:wasAttributedTo ?attributed;
        prov:wasGeneratedBy ?operationFrom;
        dct:identifier ?id;
        %1;
        dct:title ?title.
        ?operationFrom dct:description ?operationDescription.

        OPTIONAL {
            ?d prov:wasDerivedFrom ?previousDataset.
            ?previousDataset dct:identifier ?previousUUID
        }

        ?operationFrom dct:issued ?timestamp.
        ?attributed foaf:nick ?operationBy.
        ?attributed pistisUserGroup:id ?associatedUserGroup.
      }
    '''
    query = namespaces_rdf_query + re.sub(r'%1', 'pistisDatasetLineage:id "{}"^^<http://www.w3.org/2001/XMLSchema#string>'.format(lineage_id), query)

    logger.debug(
        'SELECT_LINEAGE_BY_LINEAGE_ID_SPARQL - QUERY:\n\n%s', query
    )
    
    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
        

    except Exception as e:
        logger.error(
            '500 - ERROR - SELECT_LINEAGE_BY_LINEAGE_ID_SPARQL - VIRTUOSO TRIPLE STORE', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def validate_operation_by_uuid_SPARQL(uuid:str):
    '''
    Queries rdf graph to help validate operations
    '''
    # Get rdf namespaces in a query-ready format
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query ='''
    SELECT ?operationFrom
    FROM <pistisGraph:v3> 
    WHERE 
    {
        ?d a prov:Entity;
        prov:wasGeneratedBy ?operationFrom;
        %1.
    }
    '''
    query = namespaces_rdf_query + re.sub(r'%1', 'dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>'.format(uuid), query)
    logger.debug(
        'VALIDATE_OPERATION_UUID - QUERY\n\n:\n\n%s', query
    )
    
    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            'ERROR - VALIDATE_OPERATION_UUID - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def check_was_derived_from_SPARQL(uuid:str):
    '''
    Queries triplestore to determine if any dataset wasDerivedFrom uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)

    query ='''
    SELECT ?entity ?operationFrom
    FROM <pistisGraph:v3>
    WHERE {
        ?entity a prov:Entity;
        prov:wasGeneratedBy ?operationFrom;
        prov:wasDerivedFrom ?entityDerived.
        ?entityDerived dct:identifier "%1"^^<http://www.w3.org/2001/XMLSchema#string>.
    }
    '''
    query = re.sub(r'%1', uuid, query)
    query = namespaces_rdf_query + query

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()

    except Exception as e:
        logger.error(
            '500 - ERROR - CHECK_WAS_DERIVED_FROM_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def check_lineage_node_SPARQL(uuid:str):
    '''
    Queries triplestore to determine if the lineage splits and a new lineage_id needs to be created
    Lineage splits if there is already a dataset that wasDerivedFrom uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query ='''
    SELECT ?d
    FROM <pistisGraph:v3> 
    WHERE 
    {
        ?d a prov:Entity ;
        prov:wasDerivedFrom ?from .
        %1 .
    }
    '''
    query = namespaces_rdf_query + re.sub(r'%1', '?from dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>'.format(uuid), query)
    logger.debug(
        'CHECK_LINEAGE_NODE_SPARQL - QUERY:\n\n%s', query
    )

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
        

    except Exception as e:
        logger.error(
            '500 - ERROR - CHECK_LINEAGE_NODE_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def get_status_by_uuid_SPARQL(uuid:str):
    '''
    Returns dataset status given a uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query = '''
    SELECT ?status
    FROM <pistisGraph:v3> 
    WHERE 
    {
        ?d a prov:Entity;
        adms:status ?status;
        %1.
    }
    '''
    query = namespaces_rdf_query + re.sub(r'%1', 'dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>'.format(uuid), query)
    logger.debug(
        'GET_STATUS_UUID_SPARQL - QUERY:\n\n%s', query
    )

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
        
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_STATUS_UUID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def get_lineage_id_by_uuid_SPARQL(uuid:str):
    '''
    Queries rdf graph for lineage_id given uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query ='''
    SELECT ?lineageId
    FROM <pistisGraph:v3> 
    WHERE 
    {
       ?d a prov:Entity;
        pistisDatasetLineage:id ?lineageId;
        %1
    }
    '''
    query = re.sub(r'%1', 'dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>.'.format(uuid), query)
    query = namespaces_rdf_query + query
    logger.debug(
        'GET_LINEAGE_ID_SPARQL - QUERY:\n\n%s', query
    )

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_LINEAGE_ID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def get_lineage_id_by_family_id_SPARQL(family_id:str):
    '''
    Queries rdf graph for lineage_id given family_id
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query ='''
    SELECT ?lineageId
    FROM <pistisGraph:v3> 
    WHERE 
    {
        ?d a prov:Entity ;
        pistisDatasetLineage:id ?lineageId ;
        %1
    }
    '''
    query = re.sub(r'%1', 'pistisDatasetFamily:id "{}"^^xsd:string.'.format(family_id), query)
    query = namespaces_rdf_query + query
    logger.debug(
        'GET_LINEAGE_ID_BY_FAMILY_ID_SPARQL - QUERY:\n\n%s', query
    )

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_LINEAGE_ID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def get_family_id_SPARQL(uuid:str):
    '''
    Queries rdf graph for all uuids in same family as uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    query ='''
    SELECT ?familyId
    FROM <pistisGraph:v3> 
    WHERE 
    {
        ?d a prov:Entity;
        pistisDatasetFamily:id ?familyId;
        %1
    }
    '''
    query = namespaces_rdf_query + re.sub(r'%1', 'dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>.'.format(uuid), query)
    logger.debug(
        'GET_FAMILY_ID_SPARQL - QUERY:\n\n%s', query
    )

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_FAMILY_ID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )

def get_family_uuids_by_uuid_SPARQL(uuid:str):
    '''
    Queries rdf graph for uuids for entire family of uuid
    '''
    empty_document = Document(namespaces)
    namespaces_rdf = empty_document.get_rdf_namespaces()
    namespaces_rdf_query = re_get_namespaces_rdf_query(namespaces_rdf)
    
    try:
        query = '''
        SELECT ?uuid
        FROM <pistisGraph:v3> 
        WHERE 
        {{
            ?dataset a prov:Entity;
                dct:identifier "{}"^^<http://www.w3.org/2001/XMLSchema#string>;
                pistisDatasetFamily:id ?familyId.
            
            ?otherDataset a prov:Entity;
                pistisDatasetFamily:id ?familyId;
                dct:identifier ?uuid.
        }}
        '''.format(str(uuid))
    except Exception as e:
        logger.debug("Exception: %s", e)
    
    query = namespaces_rdf_query + query
    logger.debug(
        'GET_FAMILY_UUIDS_SPARQL - QUERY:\n\n%s', query
    )

    sparql.setQuery(query)
    try:
        return sparql.queryAndConvert()
    except Exception as e:
        logger.error(
            '500 - ERROR - GET_FAMILY_ID_SPARQL - VIRTUOSO TRIPLE STORE - %s', str(e)
        )
        raise CustomError(
            str(e),
            'Virtuoso Triple Store',
            500
        )
