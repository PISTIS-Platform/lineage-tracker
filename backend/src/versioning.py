'''
The purpose of versioning.py is to add version labels to the get_family_tree api endpoint.
The dataset uuid's and connection between datasets are stored, but not the version labels.
The Jupyter notebook FamilyTree.ipynb explains this process in detail.
'''

from json import dumps, loads
from datetime import datetime
from collections import OrderedDict

class FamilyTree:
    '''
    Family Tree class that contains a dictionary representation of the family tree of datasets
    '''
    def __init__(self):
        self.nodes = {}
        self.root = None

    def add_dataset(self, dataset):
        '''
        Adds dataset to nodes dictionary, story by its dataset_id
        '''
        dataset_id = getattr(dataset, 'dataset_id')
        if getattr(dataset, 'dataset_id') not in self.nodes:
            self.nodes[dataset_id] = dataset

    def update_versioning(self):
        '''
        Adds version numbers to nodes
        Uses BFS to iterate through all nodes and add correct version numbers to each node
        '''
        # Start with root, which is named 1.0
        root = getattr(self, 'root')
        setattr(root, 'version', '1')
        
        # BFS children, add versions
        q = [root]
        while len(q) > 0:
            # Get/remove first element in q
            parent = q[0]
            parent_version = getattr(parent, 'version')
            q = q[1:]    
        
            # Add all children to q
            # NOTE: Make sure children are sorted by timestamp
            this_dataset_children_unsorted = getattr(parent, 'children')
            this_dataset_children = sorted(this_dataset_children_unsorted, key=lambda obj: datetime.strptime(obj.timestamp, '%Y-%m-%d %H:%M:%S'))
            num_children = len(this_dataset_children)
            for child in this_dataset_children:
                q.append(child)
        
            # Name versions accordingly, depending on number of children
            if num_children == 1:
                child = this_dataset_children[0]
                child_version = str((int(parent_version[0:1]) + 1)) + parent_version[1:]
                setattr(this_dataset_children[0], 'version', child_version)
            elif num_children > 1:
                for i, child in enumerate(this_dataset_children):
                    child_version = str((int(parent_version[0:1]) + 1)) + parent_version[1:] + '.' + str(i)
                    setattr(this_dataset_children[i], 'version', child_version)

    def get_version(self, dataset_id):
        '''
        Given the dataset_id, returns the version of that dataset
        '''
        version = getattr(self.nodes[dataset_id], 'version')
        return version
    
    def display_tree(self, dataset=None, level=0):
        '''
        Displays family tree
        '''
        if dataset is None:
            dataset = self.root
        if dataset is not None:
            print(' ' * 4 * level + '->', dataset)
            for child in dataset.children:
                self.display_tree(child, level + 1)

    def add_root(self, dataset):
        '''
        Notes a dataset as the root of the family tree
        A dataset is the root if it has no parents
        '''
        self.root = dataset

class Dataset:
    '''
    Dataset class that contains all dataset info and relationships to parent and children datasets
    Note that version is initialized with None, but later updated
    '''
    def __init__(self, dataset_id, username, user_group, dataset_name, derived_from, operation_description, timestamp):
        # Dataset attributes
        self.dataset_id = dataset_id
        self.username = username
        self.user_group = user_group
        self.dataset_name = dataset_name
        self.derived_from = derived_from
        self.operation_description = operation_description
        self.timestamp = timestamp
        self.version = None
        # Tree attributes
        self.parents = []
        self.children = []

    def add_parent(self, parent):
        '''
        Adds parent to parents list
        Adds this dataset to parents' childrens list
        '''
        if parent not in self.parents:
            self.parents.append(parent)
        if self not in parent.children:
            parent.children.append(self)

    def add_child(self, child):
        '''
        Adds child to children list
        Adds this dataset to child's parents list
        '''
        if child not in self.children:
            self.children.append(child)
        if self not in child.parents:
            child.parents.append(self)

    def __repr__(self):
        return f"{self.dataset_id}: Version {self.version}"

def create_family_tree(ft):
    '''
    Function that creates a FamilyTree object from json
    Input: FamilyTree json object
    Output: FamilyTree object containing Dataset objects for each dataset
    '''
    # Iterate through all datasets in ft, create Dataset class for each
    ft_obj = FamilyTree()
    
    # Create Dataset for each dataset, add to ft_dict
    for lineage_id in ft:
        this_lineage = ft[lineage_id]
        for this_dataset_id in this_lineage:
            this_dataset = this_lineage[this_dataset_id]
            
            this_dataset = Dataset(
                this_dataset_id, 
                this_dataset['username'], 
                this_dataset['user_group'], 
                this_dataset['dataset_name'], 
                this_dataset['derived_from'], 
                this_dataset['operation_description'], 
                this_dataset['timestamp']
            )
    
            ft_obj.add_dataset(this_dataset)
    
    # Add relationships between each Dataset in ft_dict
    ft_nodes = getattr(ft_obj, 'nodes')
    for dataset_id, dataset in getattr(ft_obj, 'nodes').items():
        derived_from = getattr(dataset, 'derived_from')
        if derived_from is not None:
            dataset.add_parent(ft_nodes[dataset.derived_from])
        else:
            ft_obj.add_root(dataset)

    # Update versioning
    ft_obj.update_versioning()

    return ft_obj

def add_versioning(ft):
    '''
    Adds versioning to the family tree json
    Inputs: family tree json
    Output: family tree json with updated versioning
    '''
    ft_obj = create_family_tree(ft)
    ft_output = ft

    # Update version for each dataset
    for lineage_id in ft_output:
        this_lineage = ft_output[lineage_id]
        for this_dataset_id in this_lineage:
            this_version = ft_obj.get_version(this_dataset_id)    
            ft_output[lineage_id][this_dataset_id]['version'] = this_version

    return ft_output

