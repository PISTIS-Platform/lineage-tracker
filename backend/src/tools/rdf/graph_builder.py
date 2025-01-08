from dataclasses import dataclass, field
import prov.model as prov
import urllib
from datetime import datetime

namespaces = [
    {
        'namespace_or_prefix':'foaf', 
        'uri':'http://xmlns.com/foaf/0.1/'
    },
    {
        'namespace_or_prefix':'dct', 
        'uri':'http://purl.org/dc/terms/'
    },
    {
        'namespace_or_prefix':'dcat', 
        'uri':'http://www.w3.org/ns/dcat/#'
    },
    {
        'namespace_or_prefix':'adms', 
        'uri':'http://www.w3.org/TR/vocab-adms/'
    },
    {
        'namespace_or_prefix':'pistisDataset', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/dataset/#'
    },
    {
        'namespace_or_prefix':'pistisUser', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/user/#'
    },
        {
        'namespace_or_prefix':'pistisUserGroup', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/user-group/#'
    },
    {
        'namespace_or_prefix':'pistisGraph', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/graph/#'
    },
    {
        'namespace_or_prefix':'pistisOperation', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/operation/#'
    },
    {
        'namespace_or_prefix':'pistisDatasetLineage', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/lineage/#'
    },
    {
        'namespace_or_prefix':'pistisDatasetFamily', 
        'uri':'https://develop.pistis-market.eu/lineage-tracker/family/#'
    },
    {
        'namespace_or_prefix':'owl', 
        'uri':'https://www.w3.org/TR/owl-ref/#'
    },
]

@dataclass
class Dataset:
    '''
    Dataset dataclass referring to the dataset a user performs an operation on
    '''
    uuid: str
    name: str
    lineage_id: str
    family_id: str
    
    uri: str = field(init=False, default=None)
        
    def __post_init__(self):
        self.uri =  'pistisDataset:' + urllib.parse.quote('-'.join([self.name, self.uuid]))

@dataclass
class User:
    '''
    User dataclass referring to the user that performs operations on datasets
    '''
    name: str
    group: str
    uri: str = field(init=False)

    def __post_init__(self):
        self.uri = 'pistisUser:' + urllib.parse.quote('-'.join(
                            [
                                self.name, 
                                self.group
                            ]
                            )
                        )
        
@dataclass
class Operation:
    '''
    Operation dataclass that defines an operation that a user performs on a dataset
    '''
    type_: str
    involved_dataset: Dataset
    involved_user: User
    description: str = field(default=None)
    uri: str = field(init=False)
    timestamp: str = field(init=False, default=None)
        
    def __post_init__(self):
        self.timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        
        self.uri = 'pistisOperation:' + urllib.parse.quote('-'.join(
                            [
                                self.type_, self.description or "",
                                self.involved_dataset.uuid, 
                                self.involved_user.name, 
                                self.timestamp
                            ]
                            )
                        )

@dataclass(frozen=True)
class Document:
    '''
    Document dataclass that manages rdf graph, including:
        - rdf graph creation
        - converting user/dataset/operation objects to rdf classes and properties
        - adding these rdf classes/properties to the graph
    '''

    namespaces: list
    
    # Operation performed in relation to user, dataset, dataset_prev, and operation
    user: User = field(default=None)
    dataset: Dataset = field(default=None)
    operation: Operation = field(default=None)
    dataset_prev: Dataset = field(default=None)
    rdf_graph: prov.ProvDocument = field(init=False, default_factory=prov.ProvDocument)
    
    def __post_init__(self):
        '''
        Sets up rdf graph after initialization, which includes:
            1. graph creation
            2. creates graph classes (PROV-O agent/entity/activity which corresponsd to user/dataset/operation)
            3. creates graph properties between these classes (e.g., wasDerivedFrom, wasGeneratedBy, etc)
        '''
        # Add namespaces to rdf graph
        for namespace in self.namespaces:
            self.rdf_graph.add_namespace(**namespace)
        
        #conditional graph creation. If it fails an empty graph will be created
        if self.user is not None and self.dataset is not None and self.operation is not None:
            
            rdf_dataset = self.__add_rdf_dataset(self.dataset)
            rdf_operation = self.__add_rdf_operation(self.operation)
            rdf_user = self.__add_rdf_user(self.user)

            self.rdf_graph.used(rdf_operation, rdf_dataset)
            self.rdf_graph.wasAssociatedWith(rdf_operation, rdf_user)

            # Adds wasGeneratedBy, wasAttributed properties to rdf graph
            if self.operation.type_ != 'read':
                self.rdf_graph.wasGeneratedBy(rdf_dataset, rdf_operation)
                self.rdf_graph.wasAttributedTo(rdf_dataset, rdf_user)

            # Creates rdf_dataset_prev class
            # Adds wasDerivedFrom property to rdf graph
            if self.operation.type_ == 'update':
                rdf_dataset_prev = self.__add_rdf_dataset(self.dataset_prev)
                self.rdf_graph.wasDerivedFrom(rdf_dataset, rdf_dataset_prev)
            
    def __add_rdf_dataset(self, dataset:Dataset):
        '''
        Converts a Dataset object to an rdf Entity class
        '''
        rdf_dataset = self.rdf_graph.entity(
            dataset.uri, (
            ('dct:identifier', dataset.uuid),
            ('dct:title', dataset.name),
            ('pistisDatasetLineage:id', dataset.lineage_id),
            ('pistisDatasetFamily:id', dataset.family_id)
            ) 
        )
        return rdf_dataset
    
    def __add_rdf_operation(self, operation:Operation):
        '''
        Converts an Operation object to an rdf Activity class
        '''
        dct_description = operation.type_
        if dct_description == 'update':
            dct_description += (":" + operation.description)

        rdf_operation = self.rdf_graph.activity(
                        operation.uri, other_attributes={
                            'dct:description': dct_description,
                            'dct:issued': operation.timestamp
                            }
                        )
        return rdf_operation

    def __add_rdf_user(self, user:User):
        '''
        Converts a User object to an rdf Agent class
        '''
        rdf_user = self.rdf_graph.agent(
                        user.uri, (
                        (prov.PROV_TYPE, 'Person'),
                        ("foaf:nick", user.name),
                        ("pistisUserGroup:id", user.group)
                        )
                    )
        return rdf_user

    def get_serialized_rdf_graph(self):
        '''
        Serialize rdf graph, provided by prov module
        '''
        return self.rdf_graph.serialize(format='rdf')

    def get_rdf_namespaces(self):
        '''
        Returns list of rdf namespaces in rdf graph
        '''
        return list(self.rdf_graph.get_registered_namespaces())
