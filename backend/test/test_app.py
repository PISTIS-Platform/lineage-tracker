import os
import pytest
import requests
import time
from json import loads, dumps
from faker import Faker

FDS_API_URL = 'https://develop.pistis-market.eu/srv/factory-data-storage'
FDS_API_KEY = os.getenv('FDS_API_KEY', '')
LT_API_URL = 'http://127.0.0.1:8080/'
LT_API_KEY = os.getenv('LT_API_KEY', '')

fake = Faker()
headers = {'Authorization': LT_API_KEY}

###############################################################################
############################### AUTHENTICATION ################################
###############################################################################

################################ AUTH TOKEN ###################################

def test_auth_token_200():
  '''
  Tests successful authentication using an auth token
  '''

  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }

  headers = {'Authorization': '3yF8!oNEzR2/bHDx*WU#F@^pLM9NQ$a6'}

  # Make a request to the /create_dataset route to test authentication
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

def test_auth_token_401():
  '''
  Tests failed authentication using an incorrect auth token
  '''

  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }

  headers = {'Authorization': '1yF8!oNEzR2/bHDx*WU#F@^pLM9NQ$a6'}

  # Make a request to the /create_dataset route to test authentication
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 401
  response_data = loads(response.text)
  assert 'message' in response_data
  assert response_data['message'] == 'Unauthorized access.'

############################### BEARER TOKEN ##################################

def test_bearer_token_200():
  '''
  Tests successful authentication using a bearer token
  '''

  # Get bearer token
  data = {
    'grant_type': 'client_credentials',
    'client_id': 'pistis-test-only',
    'client_secret': 'DYuAlXn8kC1SVzFiYgApfjcodZhdxreL'
  }
  response = requests.post('https://auth.pistis-market.eu/auth/realms/PISTIS/protocol/openid-connect/token', data=data)
  assert response.status_code == 200
  response_data = loads(response.text)
  assert 'access_token' in response_data
  bearer_token = loads(response.text)['access_token']

  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  headers = {
    'Authorization': f'Bearer {bearer_token}'
  }

  # Make a request to the /create_dataset route to test authentication
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

def test_bearer_token_401():
  '''
  Tests failed authentication using an incorrect bearer token
  '''

  # Get bearer token
  data = {
    'grant_type': 'client_credentials',
    'client_id': 'pistis-test-only',
    'client_secret': 'DYuAlXn8kC1SVzFiYgApfjcodZhdxreL'
  }
  response = requests.post('https://auth.pistis-market.eu/auth/realms/PISTIS/protocol/openid-connect/token', data=data)
  assert response.status_code == 200
  response_data = loads(response.text)
  assert 'access_token' in response_data
  bearer_token = loads(response.text)['access_token']

  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  headers = {
    'Authorization': f'Bearer {bearer_token}1'
  }

  # Make a request to the /create_dataset route to test authentication
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 401
  response_data = loads(response.text)
  assert 'message' in response_data
  assert response_data['message'] == 'Unauthorized access.'

###############################################################################
####################### OPERATION DOCUMENTATION ROUTES ########################
###############################################################################

############################## CREATE_DATASET #################################

def test_create_200():
  '''
  Tests create_dataset success
  '''

  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }

  # Make a request to the /create_dataset route
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Creation of the dataset successfully documented.'

def test_create_400():
  '''
  Tests create_dataset 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data_faulty = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  data_faulty = {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  data_faulty = {
    "uuid": uuid,
    "user_group": user_group,
    "dataset_name": dataset_name,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  data_faulty = {
    "uuid": uuid,
    "username": username,
    "dataset_name": dataset_name,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_create_401():
  '''
  Tests create_dataset 401 error
  Error: Unauthorized Access!
  '''

  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }

  # Make a request to the /create_dataset route
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_create_412():
  '''
  Tests create_dataset 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset has already been created
  '''
  # Create dataset
  data = {
    "username": fake.name(),
    "user_group": fake.name(),
    "uuid": fake.uuid4(),
    "dataset_name": fake.name()
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Try to create the same dataset again
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset with specified UUID already exists and cannot be created.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

################################ READ_DATASET #################################

def test_read_200():
  '''
  Tests read_dataset success
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Read dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Reading operation successfully documented.'

def test_read_400():
  '''
  Tests read_dataset 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  data_faulty = {
    "uuid": uuid,
    "username": username,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  data_faulty = {
    "uuid": uuid,
    "user_group": user_group,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  data_faulty = {
    "username": username,
    "user_group": user_group,
  }

  # 400 error
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_read_401():
  '''
  Tests read_dataset 401 error
  Error: Unauthorized Access!
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Read dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_read_412():
  '''
  Tests read_dataset 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset not created or deleted
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()

  # 412 error when dataset not created
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be read, because it does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Delete dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)

  # 412 error when trying to read a deleted dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be read, because it was deleted.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################### UPDATE_DATASET ################################

def test_update_200():
  '''
  Tests update_dataset success
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'updating the dataset successfully documented.'

def test_update_400():
  '''
  Tests update_dataset 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data\
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()
  update_description = 'add_rows'

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # 400 error
  data_faulty = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "user_group": user_group,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "username": username,
    "user_group": user_group,
    "uuid_prev": uuid_prev,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "username": username,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_update_401():
  '''
  Tests update_dataset 401 error
  Error: Unauthorized Access!
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
    "update_description": update_description,
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_update_412():
  '''
  Tests update_dataset 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset not created or deleted
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()
  update_description = 'add_rows'

  # 412 error when dataset not created
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be updated, because it does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Delete dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)

  # 412 error when trying to update a deleted dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "uuid_prev": uuid_prev,
    "update_description": update_description,
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be updated, because it was deleted.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################### DELETE_DATASET ################################

def test_delete_200():
  '''
  Tests delete_dataset success
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Delete dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Dataset successfully deleted.'

def test_delete_multiple_200():
  '''
  Tests delete_dataset success with multiple datasets
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid1 = fake.uuid4()
  uuid2 = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid2,
    "uuid_prev": uuid1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Delete dataset 2
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid2,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Dataset successfully deleted.'

  # Delete dataset 1
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid1,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Dataset successfully deleted.'

def test_delete_400():
  '''
  Tests delete_dataset 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # 400 error
  data_faulty = {
    "username": username
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_delete_401():
  '''
  Tests delete_dataset 401 error
  Error: Unauthorized Access!
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Delete dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_delete_412():
  '''
  Tests delete_dataset 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset not created, was deleted, or
  another dataset wasDerivedFrom the dataset
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()

  # 412 error when dataset not created
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be deleted, because it does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Delete dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)

  # 412 error when trying to delete a deleted dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be deleted, because it was already deleted.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

  # Create dataset
  uuid1 = fake.uuid4()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  uuid2 = fake.uuid4()
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid2,
    "uuid_prev": uuid1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Try to delete first dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid1,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset cannot be deleted, because another undeleted dataset wasDerivedFrom this dataset.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################ DELETE_FAMILY_TREE ###############################

def test_delete_family_tree_200():
  '''
  Tests delete_family_tree success
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  username = fake.name()
  uuid_new = fake.uuid4()
  dataset_name = fake.name()
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_new,
    "uuid_prev": uuid,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Delete dataset's family tree
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Dataset family tree successfully deleted.'

  # Check that uuid_new was updated and deleted
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_new
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data, headers=headers)
  response_data = sorted(loads(response.text)[uuid_new], key=lambda x: x['operation_description'])

  assert response.status_code == 200
  assert response_data[0]['operation_description'] == 'delete'

  assert response.status_code == 200
  assert response_data[1]['operation_description'] == 'update'


def test_delete_family_tree_400():
  '''
  Tests delete_dataset 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # 400 error
  data_faulty = {
    "username": username,
    "user_group": user_group
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "uuid": uuid,
    "user_group": user_group,
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "username": username,
    "uuid": uuid
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_delete_family_tree_401():
  '''
  Tests delete_family_tree 401 error
  Error: Unauthorized Access!
  '''

  # Create dataset
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Delete dataset family tree
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_delete_family_tree_412():
  '''
  Tests delete_dataset 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset not created or was already deleted
  '''
  # Delete dataset's family tree before dataset was created
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset family tree cannot be deleted, because it does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

  # Create dataset
  dataset_name = fake.name()
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  username = fake.name()
  uuid_new = fake.uuid4()
  dataset_name = fake.name()
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_new,
    "uuid_prev": uuid,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Delete dataset's family tree
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data, headers=headers)
  assert response.status_code == 200
  assert response.text == 'Dataset family tree successfully deleted.'

  # Delete dataset's family tree again
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset family tree cannot be deleted, because it was already deleted.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

###############################################################################
######################## INFORMATION RETRIEVAL ROUTES #########################
###############################################################################
  
############################## GET_USER_HISTORY ###############################

def test_get_user_history_200():
  '''
  Tests get_user_history success
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()

  # Add user actions
  # Create
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)   # We need time.sleep(1) because the results are ordered by timestamp
  # Read
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)
  # Delete
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)
  
  # Test user_history
  data = {
    "username": username
  }
  response = requests.get(f'{LT_API_URL}/get_user_history', params=data, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  assert len(response_json[username]) == 3
  # Create
  response_create = response_json[username][0]
  del response_create['timestamp']
  assert response_create == {
    "user_group": user_group,
    "dataset_name": dataset_name,
    "dataset_uuid": uuid_prev,
    "operation_description": "create"
  }
  # Read
  response_read = response_json[username][1]
  del response_read['timestamp']
  assert response_read == {
    "user_group": user_group,
    "dataset_name": dataset_name,
    "dataset_uuid": uuid_prev,
    "operation_description": "read"
  }
  # Delete
  response_delete = response_json[username][2]
  del response_delete['timestamp']
  assert response_delete == {
    "user_group": user_group,
    "dataset_name": dataset_name,
    "dataset_uuid": uuid_prev,
    "operation_description": "delete"
  }

def test_get_user_history_400():
  '''
  Tests test_user_history 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  uuid = fake.uuid4()
  dataset_name = fake.name()
  data_faulty = {
    "uuid": uuid,
  }

  # 400 error
  response = requests.get(f'{LT_API_URL}/get_user_history', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  data_faulty = {
    "dataset_name": dataset_name,
  }

  # 400 error
  response = requests.get(f'{LT_API_URL}/get_user_history', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_user_history_401():
  '''
  Tests get_user_history 401 error
  Error: Unauthorized Access!
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()

  # Add user actions
  # Create
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Test user_history
  data = {
    "username": username
  }
  response = requests.get(f'{LT_API_URL}/get_user_history', params=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_get_user_history_412():
  '''
  Tests get_user_history 412 error
  Error: Preconditions not fulfilled!
  This error occurs if user does not exist
  '''
  # Create fake data
  username = fake.name()

  # Test No user_history
  data = {
    "username": username
  }
  response = requests.get(f'{LT_API_URL}/get_user_history', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "User history cannot be shown, because the specified user does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################## GET_DATASET_HISTORY ###############################

def test_get_dataset_history_200():
  '''
  Tests get_dataset_history success
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_next = fake.uuid4()
  dataset_name = fake.name()

  # Add dataset actions
  # Create
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)   # We need time.sleep(1) because the results are ordered by timestamp
  # Read
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)
  # Update
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_next,
    "uuid_prev": uuid,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)
  # Delete
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid,
  }
  response = requests.post(f'{LT_API_URL}/delete_family_tree', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)
  
  # Test dataset_history for uuid_prev
  data = {
    "uuid": uuid
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  assert len(response_json[uuid]) == 4
  # Create
  response_create = response_json[uuid][0]
  del response_create['timestamp']
  assert response_create == {
    "username": username,
    "user_group": user_group,
    "operation_description": "create",
  }
  # Read
  response_read = response_json[uuid][1]
  del response_read['timestamp']
  assert response_read == {
    "username": username,
    "user_group": user_group,
    "operation_description": "read"
  }
  response_read = response_json[uuid][2]
  del response_read['timestamp']
  assert response_read == {
    "username": username,
    "user_group": user_group,
    "operation_description": "update",
    "update_description": "add_rows",
    "to_uuid": uuid_next
  }
  # Delete
  response_delete = response_json[uuid][3]
  del response_delete['timestamp']
  assert response_delete == {
    "username": username,
    "user_group": user_group,
    "operation_description": "delete"
  }

  # Test dataset_history for uuid
  data = {
    "uuid": uuid_next
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  assert len(response_json[uuid_next]) == 2
  # Update
  response_update = response_json[uuid_next][0]
  del response_update['timestamp']
  assert response_update == {
    "username": username,
    "user_group": user_group,
    "operation_description": "update",
    "update_description": "add_rows",
    "from_uuid": uuid
  }
  # Delete
  response_delete = response_json[uuid_next][1]
  del response_delete['timestamp']
  assert response_delete == {
    "username": username,
    "user_group": user_group,
    "operation_description": "delete"
  }



def test_get_dataset_history_400():
  '''
  Tests get_dataset_history 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  dataset_name = fake.name()

  # 400 error
  data_faulty = {
    "username": username,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "dataset_name": dataset_name,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_dataset_history_401():
  '''
  Tests get_dataset_history 401 error
  Error: Unauthorized Access!
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid = fake.uuid4()
  uuid_prev = fake.uuid4()
  dataset_name = fake.name()

  # Add dataset actions
  # Create
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_prev,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  # Test dataset_history for uuid_prev
  data = {
    "uuid": uuid_prev
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_get_dataset_history_412():
  '''
  Tests get_dataset_history 412 error
  Error: Preconditions not fulfilled!
  This error occurs if user does not exist
  '''
  # Create fake data
  uuid = fake.uuid4()

  # Test No dataset_history
  data = {
    "uuid": uuid
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_history', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset history cannot be shown, because the specified dataset does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################## GET_DATASET_LINEAGE ###############################

def test_get_dataset_lineage_200():
  '''
  Tests get_dataset_lineage success
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1, uuid_v2, uuid_v3 = fake.uuid4(), fake.uuid4(), fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v2,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset again
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v3,
    "uuid_prev": uuid_v2,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test get_dataset_lineage
  data = {
    "uuid": uuid_v1
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_lineage', params=data, headers=headers)
  assert response.status_code == 200

  response_data = loads(response.text)
  assert len(response_data) == 3
  
  del response_data[uuid_v1]['timestamp']
  assert response_data[uuid_v1] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": None,
    "operation_description": "create"
  }
  del response_data[uuid_v2]['timestamp']
  assert response_data[uuid_v2] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": uuid_v1,
    "operation_description": "update",
    "update_description": "add_rows"
  }
  del response_data[uuid_v3]['timestamp']
  assert response_data[uuid_v3] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": uuid_v2,
    "operation_description": "update",
    "update_description": "add_rows"
  }

def test_get_dataset_lineage_400():
  '''
  Tests get_dataset_lineage 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  dataset_name = fake.name()

  # 400 error
  data_faulty = {
    "username": username,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_lineage', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "dataset_name": dataset_name,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_lineage', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_dataset_lineage_412():
  '''
  Tests get_dataset_lineage 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset does not exist
  '''
  # Create fake data
  uuid = fake.uuid4()

  # Test No dataset_lineage
  data = {
    "uuid": uuid
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_lineage', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "The specified lineage ID does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################### GET_DATASET_STATUS ###############################

def test_get_dataset_status_200():
  '''
  Tests get_dataset_status success
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1, uuid_v2, uuid_v3 = fake.uuid4(), fake.uuid4(), fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test status
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data, headers=headers)
  assert response.status_code == 200
  response_status = loads(response.text)[uuid_v1]
  del response_status['timestamp']
  assert response_status == {
    "username": username,
    "user_group": user_group,
    "operation_description": "create",
  }

  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v2,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test status
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data, headers=headers)
  assert response.status_code == 200
  response_status = loads(response.text)[uuid_v2]
  del response_status['timestamp']
  assert response_status == {
    "username": username,
    "user_group": user_group,
    "operation_description": "update",
    "from_uuid": uuid_v1,
    "update_description": update_description
  }

  # Update dataset again
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v3,
    "uuid_prev": uuid_v2,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test status
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data, headers=headers)
  assert response.status_code == 200
  response_status = loads(response.text)[uuid_v3]
  del response_status['timestamp']
  assert response_status == {
    "username": username,
    "user_group": user_group,
    "operation_description": "update",
    "from_uuid": uuid_v2,
    "update_description": update_description
  }

def test_get_dataset_status_400():
  '''
  Tests get_dataset_status 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  dataset_name = fake.name()

  # 400 error
  data_faulty = {
    "username": username,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "dataset_name": dataset_name,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_dataset_status_401():
  '''
  Tests get_dataset_status 401 error
  Error: Unauthorized Access!
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1 = fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test status
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data)

  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_get_dataset_status_412():
  '''
  Tests get_dataset_status 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset does not exist
  '''
  # Create fake data
  uuid = fake.uuid4()

  # Test No dataset_lineage
  data = {
    "uuid": uuid
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset status cannot be shown, because the specified dataset does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

########################### GET_DATASET_NUM_OPERATIONS ###########################

def test_get_dataset_num_operations_200():
  '''
  Tests get_dataset_num_operations success
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1, uuid_v2, uuid_v3 = fake.uuid4(), fake.uuid4(), fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test status
  data = {
    "uuid": uuid_v1,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_num_operations', params=data, headers=headers)
  assert response.status_code == 200
  response_num_operations = loads(response.text)[uuid_v1]
  assert response_num_operations == {
    "create": 1,
    "read": 0,
    "update": 0,
    "delete": 0
  }

  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v2,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test dataset_num_operations
  data = {
    "uuid": uuid_v2,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_num_operations', params=data, headers=headers)
  assert response.status_code == 200
  response_num_operations = loads(response.text)[uuid_v2]
  assert response_num_operations == {
    "create": 0,
    "read": 0,
    "update": 1,
    "delete": 0
  }

  # Read dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Delete datasets
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v2,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 200
  
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
  }
  response = requests.post(f'{LT_API_URL}/delete_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test dataset_num_operations
  data = {
    "uuid": uuid_v1,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_num_operations', params=data, headers=headers)
  assert response.status_code == 200
  response_num_operations = loads(response.text)[uuid_v1]
  assert response_num_operations == {
    "create": 1,
    "read": 1,
    "update": 1,
    "delete": 1
  }

def test_get_dataset_num_operations_400():
  '''
  Tests get_dataset_num_operations 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  dataset_name = fake.name()

  # 400 error
  data_faulty = {
    "username": username,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_num_operations', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "dataset_name": dataset_name,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_num_operations', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_dataset_num_operations_401():
  '''
  Tests get_dataset_num_operations 401 error
  Error: Unauthorized Access!
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1 = fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test status
  response = requests.get(f'{LT_API_URL}/get_dataset_status', params=data)

  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_get_dataset_num_operations_412():
  '''
  Tests get_dataset_num_operations 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset does not exist
  '''
  # Create fake data
  uuid = fake.uuid4()

  # Test No dataset_lineage
  data = {
    "uuid": uuid
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_num_operations', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset's number of operations cannot be shown, because the specified dataset does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

############################### GET_DATASET_FAMILY_TREE ###############################

def test_get_dataset_family_tree_200():
  '''
  Tests get_dataset_family_tree success
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1, uuid_v2, uuid_v3, uuid_v4 = fake.uuid4(), fake.uuid4(), fake.uuid4(), fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)

  # Update dataset
  update_description = "add_rows"
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v2,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)

  # Update dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v3,
    "uuid_prev": uuid_v2,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)

  # Update dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v4,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200
  time.sleep(1)

  # Test get_family_tree
  response = requests.get(f'{LT_API_URL}/get_dataset_family_tree', params=data, headers=headers)
  assert response.status_code == 200
  response_status = loads(response.text)
  keys = list(response_status.keys())

  # Determine which is first and second branch from response
  first_branch = None
  second_branch = None
  if len(response_status[keys[0]]) == 1:
    first_branch = response_status[keys[1]]
    second_branch = response_status[keys[0]]
  else:
    first_branch = response_status[keys[0]]
    second_branch = response_status[keys[1]]

  # Order each branch by version
  first_branch = dict(sorted(first_branch.items(), key=lambda item: item[1]['version']))
  second_branch = dict(sorted(second_branch.items(), key=lambda item: item[1]['version']))

  # Test first branch
  assert len(first_branch) == 3
  del first_branch[uuid_v1]["timestamp"]
  assert first_branch[uuid_v1] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": None,
    "operation_description": "create",
    "version": "1",
  }
  del first_branch[uuid_v2]["timestamp"]
  assert first_branch[uuid_v2] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": uuid_v1,
    "operation_description": "update",
    "update_description": "add_rows",
    "version": "2.0",
  }
  del first_branch[uuid_v3]["timestamp"]
  assert first_branch[uuid_v3] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": uuid_v2,
    "operation_description": "update",
    "update_description": "add_rows",
    "version": "3.0",
  }

  # Test second branch
  assert len(second_branch) == 1
  del second_branch[uuid_v4]["timestamp"]
  assert second_branch[uuid_v4] == {
    "username": username,
    "user_group": user_group,
    "dataset_name": dataset_name,
    "derived_from": uuid_v1,
    "operation_description": "update",
    "update_description": "add_rows",
    "version": "2.1",
  }

def test_get_dataset_family_tree_400():
  '''
  Tests get_dataset_family_tree 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  username = fake.name()
  user_group = fake.name()
  dataset_name = fake.name()

  # 400 error
  data_faulty = {
    "username": username,
    "user_group": user_group,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_family_tree', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "dataset_name": dataset_name,
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_family_tree', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_dataset_family_tree_401():
  '''
  Tests get_dataset_family_tree 401 error
  '''
  # Create fake data
  username = fake.name()
  user_group = fake.name()
  uuid_v1, uuid_v2, uuid_v3, uuid_v4 = fake.uuid4(), fake.uuid4(), fake.uuid4(), fake.uuid4()
  dataset_name = fake.name()

  # Create dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v1,
    "dataset_name": dataset_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  update_description = 'add_rows'
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v2,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v3,
    "uuid_prev": uuid_v2,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Update dataset
  data = {
    "username": username,
    "user_group": user_group,
    "uuid": uuid_v4,
    "uuid_prev": uuid_v1,
    "update_description": update_description
  }
  response = requests.post(f'{LT_API_URL}/update_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Test get_dataset_family_tree
  response = requests.get(f'{LT_API_URL}/get_dataset_family_tree', params=data)
  assert response.status_code == 401
  assert loads(response.text) == {
    "message": "API Key or token is missing, authentication failed.",
    "origin": "Lineage Tracker Backend",
    "status_code": 401
  }

def test_get_dataset_family_tree_412():
  '''
  Tests get_dataset_family_tree 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset does not exist
  '''
  # Create fake data
  uuid = fake.uuid4()

  # Test No dataset_lineage
  data = {
    "uuid": uuid
  }
  response = requests.get(f'{LT_API_URL}/get_dataset_family_tree', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Dataset family tree cannot be shown, because the specified dataset does not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

##################################### GET_DATASETS_DIFF #######################################

def test_get_datasets_diff_200():
  '''
  Tests get_datasets_diff success
  '''
  # Create fake data
  dataset_1_name = fake.name()
  dataset_1 = {
    "metadata": {
      "name": dataset_1_name
    },
    "data_model": {
      "columns": [
        {
          "name": "entry_id",
          "dataType": "Integer"
        },
        {
          "name": "age",
          "dataType": "Integer"
        },
        {
          "name": "name",
          "dataType": "String"
        },
        {
          "name": "sex",
          "dataType": "String"
        },
        {
          "name": "hiring_date",
          "dataType": "Date"
        }
      ]
    },
    "data": {
      "rows": [
        [
          1,
          43,
          "Bob",
          "m",
          "Thu, 22 May 2008 00:00:00 GMT"
        ]
      ]
    }
  }
  dataset_1_data_model_output = [['entry_id', 'integer'], ['age', 'integer'], ['name', 'text'], ['sex', 'text'], ['hiring_date', 'date']]

  dataset_2_name = fake.name()
  dataset_2 = {
    "metadata": {
      "name": dataset_2_name
    },
    "data_model": {
      "columns": [
        {
          "name": "entry_id",
          "dataType": "Integer"
        },
        {
          "name": "age",
          "dataType": "Integer"
        },
        {
          "name": "name",
          "dataType": "String"
        },
        {
          "name": "sex",
          "dataType": "String"
        },
        {
          "name": "hiring_date",
          "dataType": "Date"
        }
      ]
    },
    "data": {
      "rows": [
        [
          1,
          44,
          "Alice",
          "m",
          "Thu, 22 May 2008 00:00:00 GMT"
        ]
      ]
    }
  }
  dataset_2_data_model_output = [['entry_id', 'integer'], ['age', 'integer'], ['name', 'text'], ['sex', 'text'], ['hiring_date', 'date']]

  # Create dataset 1
  response = requests.post(f'{FDS_API_URL}/api/tables/create_table', json=dataset_1, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  dataset_1_uuid = response_json['asset_uuid']
  
  # Add to local lineage tracker
  username_1 = fake.name()
  user_group = fake.name()
  data = {
    "username": username_1,
    "user_group": user_group,
    "uuid": dataset_1_uuid,
    "dataset_name": dataset_1_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Read dataset 1
  data = {
    "username": username_1,
    "user_group": user_group,
    "uuid": dataset_1_uuid
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Create dataset 2
  response = requests.post(f'{FDS_API_URL}/api/tables/create_table', json=dataset_2, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  dataset_2_uuid = response_json['asset_uuid']

  # Add to local lineage tracker
  username_2 = fake.name()
  data = {
    "username": username_2,
    "user_group": user_group,
    "uuid": dataset_2_uuid,
    "dataset_name": dataset_2_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Now get datasets diff
  data = {
    "uuid_1": dataset_1_uuid,
    "uuid_2": dataset_2_uuid
  }
  response = requests.get(f'{LT_API_URL}/get_datasets_diff', params=data, headers=headers)
  response_data = loads(response.text)

  assert response.status_code == 200
  assert response_data['dataset_1'][0]['data'] == dataset_1['data']
  assert response_data['dataset_1'][0]['data_model']['columns'] == dataset_1_data_model_output
  assert response_data['dataset_2'][0]['data'] == dataset_2['data']
  assert response_data['dataset_2'][0]['data_model']['columns'] == dataset_2_data_model_output

  diff = {
    'added': [], 
    'changed': [
      {
        'changes': {'age': ['43', '44'], 'name': ['Bob', 'Alice']}, 
        'key': '1'
      }
    ], 
    'columns_added': [], 
    'columns_removed': [], 
    'removed': []
  }
  assert response_data['diff'] == diff

  response = {
    'dataset_1': {
      "metadata": {
        "name": dataset_1_name
      },
      "data_model": {
        "columns": [
          {
            "name": "entry_id",
            "dataType": "Integer"
          },
          {
            "name": "age",
            "dataType": "Integer"
          },
          {
            "name": "name",
            "dataType": "String"
          },
          {
            "name": "sex",
            "dataType": "String"
          },
          {
            "name": "hiring_date",
            "dataType": "Date"
          }
        ]
      },
      "data": {
        "rows": [
          [
            1,
            43,
            "Bob",
            "m",
            "Thu, 22 May 2008 00:00:00 GMT"
          ]
        ]
      }
    },
    'dataset_2': {
      "metadata": {
        "name": dataset_2_name
      },
      "data_model": {
        "columns": [
          {
            "name": "entry_id",
            "dataType": "Integer"
          },
          {
            "name": "age",
            "dataType": "Integer"
          },
          {
            "name": "name",
            "dataType": "String"
          },
          {
            "name": "sex",
            "dataType": "String"
          },
          {
            "name": "hiring_date",
            "dataType": "Date"
          }
        ]
      },
      "data": {
        "rows": [
          [
            1,
            44,
            "Alice",
            "m",
            "Thu, 22 May 2008 00:00:00 GMT"
          ]
        ]
      }
    },
    'diff': {
      'added': [], 
      'changed': [
        {
          'changes': {'column_2': ['43', '44'], 'column_3': ['Bob', 'Alice']}, 
          'key': '1'
        }
      ], 
      'columns_added': [], 
      'columns_removed': [], 
      'removed': []
    }
  }

def test_get_datasets_diff_400():
  '''
  Tests get_datasets_diff 400 error
  Error: The shape of the provided arguments is faulty!
  '''
  # Setup fake data
  uuid = fake.uuid4()

  # 400 error
  data_faulty = {
    "uuid1": uuid,
  }
  response = requests.get(f'{LT_API_URL}/get_datasets_diff', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

  # 400 error
  data_faulty = {
    "uuid2": uuid,
  }
  response = requests.get(f'{LT_API_URL}/get_datasets_diff', params=data_faulty, headers=headers)
  assert response.status_code == 400
  assert loads(response.text) == {
    "message": "The shape of the provided arguments is faulty!",
    "origin": "Lineage Tracker Backend",
    "status_code": 400
  }

def test_get_datasets_diff_401():
  '''
  Tests get_datasets_diff success
  '''
  # Create fake data
  dataset_1_name = fake.name()
  dataset_1 = {
    "metadata": {
      "name": dataset_1_name
    },
    "data_model": {
      "columns": [
        {
          "name": "entry_id",
          "dataType": "Integer"
        },
        {
          "name": "age",
          "dataType": "Integer"
        },
        {
          "name": "name",
          "dataType": "String"
        },
        {
          "name": "sex",
          "dataType": "String"
        },
        {
          "name": "hiring_date",
          "dataType": "Date"
        }
      ]
    },
    "data": {
      "rows": [
        [
          1,
          43,
          "Bob",
          "m",
          "Thu, 22 May 2008 00:00:00 GMT"
        ]
      ]
    }
  }

  dataset_2_name = fake.name()
  dataset_2 = {
    "metadata": {
      "name": dataset_2_name
    },
    "data_model": {
      "columns": [
        {
          "name": "entry_id",
          "dataType": "Integer"
        },
        {
          "name": "age",
          "dataType": "Integer"
        },
        {
          "name": "name",
          "dataType": "String"
        },
        {
          "name": "sex",
          "dataType": "String"
        },
        {
          "name": "hiring_date",
          "dataType": "Date"
        }
      ]
    },
    "data": {
      "rows": [
        [
          1,
          44,
          "Alice",
          "m",
          "Thu, 22 May 2008 00:00:00 GMT"
        ]
      ]
    }
  }

  # Create dataset 1
  response = requests.post(f'{FDS_API_URL}/api/tables/create_table', json=dataset_1, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  dataset_1_uuid = response_json['asset_uuid']
  
  # Add to local lineage tracker
  username_1 = fake.name()
  user_group = fake.name()
  data = {
    "username": username_1,
    "user_group": user_group,
    "uuid": dataset_1_uuid,
    "dataset_name": dataset_1_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Read dataset 1
  data = {
    "username": username_1,
    "user_group": user_group,
    "uuid": dataset_1_uuid
  }
  response = requests.post(f'{LT_API_URL}/read_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Create dataset 2
  response = requests.post(f'{FDS_API_URL}/api/tables/create_table', json=dataset_2, headers=headers)
  assert response.status_code == 200
  response_json = loads(response.text)
  dataset_2_uuid = response_json['asset_uuid']

  # Add to local lineage tracker
  username_2 = fake.name()
  data = {
    "username": username_2,
    "user_group": user_group,
    "uuid": dataset_2_uuid,
    "dataset_name": dataset_2_name
  }
  response = requests.post(f'{LT_API_URL}/create_dataset', json=data, headers=headers)
  assert response.status_code == 200

  # Now get datasets diff
  data = {
    "uuid_1": dataset_1_uuid,
    "uuid_2": dataset_2_uuid
  }
  response = requests.get(f'{LT_API_URL}/get_datasets_diff', params=data)
  assert response.status_code == 401

def test_get_datasets_diff_412():
  '''
  Tests get_datasets_diff 412 error
  Error: Preconditions not fulfilled!
  This error occurs if dataset does not exist
  '''
  # Create fake data
  uuid_1 = fake.uuid4()
  uuid_2 = fake.uuid4()

  # Test No dataset_lineage
  data = {
    "uuid_1": uuid_1,
    "uuid_2": uuid_2
  }
  response = requests.get(f'{LT_API_URL}/get_datasets_diff', params=data, headers=headers)
  assert response.status_code == 412
  assert loads(response.text) == {
    "message": "Datasets' diff cannot be shown, because the specified datasets do not exist.",
    "origin": "Lineage Tracker Backend",
    "status_code": 412
  }

