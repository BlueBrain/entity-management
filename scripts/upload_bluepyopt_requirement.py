#!/usr/bin/env python
import requests
import os

from entity_management.simulation import Configuration, Distribution, SubCellularModelScript, SubCellularModel, IonChannelMechanismRelease

def upload_recipe():
    node_name = "Thalamus recipe"
    if not next(Configuration.find_by(name=node_name), None):
        print("Publishing: recipes.json")
        conf = Configuration(node_name,
                             distribution=[
                                 Distribution(downloadURL=
                                              "file:///gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/config/recipes/recipes.json")
                             ])
        conf.publish(use_auth=os.getenv("NEXUS_TOKEN"))


def upload_protocols():
    path = "/gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/config/protocols/"
    for name in filter(lambda name: name.lower().endswith(".json"),
                       os.listdir(path)):

        node_name = "Thalamus protocol: {}".format(name)
        if not next(Configuration.find_by(name=node_name), None):
            print("Publishing: {}".format(name))
            conf = Configuration(node_name,
                                 distribution=[
                                     Distribution(downloadURL= os.path.join("file://"+path, name))
                                 ])
            conf.publish(use_auth=os.getenv("NEXUS_TOKEN"))

def upload_params():
    path = "/gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/config/params/"
    for name in filter(lambda name: name.lower().endswith(".json"),
                       os.listdir(path)):

        node_name = "Thalamus params: {}".format(name)
        if not next(Configuration.find_by(name=node_name), None):
            print("Publishing: {}".format(node_name))
            conf = Configuration(node_name,
                                 distribution=[
                                     Distribution(downloadURL= os.path.join("file://"+path, name))
                                 ])
            conf.publish(use_auth=os.getenv("NEXUS_TOKEN"))

def upload_sub_cellular_model_scripts():
    release_name = "Thalamus release"
    release = next(IonChannelMechanismRelease.find_by(name=release_name), None)
    if not release:
        release = IonChannelMechanismRelease(name=release_name).publish(use_auth=os.getenv('NEXUS_TOKEN'))

    path = os.path.join(os.path.dirname(__file__), 'mechanisms')
    for name in filter(lambda name: name.lower().endswith(".mod"),
                       os.listdir(path)):
        node_name = name
        print("name: {}".format(name))

        if not next(SubCellularModel.find_by(name=node_name), None):

            script = next(SubCellularModelScript.find_by(name=node_name), None)
            if not script:
                script = SubCellularModelScript(node_name,
                                                distribution=[
                                                    Distribution(downloadURL=os.path.join("file://"+path, name))
                                              ]).publish()
            inst = SubCellularModel(name=node_name,
                             modelScript=script,
                             isPartOf=release)
            inst.publish()

def delete_recipe():
    try:
        next(Configuration.find_by(name="Thalamus recipe")).deprecate()
    except StopIteration:
        pass

def delete_params():
    for node in filter(lambda node: node.name.startswith("Thalamus params"),
                       Configuration.find_by()):
        node.deprecate()

def delete_protocols():
    for node in filter(lambda node: node.name.startswith("Thalamus protocol"),
                       Configuration.find_by()):
        node.deprecate()

def delete_sub_cellular_model_scripts():
    for node in SubCellularModelScript.find_by():
        node.deprecate()

if __name__=='__main__':
    # delete_protocols()
    # delete_params()
    # delete_recipe()
    # delete_sub_cellular_model_scripts()

    # upload_protocols()
    # upload_params()
    # upload_recipe()
    # upload_sub_cellular_model_scripts()
