import logging
import os
from config import Config
from flask import Blueprint, Flask, jsonify, request, make_response, send_from_directory
from importlib.metadata import distribution, metadata, version
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from functools import wraps
from logging.config import dictConfig
from flask_restx import Api
from flask_restx.apidoc import apidoc
from json import dumps, loads

from identity_manager import IdentityManager, IdentityManagerApi
from logic_layer import create, read, update, delete, delete_family_tree, get_history_dataset, get_num_operations_dataset, get_history_user, get_lineage_by_uuid, get_family_tree, get_diff_datasets
from tools.error_handler import CustomError
from versioning import add_versioning

FDS_API_URL = 'https://develop.pistis-market.eu/srv/factory-data-storage'
FDS_API_KEY = os.getenv('FDS_API_KEY', '')
LT_API_KEY = os.getenv('LT_API_KEY', '')
CLIENT_ID = os.getenv('CLIENT_ID', '')
CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')

logger = logging.getLogger('api')

app = Flask(__name__)
app.config.from_object(Config)
app.debug = True

CORS(app, supports_credentials=True)
app.config['CORS_SUPPORTS_CREDENTIALS'] = True

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    os.getenv('SWAGGER_SWAGGER_URL', ''),
    os.getenv('SWAGGER_API_URL', '/static/swagger.json'),
    config={
        'app_name': "Lineage Tracker Backend"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/')

log_level = os.getenv('LOG_LEVEL', 'INFO')

dictConfig({ 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '\n%(asctime)s [%(levelname)s] %(name)s:\n\n %(message)s\n'
        },
    },
    'handlers': { 
        'default': { 
            'level': log_level,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  
        },
    },
    'loggers': { 
        'api': { 
            'handlers': ['default'],
            'level': log_level,
            'propagate': False
        },
        'wrapper': {  
            'handlers': ['default'],
            'level': log_level,
            'propagate': False
        },
        'operation_validator': {  
            'handlers': ['default'],
            'level': log_level,
            'propagate': False
        },
        'logic_layer': {  
            'handlers': ['default'],
            'level': log_level,
            'propagate': False
        },
        'identity_manager': {  
            'handlers': ['default'],
            'level': log_level,
            'propagate': False
        },
        
    } 
})

@app.errorhandler(CustomError)
def handleError(e):
    return make_response(jsonify(e.__dict__), e.status_code)

# API Key specification
def token_required(f):
    '''decorator function to check tokens in header'''
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.headers.get("Authorization", None)
        app.logger.info("TOKEN: %s", token)
        app.logger.info("LT_API_KEY: %s", LT_API_KEY)
        if token and not token.startswith("Bearer"):
            if token == LT_API_KEY:
                return f(*args,**kwargs)
            else:
                raise CustomError(
                    'Unauthorized access.',
                    'Lineage Tracker Backend',
                    401
                )
        elif token and token.startswith("Bearer "):
            # NOTE: Documentation here https://docs.pistis-market.eu/developers/keycloak/authorization-token
            # TODO: IdentityManager permission will likely have datasetId in future, but not ready yet
            identity_object = IdentityManager('application/x-www-form-urlencoded', 'urn:ietf:params:oauth:grant-type:uma-ticket', '')
            bearer_token = token.split(' ')[1]
            response = IdentityManagerApi().user_account_authorize(identity_object, bearer_token)
            if response.status_code != 200:
                raise CustomError(
                    'Unauthorized access.',
                    'Lineage Tracker Backend',
                    401
                )
            return f(*args,**kwargs)
        else:
            raise CustomError(
                'API Key or token is missing, authentication failed.',
                'Lineage Tracker Backend',
                401
            )
    return wrapped

@app.route('/create_dataset', methods=['POST'])
@token_required
def create_dataset():
    '''
    Document the creation of a new dataset in the Lineage Information Store.
    '''
    kwargs = request.json
    app.logger.info("*** Inside create dataset")
    try:
        result = create(**kwargs)
        app.logger.info(
            'SUCCESS - DATA STORAGE - CREATE - %s', kwargs['uuid']
            )
    except TypeError:
        app.logger.error(
            'ERROR - 400 - CREATE - The shape of the provided arguments is faulty!'
            )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )
    return result

@app.route('/read_dataset', methods=['POST'])
@token_required
def read_dataset():
    '''
    Document the reading of an existing dataset in the Lineage Information Store.
    '''
    kwargs = request.json
    try:
        result = read(**kwargs)
        app.logger.info(
            'SUCCESS - DATA STORAGE - READ - %s', kwargs['uuid']
            )
    except TypeError as e:
        app.logger.error(
            'ERROR - 400 - READ - The shape of the provided arguments is faulty!'
            )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )
    return result

@app.route('/update_dataset', methods=['POST'])
@token_required
def update_dataset():
    '''
    Document the updating of an existing dataset in the Lineage Information Store.
    '''
    kwargs = request.json
    try:
        result = update(**kwargs)
        app.logger.info(
            'SUCCESS - DATA STORAGE - UPDATE - %s', kwargs['uuid']
            )
    except TypeError:
        app.logger.error(
            'ERROR - 400 - UPDATE - The shape of the provided arguments is faulty!'
            )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )

    return result

@app.route('/delete_dataset', methods=['POST'])
@token_required
def delete_dataset():
    '''
    Document the deletion of an existing dataset in the Lineage Information Store.
    '''
    kwargs = request.json
    try:
        result = delete(**kwargs)
        app.logger.info(
            'SUCCESS - DATA STORAGE - DELETE - %s', kwargs['uuid']
            )
    except TypeError as e:
        app.logger.error(
            'ERROR - 400 - DELETE - The shape of the provided arguments is faulty!'
            )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )

    return result

@app.route('/delete_family_tree', methods=['POST'])
@token_required
def delete_ft():
    '''
    Document the deletion of the entire family tree of an existing dataset in the Lineage Information Store.
    '''
    kwargs = request.json
    try:
        result = delete_family_tree(**kwargs)
        app.logger.info(
            'SUCCESS - DATA STORAGE - DELETE - %s', kwargs['uuid']
            )
    except TypeError as e:
        app.logger.error(
            'ERROR - 400 - DELETE - The shape of the provided arguments is faulty!'
            )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )

    return result

@app.route('/get_dataset_history', methods=['GET'])
@token_required
def get_dataset_history():
    '''
    Get the complete operation history associated with a dataset from the Lineage Information Store.
    '''
    uuid = request.args.get('uuid', None)
    user_group = request.args.get('user_group', None)

    if uuid is not None:
        result = get_history_dataset(uuid, user_group)
        app.logger.info(
            'SUCCESS - GET_DATASET_HISTORY'
            )
    else:
        app.logger.error(
            'ERROR - GET_DATASET_HISTORY - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )

    return jsonify(result)

@app.route('/get_user_history', methods=['GET'])
@token_required
def get_user_history():
    '''
    Get the complete history of performed operations associated with a user from the Lineage Information Store.
    '''
    username = request.args.get('username')
    if username is not None:
        result = get_history_user(username)
        app.logger.info(
            'SUCCESS - GET_USER_HISTORY'
        )
    else:
        app.logger.error(
            'ERROR - GET_USER_HISTORY - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )

    return jsonify(result)

@app.route('/get_dataset_status', methods=['GET'])
@token_required
def get_dataset_status():
    '''
    Get the last operation performed on dataset from the Lineage Information Store.
    '''
    uuid = request.args.get('uuid')
    if uuid is not None:
        result = get_history_dataset(uuid, only_status=True)
        app.logger.info(
            'SUCCESS - GET_DATASET_STATUS'
            )
    else:
        app.logger.error(
            'ERROR - GET_DATASET_STATUS - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )
    return jsonify(result)

@app.route('/get_dataset_num_operations', methods=['GET'])
@token_required
def get_dataset_num_operations():
    '''
    Count the number of create, read, update, and delete operations performed on a dataset 
    from the Lineage Information Store.
    '''
    uuid = request.args.get('uuid')
    if uuid is not None:
        result = get_num_operations_dataset(uuid)
        app.logger.info(
            'SUCCESS - GET_DATASET_NUM_OPERATIONS'
            )
    else:
        app.logger.error(
            'ERROR - GET_DATASET_NUM_OPERATIONS - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )
    return jsonify(result)

@app.route('/get_dataset_lineage', methods=['GET'])
@token_required
def get_dataset_lineage():
    '''
    Get the complete lineage of a dataset from the Lineage Information Store.
    '''
    uuid = request.args.get('uuid')
    if uuid is not None:
        result = get_lineage_by_uuid(uuid)
        app.logger.info(
            'SUCCESS - GET_DATASET_LINEAGE'
        )
    else:
        app.logger.error(
            'ERROR - GET_DATASET_LINEAGE - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )

    return jsonify(result)

@app.route('/get_dataset_family_tree', methods=['GET'])
@token_required
def get_dataset_family_tree():
    '''
    Get the complete family tree of a dataset from the Lineage Information Store.
    '''
    uuid = request.args.get('uuid')
    if uuid is not None:
        ft = get_family_tree(uuid)
        app.logger.info(
            'GET_DATASET_FAMILY_TREE - WITHOUT VERSIONS: %s', ft
            )
        ft_versions = add_versioning(ft)
        app.logger.info(
            'GET_DATASET_FAMILY_TREE - WITH VERSIONS: %s', ft_versions
            )
        app.logger.info(
            'SUCCESS - GET_DATASET_FAMILY_TREE'
            )
    else:
        app.logger.error(
            'ERROR - GET_DATASET_FAMILY_TREE - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )
    
    return jsonify(ft_versions)

@app.route('/get_datasets_diff', methods=['GET'])
@token_required
def get_datasets_diff():
    '''
    Get the diff of two datasets from the Factory Data Storage.
    '''
    uuid_1 = request.args.get('uuid_1')
    uuid_2 = request.args.get('uuid_2')
    if uuid_1 is not None and uuid_2 is not None:
        
        result = get_diff_datasets(uuid_1, uuid_2)

        app.logger.info(
            'SUCCESS - GET_DATASETS_DIFF - %s', result
            )
    else:
        app.logger.error(
            'ERROR - GET_DATASET_FAMILY_TREE - The shape of the provided arguments is faulty!'
        )
        raise CustomError(
            'The shape of the provided arguments is faulty!',
            'Lineage Tracker Backend',
            400
        )
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
