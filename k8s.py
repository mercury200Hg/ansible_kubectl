from kubernetes import client, config
from typing import Dict, Any, List, NoReturn
from pathlib import Path
import logging
import sys
import os

# Gets or create a logger
logger = logging.getLogger(__name__)
# Set log level
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)


class Messages:
    NO_WORKER_NODES_FOUND = "No worker nodes exists for the given kube config"
    KUBE_CONFIG_NOT_FOUND = "Kube config not found!"


class Nodes:
    class Node:
        """
            --- Custom node class restricting only variables that are required for current functionality ---
        """

        def __init__(self, name: str, ip: str, labels: List[Dict[str, str]]):
            self.node_name = name
            self.node_ip = ip
            self.node_labels = labels

    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    def group_by_labels(self) -> List[str]:
        """
        Groups the inventory by labels
        :return: List of nodes having IP as their value
        :rtype: List[str]
        """
        pass

    def group_by_name(self) -> List[str]:
        """
        Groups the inventory by node name
        :return: List of nodes having IP as their value
        :rtype: List[str]
        """
        pass

    def group_by_ip(self) -> List[str]:
        """
        Groups the inventory by ip
        :return: List of nodes having IP as their value
        :rtype: List[str]
        """
        pass


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

    def _parse_all_nodes_info(self) -> Nodes:
        """
        Parses all nodes information from kubeconfig
        :return: List of all nodes in desired it's class object form
        :rtype: Nodes
        """
        result = []
        if self.v1 is None:
            self.v1 = client.CoreV1Api()
        ret = self.v1.list_node(pretty=True)
        if ret is None:
            raise Exception(Messages.NO_WORKER_NODES_FOUND)

        return result


def merge_groups():
    pass
