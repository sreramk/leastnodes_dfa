class GeneralIndex:
    def __init__(self):
        self.__KeyToNode = {}
        self.__NodeToKey = {}

    def clear(self):
        self.__KeyToNode = {}
        self.__NodeToKey = {}

    def add_node(self, key, node):
        """
        Adds node associated with a key. This method ensures that a key already
        associated with a node does not get replaced. But the same key can
        connect with multiple nodes.

        But duplicates of the same node cannot exist under a specific key
        :param key:
        :param node:
        :return:
        """
        if node not in self.__NodeToKey:
            if key not in self.__KeyToNode:
                temp = set()
                temp.add(node)
                self.__KeyToNode[key] = temp
            else:
                self.__KeyToNode[key].add(node)

            self.__NodeToKey[node] = key
            return True

        return False

    def node_exists(self, node):
        return node in self.__NodeToKey

    def remove_key(self, key):
        if key in self.__KeyToNode:
            node_set = self.__KeyToNode[key]
            for node in node_set:
                del self.__NodeToKey[node]
            del self.__KeyToNode[key]

    def remove_node(self, node):
        if node in self.__NodeToKey:
            key = self.__NodeToKey[node]
            del self.__NodeToKey[node]
            self.__KeyToNode[key].remove(node)

    def get_node_tuple(self, key):
        """
        A single key can be associated with many nodes
        :param key:
        :return:
        """
        if key in self.__KeyToNode:
            return tuple(self.__KeyToNode[key])

    def get_all_nodes(self):
        result = set()
        for node_set in self.__KeyToNode.values():
            result.update(node_set)
        return tuple(result)

    def get_all_node_tuples_grouped_by_key(self):
        """
        Retrieves all the nodes, as tuples of nodes grouped by
        their key.
        :return:
        """
        result = []
        for node_set in self.__KeyToNode.values():
            result.append(tuple(node_set))
        return result

    def key_exists(self, key):
        return key in self.__KeyToNode

    def get_key(self, node):
        """
        A single node will be associated with just one key
        :param node:
        :return:
        """
        if node in self.__NodeToKey:
            return self.__NodeToKey[node]

    def get_all_keys(self):
        return tuple(self.__KeyToNode.values())