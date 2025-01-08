'''
This 
'''

import logging
import numpy as np
import os
import pandas as pd
import time
import uuid as uuid_generator
from csv_diff import load_csv, compare
from datetime import datetime
from flask import jsonify
from json import dumps, loads
import requests

from collections import Counter
from tools.error_handler import CustomError
from tools.rdf.graph_builder import namespaces, Dataset, Operation, User, Document

from tools.sparql.wrapper import insert_SPARQL, select_lineage_by_lineage_id_SPARQL, \
    select_dataset_history_by_uuid_SPARQL, select_user_history_by_uuid_SPARQL
from tools.operation_validator import validate_update, validate_create, validate_read, \
    validate_delete, validate_delete_family_tree, check_lineage_node, get_lineage_id_by_uuid, get_family_id, \
    get_lineage_ids_by_family_id, get_name_by_uuid, get_family_uuids_by_uuid

FDS_API_URL = 'https://develop.pistis-market.eu/srv/factory-data-storage'
FDS_API_KEY = os.getenv('FDS_API_KEY', '')
LT_API_KEY = os.getenv('LT_API_KEY', '')
CLIENT_ID = os.getenv('CLIENT_ID', 'client_id')
CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'client_secret')

logger = logging.getLogger('logic_layer')

def create(username:str, user_group:str, uuid:str, dataset_name:str) -> str:
    '''
    Validates create action and appends to rdf graph
    '''
    lineage_id = str(uuid_generator.uuid4())
    family_id = str(uuid_generator.uuid4())
    
    # checking if the dataset does not already exist
    if validate_create(uuid):
        logger.info(
            'CREATE - CONDITION FULFILLED'
        )

        dataset = Dataset(uuid, dataset_name, lineage_id, family_id)
        user = User(name=username, group=user_group)
        operation = Operation(
            type_='create', 
            involved_dataset=dataset, 
            involved_user=user
        )

        # Abstract document object, which is being independently created for each CRUD operation. 
        # It can be seen as a sub-graph,
        # which is subsequently being extended to the overarching RDF graph
        document = Document(namespaces, user, dataset, operation)
        insert_SPARQL(document)

        return 'Creation of the dataset successfully documented.'
    else:
        logger.error(
            '412 - ERROR - CREATE - CONDITION FAILED'
            )
        raise CustomError(
            'Dataset with specified UUID already exists and cannot be created.',
            'Lineage Tracker Backend',
            412
        )

def read(username:str, user_group:str, uuid:str) -> str:
    '''
    Validates read action and appends to rdf graph
    '''
    # Checks if uuid exists and is not deleted
    update_conditions = validate_read(uuid)
    if sum(list(update_conditions.values())) == 2:
        logger.info(
            'READ - CONDITIONS FULFILLED'
        )
        
        dataset_name = get_name_by_uuid(uuid)
        lineage_id = get_lineage_id_by_uuid(uuid)
        family_id = get_family_id(uuid)

        logger.debug(
            'READ - LINEAGE_ID: %s', lineage_id
        )
        logger.debug(
            'READ - FAMILY_ID: %s', family_id
        )
        logger.debug(
            'READ - DATASET_NAME: %s', dataset_name
        )

        # "pseudo"-dataset with similar attributes to the "old" ones
        # is being created 
        dataset = Dataset(uuid, dataset_name, lineage_id, family_id)
        user = User(name=username, group=user_group)
        operation = Operation(
            type_='read', 
            involved_dataset=dataset, 
            involved_user=user
        )

        document = Document(namespaces, user, dataset, operation)
        
        insert_SPARQL(document)

        return 'Reading operation successfully documented.'
    
    else:
        if not update_conditions['dataset_exists']:
            logger.error(
            '412 - ERROR - READ - CONDITION FAILED - DATASET DOES NOT EXIST'
            )
            raise CustomError(
                'Dataset cannot be read, because it does not exist.',
                'Lineage Tracker Backend',
                412
            )
        else:
            logger.error(
            '412 - ERROR - READ - CONDITION FAILED - DATASET WAS DELETED'
            )
            raise CustomError(
                'Dataset cannot be read, because it was deleted.',
                'Lineage Tracker Backend',
                412
            )

def update(username:str, user_group:str, uuid:str, uuid_prev:str, update_description:str) -> str:
    '''
    Validates update action and appends to rdf graph
    '''
    # Checks if uuid_prev exists and is not deleted
    update_conditions = validate_update(uuid_prev)
    if sum(list(update_conditions.values())) == 2:
        logger.info(
            'UPDATE - CONDITIONS FULFILLED'
            )
        
        dataset_name = get_name_by_uuid(uuid_prev)
        lineage_id_prev = get_lineage_id_by_uuid(uuid_prev)
        family_id = get_family_id(uuid_prev)
        
        # checking if the family tree of the dataset splits
        # If yes, a new lineage_id is being assigned
        if check_lineage_node(uuid_prev):
            logger.info(
                'UPDATE - LINEAGE SPLIT DETECTED'
            )
            lineage_id = str(uuid_generator.uuid4())
        else:
            lineage_id = lineage_id_prev

        logger.debug(
            'UPDATE - LINEAGE_ID_PREV: %s', lineage_id_prev
        )
        logger.debug(
            'UPDATE - LINEAGE_ID: %s', lineage_id
        )
        logger.debug(
            'UPDATE - FAMILY_ID: %s', family_id
        )
        logger.debug(
            'UPDATE - DATASET_NAME: %s', dataset_name
        )

        dataset = Dataset(uuid, dataset_name, lineage_id, family_id)
        dataset_prev = Dataset(uuid_prev, dataset_name, lineage_id_prev, family_id)
        user = User(name=username, group=user_group) 

        # Add Update operation for uuid
        operation = Operation(
            type_='update', 
            description=update_description,
            involved_dataset=dataset, 
            involved_user=user
        )
        document = Document(namespaces, user, dataset, operation, dataset_prev)
        insert_SPARQL(document)

        return 'updating the dataset successfully documented.'

    else:
        if not update_conditions['dataset_exists']:
            logger.error(
            '412 - ERROR - UPDATE - CONDITION FAILED - DATASET DOES NOT EXIST'
            )
            raise CustomError(
                'Dataset cannot be updated, because it does not exist.',
                'Lineage Tracker Backend',
                412
            )
        else:
            logger.error(
            '412 - ERROR - UPDATE - CONDITION FAILED - DATASET WAS DELETED'
            )
            raise CustomError(
                'Dataset cannot be updated, because it was deleted.',
                'Lineage Tracker Backend',
                412
            )

def delete(username:str, user_group:str, uuid:str) -> str:
    '''
    Validates delete action and appends to rdf graph
    A node can only be deleted if no other undeleted node wasDerivedFrom it
    (e.g., node2 wasDerivedFrom node1. node1 cannot be deleted unless node2 is deleted)
    '''
    
    # Checks if uuid exists, is not deleted, and 
    # no other dataset wasDerivedFrom this one
    delete_conditions = validate_delete(uuid)
    if sum(list(delete_conditions.values())) == 3:

        logger.info(
            'DELETE - CONDITIONS FULFILLED'
        )

        dataset_name = get_name_by_uuid(uuid)
        lineage_id = get_lineage_id_by_uuid(uuid)
        family_id = get_family_id(uuid)

        logger.debug(
            'DELETE - LINEAGE_ID: %s', lineage_id
        )
        logger.debug(
            'DELETE - FAMILY_ID: %s', family_id
        )

        dataset = Dataset(uuid, dataset_name, lineage_id, family_id)
        user = User(name=username, group=user_group)
        operation = Operation(
            type_='delete', 
            involved_dataset=dataset, 
            involved_user=user
        )

        document = Document(namespaces, user, dataset, operation)

        insert_SPARQL(document)

        return 'Dataset successfully deleted.'
    else:
        if not delete_conditions['dataset_exists']:
            logger.error(
            '412 - ERROR - DELETE - CONDITION FAILED - DATASET DOES NOT EXIST'
            )
            raise CustomError(
                'Dataset cannot be deleted, because it does not exist.',
                'Lineage Tracker Backend',
                412
            )
        elif not delete_conditions['not_deleted']:
            logger.error(
            '412 - ERROR - DELETE - CONDITION FAILED - DATASET WAS ALREADY DELETED'
            )
            raise CustomError(
                'Dataset cannot be deleted, because it was already deleted.',
                'Lineage Tracker Backend',
                412
            ) 
        elif not delete_conditions['not_undeleted_was_derived_from']:
            logger.error(
            '412 - ERROR - DELETE - CONDITION FAILED - ANOTHER UNDELETED DATASET WASDERIVEDFROM THIS DATASET'
            )
            raise CustomError(
                'Dataset cannot be deleted, because another undeleted dataset wasDerivedFrom this dataset.',
                'Lineage Tracker Backend',
                412
            ) 
        else:
            logger.error(
                '412 - ERROR - DELETE - CONDITION FAILED - DATASET DOES NOT EXIST'
                )
            raise CustomError(
                        'Dataset cannot be deleted, because it does not exist.',
                        'Lineage Tracker Backend',
                        412
                    )  

def delete_family_tree(username:str, user_group:str, uuid:str) -> str:
    '''
    Validates delete_family_tree action and appends to rdf graph
    '''
    
    # Checks if uuid exists, is not deleted, and 
    # no other dataset wasDerivedFrom this one
    delete_family_tree_conditions = validate_delete_family_tree(uuid)
    if sum(list(delete_family_tree_conditions.values())) == 2:

        logger.info(
            'DELETE_FAMILY_TREE - CONDITIONS FULFILLED'
        )
        
        # Get all uuid's for that family tree
        uuids = get_family_uuids_by_uuid(uuid)

        # Delete every uuid in the family tree
        for this_uuid in uuids:
            dataset_name = get_name_by_uuid(this_uuid)
            lineage_id = get_lineage_id_by_uuid(this_uuid)
            family_id = get_family_id(this_uuid)

            logger.debug(
                'DELETE_FAMILY_TREE - FAMILY_ID: %s', family_id
            )
            logger.debug(
                'DELETE_FAMILY_TREE - LINEAGE_ID: %s', lineage_id
            )
            logger.debug(
                'DELETE_FAMILY_TREE - DATASET_UUID: %s', this_uuid
            )

            dataset = Dataset(this_uuid, dataset_name, lineage_id, family_id)
            user = User(name=username, group=user_group)
            operation = Operation(
                type_='delete', 
                involved_dataset=dataset, 
                involved_user=user
            )

            document = Document(namespaces, user, dataset, operation)

            insert_SPARQL(document)

        return 'Dataset family tree successfully deleted.'
    else:
        if not delete_family_tree_conditions['dataset_exists']:
            logger.error(
            '412 - ERROR - DELETE FAMILY TREE - CONDITION FAILED - DATASET DOES NOT EXIST'
            )
            raise CustomError(
                'Dataset family tree cannot be deleted, because it does not exist.',
                'Lineage Tracker Backend',
                412
            )
        elif not delete_family_tree_conditions['not_deleted']:
            logger.error(
            '412 - ERROR - DELETE FAMILY TREE - CONDITION FAILED - DATASET WAS ALREADY DELETED'
            )
            raise CustomError(
                'Dataset family tree cannot be deleted, because it was already deleted.',
                'Lineage Tracker Backend',
                412
            ) 
        else:
            logger.error(
                '412 - ERROR - DELETE - CONDITION FAILED - DATASET DOES NOT EXIST'
                )
            raise CustomError(
                        'Dataset family tree cannot be deleted, because it does not exist.',
                        'Lineage Tracker Backend',
                        412
                    )  

def get_history_dataset(uuid:str, user_group=None, only_status=False) -> dict:
    '''
    Returns the history of a dataset given its uuid
    The history refers to all operations performed on a dataset
    '''
    logger.debug(
        'GET_HISTORY_DATASET - ONLY_STATUS:\n\n%s', only_status
    )
    
    # inverse create condition -> dataset has to exist
    if not validate_create(uuid):

        logger.info(
            'GET_HISTORY_DATASET - CONDITION FULFILLED'
        )

        # retrieving all the needed information with help of the SPARQL-wrapper,
        # which is querying the PIS
        ret = select_dataset_history_by_uuid_SPARQL(uuid, user_group)


        logger.debug(
            'GET_HISTORY_DATASET - RESULT:\n\n%s', ret['results']['bindings']
        )

        # creating the dictionary like response object out of the wrapper-result
        history = []
        for object_ in ret['results']['bindings']:
            entry = {
                    'operation_description': object_['operationDescription']['value'],
                    'username': object_['associatedUser']['value'],
                    'user_group': object_['associatedUserGroup']['value'],
                    'timestamp':object_['timestamp']['value']
                }
            
            if 'update' in entry['operation_description']:
                if 'previousUUID' in object_:
                    entry['from_uuid'] = object_['previousUUID']['value']
                if 'nextUUID' in object_:
                    entry['to_uuid'] = object_['nextUUID']['value']
                operation_description_list = entry['operation_description'].split(':')
                if len(operation_description_list) == 2:
                    entry['operation_description'] = operation_description_list[0]
                    entry['update_description'] = operation_description_list[1]

            history.append(entry)

        # sorting the collected events by date to make them chronological
        timestamps = [time.mktime(datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S').timetuple()) for entry in history]
        chronology = np.argsort(timestamps)
        history = np.array(history)[chronology].tolist()

        logger.debug(
            'GET_HISTORY_DATASET - HISTORY:\n\n%s', history
        )

        if only_status:
            last_operation = history[-1:][0]
            
            return {
                uuid: last_operation
            }
        
        else:
            return {
                uuid: history
                }
    
    else:
        if only_status:
            raise CustomError(
                'Dataset status cannot be shown, because the specified dataset does not exist.',
                'Lineage Tracker Backend',
                412
            )
        else:
            raise CustomError(
                'Dataset history cannot be shown, because the specified dataset does not exist.',
                'Lineage Tracker Backend',
                412
            )

def get_num_operations_dataset(uuid:str) -> dict:
    '''
    Returns the number of create, read, update, and delete operations 
    performed on a dataset given its uuid
    '''
    # inverse create condition -> dataset has to exist
    if not validate_create(uuid):

        logger.info(
            'GET_NUM_OPERATIONS_DATASET - CONDITION FULFILLED'
        )

        # Get the dataset history
        result = get_history_dataset(uuid)

        logger.info(
            'GET_NUM_OPERATIONS_DATASET - DATASET HISTORY - RESULT: \n%s', result
        )

        logger.info(
            'GET_NUM_OPERATIONS_DATASET - DATASET HISTORY - RESULT[UUID]: \n%s', result[uuid]
        )

        # Get the number of operations for create, read, update, delete
        operation_descriptions = [r['operation_description'] for r in result[uuid]]
        counts = loads(dumps(Counter(operation_descriptions)))
        
        # Ensure create, read, update, delete are in counts
        for operation in ['create', 'read', 'update', 'delete']:
            if counts.get(operation) is None:
                counts[operation] = 0

        logger.debug(
            'GET_NUM_OPERATIONS_DATASET - COUNTS:\n\n%s', counts
        )

        return {
            uuid: counts
            }

    else:
        raise CustomError(
            "Dataset's number of operations cannot be shown, because the specified dataset does not exist.",
            "Lineage Tracker Backend",
            412
        )

def get_diff_datasets(uuid_1:str, uuid_2:str) -> dict:
    '''
    Returns the datasets uuid_1, uuid_2, and 
    the diff between the two datasets
    '''
    # inverse create condition -> datasets have to exist
    if not validate_create(uuid_1) and not validate_create(uuid_2):

        logger.info(
            'GET_DIFF_DATASETS - CONDITION FULFILLED'
        )

        # Retrieve datasets from factory data storage, save to csv
        headers = {'Authorization': FDS_API_KEY}

        # Dataset 1
        data = {
            "asset_uuid": uuid_1,
            "JSON_output": True
        }
        response = requests.get(f'{FDS_API_URL}/api/tables/get_table', params=data, headers=headers)
        if response.status_code != 200:
            logger.error(
                'GET_DATASETS_DIFF - Error retrieving dataset 1 - %s', response.text
            )
            raise CustomError(
                "Failed to retrieve dataset 1.",
                "Lineage Tracker Backend",
                response.status_code
            )

        dataset_1 = loads(response.text)
        dataset_1_key = dataset_to_csv(dataset_1, 'diff_csv/dataset_1.csv')
        logger.info(
            'GET_DATASETS_DIFF - dataset_1 - %s', dataset_1
        )

        # Dataset 2
        data = {
            "asset_uuid": uuid_2,
            "JSON_output": True
        }
        response = requests.get(f'{FDS_API_URL}/api/tables/get_table', params=data, headers=headers)
        if response.status_code != 200:
            logger.error(
                'GET_DATASETS_DIFF - Error retrieving dataset 2 - %s', response.text
            )
            raise CustomError(
                "Failed to retrieve dataset 2.",
                "Lineage Tracker Backend",
                response.status_code
            )
        logger.info(
            'GET_DATASETS_DIFF - response_2 - %s', response
        )
        dataset_2 = loads(response.text)
        dataset_2_key = dataset_to_csv(dataset_2, 'diff_csv/dataset_2.csv')
        logger.info(
            'GET_DATASETS_DIFF - dataset_2 - %s', dataset_2
        )

        # Calculate diff of two datasets
        diff = compare(
            load_csv(open("diff_csv/dataset_1.csv"), key=dataset_1_key),
            load_csv(open("diff_csv/dataset_2.csv"), key=dataset_2_key)
        )

        # Delete from csv
        os.remove("diff_csv/dataset_1.csv")
        os.remove("diff_csv/dataset_2.csv")

        result = {
            'dataset_1': dataset_1,
            'dataset_2': dataset_2,
            'diff': diff,
        }
        logger.info(
            'GET_DATASETS_DIFF - result - %s', result
        )

        return result

    else:
        raise CustomError(
            "Datasets' diff cannot be shown, because the specified datasets do not exist.",
            "Lineage Tracker Backend",
            412
        )

def dataset_to_csv(dataset, filename):
    '''
    Converts dataset to csv file
    Returns name of index column
    '''
    # Check if data_model is present
    if "data_model" in dataset[0] and "columns" in dataset[0]["data_model"]:
        # Extract column names from data_model
        columns = [col[0] for col in dataset[0]["data_model"]["columns"]]
    else:
        # If data_model is not present, use generic column names
        if len(dataset[0]["data"]["rows"]) > 0:
            columns = [f"column_{i+1}" for i in range(len(dataset[0]["rows"][0]))]
        else:
            columns = []
    
    # Extract rows
    rows = dataset[0]["data"]["rows"]
    
    # Create a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)
    
    # Write DataFrame to CSV file
    df.to_csv(filename, index=False)

    return columns[0]

def get_history_user(username:str) -> dict:
    '''
    Returns the history of a user given its username
    The user history refers to all operations performed by a user on a dataset
    '''
    ret = select_user_history_by_uuid_SPARQL(username)

    logger.debug(
        'GET_HISTORY_USER - RESULT:\n\n%s', ret['results']['bindings']
    )

    history = []
    for object_ in ret['results']['bindings']:
        entry = {
                'user_group': object_['associatedUserGroup']['value'],
                'operation_description': object_['operationDescription']['value'],
                'dataset_uuid': object_['datasetUUID']['value'],
                'dataset_name': object_['datasetTitle']['value'],
                'timestamp': object_['timestamp']['value']
            } 
        if 'update' in entry['operation_description']:
            entry['uuid_prev'] = object_['previousUUID']['value']
            operation_description_list = entry['operation_description'].split(':')
            if len(operation_description_list) == 2:
                entry['operation_description'] = operation_description_list[0]
                entry['update_description'] = operation_description_list[1]

        history.append(entry)

    timestamps = [time.mktime(datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S').timetuple()) for entry in history]
    chronology = np.argsort(timestamps)
    history = np.array(history)[chronology].tolist()

    logger.debug(
        'GET_HISTORY_USER - HISTORY:\n\n%s', history
    )
    
    if len(history) == 0:
        raise CustomError(
            'User history cannot be shown, because the specified user does not exist.',
            'Lineage Tracker Backend',
            412
        )
    
    return {
        username: history
        }

def get_lineage_by_uuid(uuid:str) -> dict:
    '''
    Returns the dataset lineage given its uuid
    A dataset family tree is split into different lineages
    The lineage refers to the heritage of a dataset associated with the specified lineage_id
    '''
    lineage = {}
    lineage_id = get_lineage_id_by_uuid(uuid)
    if lineage_id is None:
        raise CustomError(
            'The specified lineage ID does not exist.',
            'Lineage Tracker Backend',
            412
        ) 
    ret = select_lineage_by_lineage_id_SPARQL(lineage_id)

    logger.debug(
        'GET_LINEAGE - RESULT:\n\n%s', ret['results']['bindings']
    )

    timestamps = [time.mktime(datetime.strptime(entry['timestamp']['value'], '%Y-%m-%d %H:%M:%S').timetuple()) for entry in ret['results']['bindings']]
    chronology = np.argsort(timestamps)
    for index, version in enumerate(np.array(ret['results']['bindings'])[chronology]):
        try:
            lineage[version['id']['value']] = {
                'username': version['operationBy']['value'],
                'user_group': version['associatedUserGroup']['value'],
                'dataset_name': version['title']['value'],
                'timestamp': version['timestamp']['value'],
                'operation_description': version['operationDescription']['value'],
                'derived_from': version['previousUUID']['value']    
            }
        except KeyError:
            lineage[version['id']['value']] = {
                'username': version['operationBy']['value'],
                'user_group': version['associatedUserGroup']['value'],
                'dataset_name': version['title']['value'],
                'timestamp': version['timestamp']['value'],
                'operation_description': version['operationDescription']['value'],
                'derived_from': None
            }
        # If update operation, operation description and update description need to be separated
        if 'update' in version['operationDescription']['value']:
            operation_description_list = version['operationDescription']['value'].split(':')
            if len(operation_description_list) == 2:
                lineage[version['id']['value']]['operation_description'] = operation_description_list[0]
                lineage[version['id']['value']]['update_description'] = operation_description_list[1]
    if len(lineage) > 0:
        return lineage
    else:
        raise CustomError(
            'Dataset lineage cannot be shown, because the specified dataset does not exist.',
            'Lineage Tracker Backend',
            412
        ) 

def get_lineage_by_lineage_id(lineage_id:str) -> dict:
    '''
    Returns the dataset lineage given its lineage_id
    A dataset family tree is split into different lineages
    The lineage refers to the heritage of a dataset associated with the specified lineage_id
    '''
    lineage = {}
    ret = select_lineage_by_lineage_id_SPARQL(lineage_id)

    logger.debug(
        'GET_LINEAGE - RESULT:\n\n%s', ret['results']['bindings']
    )

    timestamps = [time.mktime(datetime.strptime(entry['timestamp']['value'], '%Y-%m-%d %H:%M:%S').timetuple()) for entry in ret['results']['bindings']]
    chronology = np.argsort(timestamps)
    for index, version in enumerate(np.array(ret['results']['bindings'])[chronology]):
        try:
            lineage[version['id']['value']] = {
                'username': version['operationBy']['value'],
                'user_group': version['associatedUserGroup']['value'],
                'dataset_name': version['title']['value'],
                'timestamp': version['timestamp']['value'],
                'operation_description': version['operationDescription']['value'],
                'derived_from': version['previousUUID']['value']    
            }
        except KeyError:
            lineage[version['id']['value']] = {
                'username': version['operationBy']['value'],
                'user_group': version['associatedUserGroup']['value'],
                'dataset_name': version['title']['value'],
                'timestamp': version['timestamp']['value'],
                'operation_description': version['operationDescription']['value'],
                'derived_from': None
            }
        # If update operation, operation description and update description need to be separated
        if 'update' in lineage[version['id']['value']]['operation_description']:
            operation_description_list = lineage[version['id']['value']]['operation_description'].split(':')
            if len(operation_description_list) == 2:
                lineage[version['id']['value']]['operation_description'] = operation_description_list[0]
                lineage[version['id']['value']]['update_description'] = operation_description_list[1]
    if len(lineage) > 0:
        return lineage
    else:
        raise CustomError(
            'The specified lineage ID does not exist',
            'Lineage Tracker Backend',
            412
        ) 

def get_family_tree(uuid:str) -> dict:
    '''
    Returns the entire family tree given a uuid
    The family tree includes all tree branches/lineage_ids
    '''
    logger.info("*** Inside get_family_tree")
    family_id = get_family_id(uuid)
    ret = get_lineage_ids_by_family_id(family_id)
    lineage_ids = np.unique(ret)

    if len(lineage_ids) == 0:
        raise CustomError(
            'Dataset family tree cannot be shown, because the specified dataset does not exist.',
            'Lineage Tracker Backend',
            412
        )
    
    family_tree = {lineage_id: get_lineage_by_lineage_id(lineage_id) for lineage_id in lineage_ids}

    logger.debug(
        'GET_FAMILY_TREE - FAMILY TREE:\n\n%s', family_tree
    )
    
    return family_tree
