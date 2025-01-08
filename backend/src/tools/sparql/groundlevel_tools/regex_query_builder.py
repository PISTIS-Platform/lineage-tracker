import re


def re_get_namespaces_rdf_query(namespaces_rdf:list) -> str:
    pattern = r'<Namespace: (\w+) \{(.*)\}'
    namespaces_rdf_query = '\n'.join([re.sub(pattern, r'PREFIX \1: <\2', str(namespace)) for namespace in list(namespaces_rdf)])
    namespaces_rdf_query += '\nPREFIX prov:<http://www.w3.org/ns/prov#>\n\n'
    return namespaces_rdf_query




def re_convert_insert(match:re.Match) -> str:
    if match.group(5) is None:
        return 'PREFIX' + ''.join(list(match.groups())[2:4])
    else:
        return 'PREFIX' + ''.join(list(match.groups())[2:4]) + '''
        INSERT DATA
        {
        GRAPH <pistisGraph:v3> 
        ''' + match.group(5) +'\n}'