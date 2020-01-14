import enum
from sortedcontainers import SortedList


class SymbolNode:
    __node_id = 0

    @staticmethod
    def __get_node_id():
        SymbolNode.__node_id += 1
        return SymbolNode.__node_id

    class NodeNature(enum.Enum):
        NON_TERMINAL = 0
        TERMINAL = 1

    def __init__(self, node_nature=None):

        self.__node_id = SymbolNode.__get_node_id()

        # These are always sorted
        # self.__sub_graph_word_left = []
        self.__subgraph_word = SortedList()

        self.__child_nodes = {}  # stores the associations {symbol -> node}
        self.__reverse_index_child_nodes = {}  # stores the associations {node -> set of symbols}

        self.__parent_nodes = set()  # stores the parent nodes

        if node_nature is None:
            self.__node_nature = SymbolNode.NodeNature.NON_TERMINAL
        else:
            self.__node_nature = node_nature

    def __str__(self):

        result = []
        result.append(self.__node_id)
        for node, symbol_set in self.__reverse_index_child_nodes.items():
            result.append(
                ((self.__node_id, node.get_node_id()), symbol_set)
            )
        result.append("Terminal" if self.__node_nature is SymbolNode.NodeNature.TERMINAL else "Non-Terminal")
        # return str({"node id:": self.__node_id,
        #             " child nodes:": [node.get_all_child_node_id() for node in self.__reverse_index_child_nodes]})

        return str(result)

    def get_edges_and_labels(self):
        edges = []
        edge_labels = {}
        for node, symbol_set in self.__reverse_index_child_nodes.items():
            cur_node_id = str(self.__node_id)
            conn_node_id = str(node.get_node_id())
            edges.append((cur_node_id, conn_node_id))
            edge_labels[(cur_node_id, conn_node_id)] = str(symbol_set)

        return edges, edge_labels, self.get_node_nature()

    def get_node_nature(self):
        return self.__node_nature

    def mark_node_terminal(self):
        self.__node_nature = SymbolNode.NodeNature.TERMINAL

    def mark_node_non_terminal(self):
        self.__node_nature = SymbolNode.NodeNature.NON_TERMINAL

    def __hash__(self):
        return hash(self.__node_id)

    def get_node_id(self):
        return self.__node_id

    def __add_child_node_low(self, symbol, node):
        self.__child_nodes[symbol] = node
        if node not in self.__reverse_index_child_nodes:
            self.__reverse_index_child_nodes[node] = set()
        self.__reverse_index_child_nodes[node].add(symbol)
        node.__parent_nodes.add(self)

    def add_child_node(self, symbol, node, subset_word_right):
        """
        Forcefully adds child node, even if a different node was already present,
        by replacing the previous node
        :param symbol:
        :param node:
        :param subset_word_right:
        :return:
        """
        if symbol not in self.__child_nodes:
            self.__add_child_node_low(symbol, node)

        # self.__sub_graph_word_left.append(tuple(sub_graph_word_left))
        # self.__sub_graph_word_left.sort()
        subset_word_right = tuple(subset_word_right)

        if subset_word_right not in self.__subgraph_word:
            self.__subgraph_word.add(tuple(subset_word_right))

        # sorting ensures that each subgraph with the same structure
        # will have the same value (when hashed)
        # self.__subgraph_word.sort()

    def __reset_parents_low(self):
        self.__parent_nodes = set()

    def __remove_parent_node_connection(self, parent_node):
        if parent_node in self.__parent_nodes:
            self.__parent_nodes.remove(parent_node)

    def __remove_child_node_connection(self, child_node):
        if child_node in self.__reverse_index_child_nodes:
            symbol_set = self.__reverse_index_child_nodes[child_node]
            for symbol in symbol_set:
                del self.__child_nodes[symbol]
            del self.__reverse_index_child_nodes[child_node]

    def __disconnect_from_parent_node(self, parent_node):
        self.__remove_parent_node_connection(parent_node)
        parent_node.__remove_child_node_connection(self)

    def __disconnect_from_child_node(self, child_node):
        child_node.__remove_parent_node_connection(self)
        self.__remove_child_node_connection(child_node)

    def __get_parent_node_key_tuple(self, parent_node):
        if parent_node in self.__parent_nodes:
            return tuple(parent_node.__reverse_index_child_nodes[self])

    def steal_parent_links(self, node):
        parent_nodes = tuple(node.__parent_nodes)
        for parent_node in parent_nodes:
            symbol_tuple = node.__get_parent_node_key_tuple(parent_node)
            node.__disconnect_from_parent_node(parent_node)
            for symbol in symbol_tuple:
                parent_node.__add_child_node_low(symbol, self)

    def get_subgraph_words_tuple(self):
        return tuple(self.__subgraph_word)

    def link_to_child_exists(self, symbol):
        return symbol in self.__child_nodes

    def get_child_node(self, symbol):
        if self.link_to_child_exists(symbol):
            return self.__child_nodes[symbol]

    def get_all_child_node_symbols(self):
        return list(self.__child_nodes.keys())

    def get_all_child_node_id(self):

        result = []

        for node in self.__child_nodes.values():
            result.append(node.get_node_id())

        return result

    def get_all_child_nodes(self):
        """
        unused- to be deleted
        :return:
        """
        return list(self.__child_nodes.values())

    def get_all_parent_node_id(self):
        result = []

        for node in self.__parent_nodes:
            result.append(node.get_node_id())

        return result

    def get_all_parent_nodes(self):
        """
        unused- to be deleted
        :return:
        """
        return tuple(self.__parent_nodes)
