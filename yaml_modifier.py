#!/usr/bin/python
from __future__ import print_function

import yaml

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

def represent_odict(dump, tag, mapping, flow_style=None):
    """Like BaseRepresenter.represent_mapping, but does not issue the sort().
    """
    value = []
    node = yaml.MappingNode(tag, value, flow_style=flow_style)
    if dump.alias_key is not None:
        dump.represented_objects[dump.alias_key] = node
    best_style = True
    if hasattr(mapping, 'items'):
        mapping = mapping.items()
    for item_key, item_value in mapping:
        node_key = dump.represent_data(item_key)
        node_value = dump.represent_data(item_value)
        if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
            best_style = False
        if not (isinstance(node_value, yaml.ScalarNode) and not node_key.style):
            best_style = False
        value.append((node_key, node_value))
    if flow_style is None:
        if dump.default_flow_style is not None:
            node.flow_style = dump.default_flow_style
        else:
            node.flow_style = best_style
    return node

yaml.SafeDumper.add_representer(OrderedDict,
    lambda dumper, value: represent_odict(dumper, u'tag:yaml.org,2002:map', value))

def construct_tuple(loader, node):
    return tuple(yaml.SafeLoader.construct_sequence(loader, node))
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:seq', construct_tuple)

def construct_yaml_map(loader, node):
    data = OrderedDict()
    yield data
    value = construct_mapping(loader, node)
    data.update(value)

def construct_mapping(loader, node, deep=False):
    if isinstance(node, yaml.MappingNode):
        loader.flatten_mapping(node)
    else:
        raise yaml.constructor.ConstructorError(None, None,
            'expected a mapping node, but found %s' % node.id, node.start_mark)

    mapping = OrderedDict()
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as exc:
            raise yaml.constructor.ConstructorError('while constructing a mapping', node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
        value = loader.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping

yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:map', construct_yaml_map)
#yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:omap', construct_yaml_map)

if __name__ == '__main__':
    import textwrap

    sample = """
    one:
        two: fish
        red: fish
        blue: fish
    two:
        a: yes
        b: no
        c: null
    """

    data = yaml.safe_load(textwrap.dedent(sample))

    assert type(data) is OrderedDict
    print(data)
    print("---")
    print(yaml.safe_dump(data, default_flow_style=False))
