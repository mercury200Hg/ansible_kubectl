import configparser
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, NoReturn

from kubernetes import client, config

# Gets or create a logger
logger = logging.getLogger(__name__)
# Set log level
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)


class Messages:
    NO_WORKER_NODES_FOUND = "No worker nodes exists for the given kube config"
    KUBE_CONFIG_NOT_FOUND = "Kube config not found!"


class Node:
    """
        --- Custom node class restricting only variables that are required for current functionality ---
    """

    def __init__(self, name: str, ip: str, labels: List[Dict[str, Any]], annotations: List[Dict[str, Any]]):
        self.node_name = name
        self.node_ip = ip
        self.node_labels = labels
        self.node_annotations = annotations


class Grouping:

    def __init__(self, worker_nodes: List[Node]):
        self.worker_nodes = worker_nodes

    def group_by_labels(self) -> Dict[str, List[str]]:
        """
        Groups the inventory by labels
        :return: Dict of list of nodes having IP as their value
        :rtype: dict
        """
        result = {}
        return result

    def group_by_annotations(self) -> Dict[str, List[str]]:
        """
        Groups the inventory by annotations
        :return: Dict of list of nodes having IP as their value
        :rtype: dict
        """
        result = {}
        return result

    def group_by_name(self) -> Dict[str, List[str]]:
        """
        Groups the inventory by node name
        :return: Dict of list of nodes having IP as their value
        :rtype: dict
        """
        result = {}
        return result

    def group_by_ip(self) -> Dict[str, List[str]]:
        """
        Groups the inventory by ip
        :return: Dict of List of nodes having IP as their value
        :rtype: dict
        """
        result = {}
        return result

    def group_all(self) -> Dict[str, List[str]]:
        """
        Groups the inventory by nothing and returns single group with IP's of all nodes
        :return: dict
        """
        result = {}
        return result

    @staticmethod
    def create_inventory(groups: List[Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        Merge all groups and provide final inventory file
        :param groups: List of all the groups individually created and to be merged as per the ini file
        :return: dict
        """
        result = {}
        return result


class K8sUtils:

    def __init__(self):
        self.v1 = None

    def _init_kube_config(self) -> NoReturn:
        """
        Assumes kubeconfig is present in the path $HOME/.kube/config
        """
        if not os.path.exists(f"{str(Path.home())}/.kube"):
            logger.info(Messages.KUBE_CONFIG_NOT_FOUND)
        config.load_kube_config()

    def parse_all_nodes_info(self) -> List[Node]:
        """
        Parses all nodes information from kubeconfig
        :return: List of all nodes in desired it's class object form
        :rtype: List[Node]
        """
        result = []
        if self.v1 is None:
            self._init_kube_config()
            self.v1 = client.CoreV1Api()
        ret = self.v1.list_node(pretty=True)
        if ret is None:
            raise Exception(Messages.NO_WORKER_NODES_FOUND)
        for item in ret.items:
            node_name = item.metadata.name
            node_annotations = item.metadata.annotations
            node_labels = item.metadata.labels
            addresses = item.status.addresses
            node_ip_set = [add.address if add.type == 'InternalIP' else None for add in addresses]
            node_ip_set.remove(None)
            node_ip = node_ip_set[0]
            result.append(Node(name=node_name, ip=node_ip, labels=node_labels, annotations=node_annotations))
        return result


if __name__ == '__main__':
    config_parser = configparser.ConfigParser()
    config_parser.read("k8s.ini")
    # Get Default Config
    default_config = config_parser[config_parser.default_section]

    # Parse all nodes info
    nodes = K8sUtils().parse_all_nodes_info()
    # Create grouping object
    grouping_obj = Grouping(worker_nodes=nodes)

    groups_to_merge = [grouping_obj.group_all()]

    if default_config.getboolean("GROUP_BY_NAME"):
        groups_to_merge.append(grouping_obj.group_by_name())
    if default_config.getboolean("GROUP_BY_LABELS"):
        groups_to_merge.append(grouping_obj.group_by_labels())
    if default_config.getboolean("GROUP_BY_ANNOTATIONS"):
        groups_to_merge.append(grouping_obj.group_by_annotations())
    if default_config.getboolean("GROUP_BY_IP"):
        groups_to_merge.append(grouping_obj.group_by_ip())

    inventory = Grouping.create_inventory(groups_to_merge)
    print(json.dumps(inventory, indent=4, sort_keys=True))
