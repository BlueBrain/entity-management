#!/usr/bin/env python
import requests
import os

from entity_management.simulation import Configuration, Distribution, SubCellularModelScript, SubCellularModel, IonChannelMechanismRelease

def upload_recipe(recipe):
    node_name = "Thalamus recipe"
    if not next(Configuration.find_by(name=node_name), None):
        print("Publishing: recipes.json")
        conf = Configuration(node_name,
                             distribution=[
                                 Distribution(downloadURL="file://"+recipe)
                             ])
        conf.publish(use_auth=os.getenv("NEXUS_TOKEN"))


def upload_protocols(protocol_folder):
    for name in filter(lambda name: name.lower().endswith(".json"),
                       os.listdir(protocol_folder)):
        node_name = "Thalamus protocol: {}".format(name)
        if not next(Configuration.find_by(name=node_name), None):
            print("Publishing: {}".format(name))
            conf = Configuration(node_name,
                                 distribution=[
                                     Distribution(downloadURL= os.path.join("file://"+protocol_folder, name))
                                 ])
            conf.publish(use_auth=os.getenv("NEXUS_TOKEN"))

def upload_params(params_folder):
    for name in filter(lambda name: name.lower().endswith(".json"),
                       os.listdir(params_folder)):
        node_name = "Thalamus params: {}".format(name)
        if not next(Configuration.find_by(name=node_name), None):
            print("Publishing: {}".format(node_name))
            conf = Configuration(node_name,
                                 distribution=[
                                     Distribution(downloadURL= os.path.join("file://"+params_folder, name))
                                 ])
            conf.publish(use_auth=os.getenv("NEXUS_TOKEN"))

def upload_sub_cellular_model_scripts(mechanism_folder):
    release_name = "Thalamus release"
    release = IonChannelMechanismRelease.find_unique(
        name=release_name,
        on_no_result=lambda: IonChannelMechanismRelease(name=release_name).publish(use_auth=os.getenv('NEXUS_TOKEN'))
        )

    for name in filter(lambda name: name.lower().endswith(".mod"),
                       os.listdir(mechanism_folder)):
        node_name = name
        print("name: {}".format(name))

        if not next(SubCellularModel.find_by(name=node_name), None):

            script = next(SubCellularModelScript.find_by(name=node_name), None)
            if not script:
                script = SubCellularModelScript(node_name,
                                                distribution=[
                                                    Distribution(downloadURL=os.path.join("file://"+mechanism_folder, name))
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

    # upload_protocols("/gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/config/protocols/")
    # upload_params("/gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/config/params/")
    # upload_recipe("/gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/config/recipes/recipes.json")
    upload_sub_cellular_model_scripts('/gpfs/bbp.cscs.ch/project/proj55/singlecell/optimization-mouse_TH/mechanisms/')
