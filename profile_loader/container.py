import oyaml as yaml  # make sure order in yaml file is preserved


class Container(yaml.YAMLObject):
    yaml_tag = u'!Container'
    _counter = 0

    def __init__(self, url, children, name='Container'):
        super().__init__()
        self.id = str(type(self)._counter)
        type(self)._counter += 1
        self.name = name
        self.url = url
        self.children = children

    @classmethod
    def from_yaml(cls, loader, node):
        m = loader.construct_mapping(node)

        # rename some keys, so it fits into container
        def _get_list_key():
            for poss_key in ['floors', 'rooms', 'devices']:
                if poss_key in m:
                    return poss_key

        m['children'] = m.pop(_get_list_key())
        if 'project' in m:
            m['name'] = m['url'] = m.pop('project')

        return cls(**m)

    def __repr__(self):
        return '{ name: %s, url: %s, children: %s}' % (self.name, self.url, repr(self.children))


_path_containers = ['floors', None, 'rooms', None]


for i in range(0, len(_path_containers) + 1, 2):
    yaml.add_path_resolver(Container.yaml_tag, _path_containers[:i])
