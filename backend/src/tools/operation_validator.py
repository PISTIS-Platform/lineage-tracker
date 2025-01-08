import logging
from tools.sparql.wrapper import validate_operation_by_uuid_SPARQL, \
    get_name_by_uuid_SPARQL, get_lineage_id_by_uuid_SPARQL, get_lineage_id_by_family_id_SPARQL, get_family_id_SPARQL, get_family_uuids_by_uuid_SPARQL, \
        check_lineage_node_SPARQL, check_was_derived_from_SPARQL

logger = logging.getLogger('operation_validator')

def validate_create(uuid:str) -> bool:
    '''
    Validates if a dataset can be created based on the condition:
    1. The dataset does not already exist
    '''

    ret = validate_operation_by_uuid_SPARQL(uuid)

    logger.debug(
        'VALIDATE_CREATE - RESULT:\n\n%s', ret['results']['bindings']
    )
    
    # 1. Dataset exists?
    condition = len(ret['results']['bindings']) == 0

    logger.debug('VALIDATE_CREATE - CONDITION: %s', condition)

    return condition

def validate_read(uuid:str):
    '''
    Validates if a dataset can be read based on the conditions:
    1. dataset exists
    2. dataset is not deleted
    '''
    ret = validate_operation_by_uuid_SPARQL(uuid)

    logger.debug(
        'VALIDATE_READ - RESULT:\n\n%s', ret['results']['bindings']
    )

    # Condition 1. Check that dataset exists
    dataset_exists = len(ret['results']['bindings']) > 0

    # Condition 2. Check that dataset has not been deleted
    # Check if delete operations have been performed on this uuid
    operations = [entry['operationFrom']['value'] for entry in ret['results']['bindings']]
    logger.debug("operation_validator.py/validate_read - operations: %s", operations)
    not_deleted = len(list(filter(lambda o: 'delete' in o, operations))) == 0
    logger.debug("operation_validator.py/validate_read - not_deleted: %s", not_deleted)

    conditions = {
        'dataset_exists': dataset_exists,
        'not_deleted': not_deleted
    }

    logger.debug(
        'VALIDATE_READ - CONDITIONS: %s', conditions
    )

    return conditions

def validate_update(uuid:str) -> dict:
    '''
    Validates if a dataset can be updated based on the conditions:
    1. The dataset exists
    2. The dataset has not been deleted
    '''
    ret = validate_operation_by_uuid_SPARQL(uuid)

    logger.debug(
        'VALIDATE_UPDATE - RESULT:\n\n%s', ret['results']['bindings']
    )
    
    # 1. Dataset exists?
    dataset_exists = len(ret['results']['bindings']) > 0
    operations = [entry['operationFrom']['value'] for entry in ret['results']['bindings']]
    
    # 2. Dataset deleted?
    not_deleted = len(list(filter(lambda o: 'delete' in o, operations))) == 0

    conditions = {
        'dataset_exists': dataset_exists,
        'not_deleted': not_deleted
    }

    logger.debug(
        'VALIDATE_UPDATE - CONDITIONS: %s', conditions
    )
    
    return conditions

def validate_delete(uuid:str) -> dict:
    '''
    Validates if a dataset can be deleted based on the conditions:
    1. The dataset exists
    2. The dataset has not been deleted
    3. There is not an undeleted dataset this dataset wasDerivedFrom
    '''

    ret = validate_operation_by_uuid_SPARQL(uuid)

    logger.debug(
        'VALIDATE_DELETE - RESULT:\n\n%s', ret['results']['bindings']
    )
    
    # 1. Dataset exists?
    dataset_exists = len(ret['results']['bindings']) > 0

    # 2. Dataset deleted?
    operations = [entry['operationFrom']['value'] for entry in ret['results']['bindings']]
    not_deleted = len(list(filter(lambda o: 'delete' in o, operations))) == 0

    # 3. Was any other undeleted dataset derivedFrom this dataset?
    # This returns any entities that wasDerivedFrom and all of their operations
    ret = check_was_derived_from_SPARQL(uuid)
    logger.debug(
        'VALIDATE_UPDATE - was_derived_from check:\n\n%s', ret['results']['bindings']
    )
    logger.debug("*** Inside operationvalidator/validate_delete")
    logger.debug("Ret: %s", ret)

    not_undeleted_was_derived_from = False
    if len(ret['results']['bindings']) != 0:
        # For each entity returned, check if the entity was deleted
        entity_dict = {}
        for entity in ret['results']['bindings']:
            this_entity_val = entity['entity']['value']
            is_entity_deleted = ('delete' in entity['operationFrom']['value'])
            if this_entity_val in entity_dict:
                if not entity_dict[this_entity_val]:
                    entity_dict[this_entity_val] = is_entity_deleted
            else:
                entity_dict[this_entity_val] = is_entity_deleted

        # Check if all entities returned have been deleted
        are_all_entities_deleted = True
        for _, val in entity_dict.items():
            if not val:
                are_all_entities_deleted = False
                break
        
        # If all wasDerivedFrom entities are deleted, condition passes
        # Otherwise, condition fails
        not_undeleted_was_derived_from = are_all_entities_deleted
    else:
        # If no wasDerivedFrom entities, condition passes
        not_undeleted_was_derived_from = True

    conditions = {
        'dataset_exists': dataset_exists,
        'not_deleted': not_deleted,
        'not_undeleted_was_derived_from': not_undeleted_was_derived_from
    }

    logger.debug(
        'VALIDATE_DELETE - CONDITIONS: %s', conditions
    )
    
    return conditions

def validate_delete_family_tree(uuid:str) -> dict:
    '''
    Validates if a family tree can be deleted based on the conditions:
    1. The dataset exists
    2. The dataset has not been deleted
    '''

    ret = validate_operation_by_uuid_SPARQL(uuid)

    logger.debug(
        'VALIDATE_DELETE - RESULT:\n\n%s', ret['results']['bindings']
    )
    
    # 1. Dataset exists?
    dataset_exists = len(ret['results']['bindings']) > 0

    # 2. Dataset deleted?
    operations = [entry['operationFrom']['value'] for entry in ret['results']['bindings']]
    not_deleted = len(list(filter(lambda o: 'delete' in o, operations))) == 0

    conditions = {
        'dataset_exists': dataset_exists,
        'not_deleted': not_deleted,
    }

    logger.debug(
        'VALIDATE_DELETE - CONDITIONS: %s', conditions
    )
    
    return conditions

def check_lineage_node(uuid:str) -> bool:
    '''
    Checks if the lineage splits and a new lineage_id needs to be created
    Lineage splits if there is already a dataset that wasDerivedFrom uuid
    '''
    ret = check_lineage_node_SPARQL(uuid)
    
    return len(ret['results']['bindings']) > 0

def get_name_by_uuid(uuid:str):
    '''
    Returns the name of a dataset given its uuid
    '''
    ret = get_name_by_uuid_SPARQL(uuid)

    logger.debug(
        'CHECK_LINEAGE_ID_BY_UUID - RESULT:\n\n%s', ret['results']['bindings']
    )

    name = ret['results']['bindings'][-1:][0]['name']['value']

    return name

def get_lineage_id_by_uuid(uuid:str) -> str :
    '''
    Given a dataset's uuid, returns its lineageId
    Return format: lineageId
    '''
    ret = get_lineage_id_by_uuid_SPARQL(uuid)

    logger.debug(
        'CHECK_LINEAGE_ID_BY_UUID - RESULT:\n\n%s', ret['results']['bindings']
        )
    
    # Format result
    result = None
    bindings = ret['results']['bindings']
    if len(bindings) == 1:
        result = bindings[0]['lineageId']['value']

    return result

def get_lineage_ids_by_family_id(family_id:str) -> str :
    '''
    Given a dataset's family_id, returns all of the associated lineage_ids
    Return format: [lineageId1, lineageId2, ...]
    '''
    ret = get_lineage_id_by_family_id_SPARQL(family_id)

    logger.debug(
        'CHECK_LINEAGE_IDS_BY_FAMILY_ID - RESULT:\n\n%s', ret['results']['bindings']
        )

    # Format return values
    result = []
    bindings = ret['results']['bindings']
    if len(bindings) > 0:
        for binding in bindings:
            result.append(binding['lineageId']['value'])

    return result

def get_family_id(uuid:str) -> str :
    '''
    Given a dataset's uuid, returns the associated familyId
    Return format: familyId
    '''
    ret = get_family_id_SPARQL(uuid)

    logger.debug(
        'GET_FAMILY_ID - RESULT:\n\n%s', ret['results']['bindings']
        )

    # Format return value
    result = None
    bindings = ret['results']['bindings']
    if len(bindings) == 1:
        result = bindings[0]['familyId']['value']
    return result

def get_family_uuids_by_uuid(uuid:str) -> list :
    '''
    Given a dataset's uuid, returns all uuids for that family tree
    Return format: ['uuid1', 'uuid2']
    '''
    logger.debug("*** Inside get_family_uuids_by_uuid")
    ret = get_family_uuids_by_uuid_SPARQL(uuid)

    logger.debug(
        'GET_FAMILY_UUIDS_BY_UUID - RESULT:\n\n%s', ret['results']['bindings']
        )
    
    # Format return value
    result = []
    bindings = ret['results']['bindings']
    if len(bindings) > 0:
        for this_uuid in bindings:
            this_uuid_val = this_uuid['uuid']['value']
            result.append(this_uuid_val)

    return result
   