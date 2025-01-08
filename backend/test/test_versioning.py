import pytest
from src.versioning import add_versioning

sample_ft = {
  "32463890-4f0f-43b9-a697-86ced79c166d": {
    "1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": None,
      "operation_description": "create",
      "timestamp": "2024-09-05 13:23:30"
    },
    "2": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "1",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:23:55"
    },
    "3.0": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "2",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:24:17"
    },
    "4.0": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "3.0",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:27:17"
    },
    "5.0.0": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "4.0",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:24:55"
    },
    "6.0.0": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "5.0.0",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:25:10"
    }
  },
  "25178878-39c1-428f-a31b-d7cf723cc66f": {
    "5.0.2": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "4.0",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:26:19"
    },
    "6.0.2": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "5.0.2",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:26:36"
    }
  },
  "3b79d3e3-2455-4e98-a36a-cad468b6e660": {
    "5.0.1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "4.0",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:25:34"
    },
    "6.0.1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "5.0.1",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:25:52"
    }
  },
  "66420a35-17a5-49e3-a557-452629e3d48d": {
    "3.1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "2",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:27:17"
    },
    "4.1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "3.1",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:27:00"
    }
  },
  "4687cfdd-d03a-4c14-a8a9-6c294ad096ff": {
    "3.2": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "2",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:27:56"
    },
    "4.2.0": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "3.2",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:28:07"
    },
    "5.2.0": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "4.2.0",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:28:29"
    }
  },
  "7d0bf9c0-13ef-4545-8996-8e0fd54c61a7": {
    "4.2.1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "3.2",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:28:45"
    },
    "5.2.1": {
      "username": "user1",
      "user_group": "group1",
      "dataset_name": "random_name",
      "derived_from": "4.2.1",
      "operation_description": "update",
      "timestamp": "2024-09-05 13:29:01"
    }
  }
}

def test_versioning():
    '''
    Tests dataset versioning function, which adds versioning
    '''
    ft_input = sample_ft

    ft = add_versioning(ft_input)

    for lineage_id in ft:
        for dataset_id in ft[lineage_id]:
            this_dataset = ft[lineage_id][dataset_id]
            assert dataset_id == this_dataset['version']

