import oyaml as yaml # make sure order in yaml file is preserved
import objects
from container import Container

class ProjectFactory:
    def __init__(self, project):
        file = open(project, 'r')
        self.document = yaml.load(file)
        file.close()
        
    def create_project(self):
        doc = self.document
        doc, root_container = self.__create_root_container(doc)
        return root_container
    
    def __create_root_container(self, doc):
        top_level_keys = list(doc.keys())
        if len(top_level_keys) > 1:
            raise Exception("YAML file invalid, multiple project names")
        if len(top_level_keys) < 1:
            raise Exception("YAML file invalid, no project name given")
        return doc.values(), Container(top_level_keys[0])
    
    def __create_object(self):
        pass
        