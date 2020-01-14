from networkx.drawing.nx_agraph import graphviz_layout

from byn_auto.general_index import GeneralIndex
from byn_auto.symbol_node import SymbolNode
import networkx as nx
import matplotlib.pyplot as plt


class Graph:

    @staticmethod
    def __generate_symbol_subsets(symbol_sequence):

        result = []
        for i in range(len(symbol_sequence)):
            result.append(tuple(symbol_sequence[i:]))

        return tuple(result)

    def __init__(self):

        self.__node_id_index = GeneralIndex()
        self.__subgraph_index = GeneralIndex()
        self.__root_node = SymbolNode()

        key = self.__root_node.get_node_id()
        self.__node_id_index.add_node(key, self.__root_node)

        self.__context_node = None
        self.context_reset()

    def add_sequence(self, symbol_sequence):

        symbol_subsets = Graph.__generate_symbol_subsets(symbol_sequence)
        self.context_reset()
        for i in range(len(symbol_subsets)):
            subset_word = symbol_subsets[i]
            symbol = subset_word[0]
            if not self.__context_get_node().link_to_child_exists(symbol):
                if i == (len(symbol_subsets) - 1):
                    # The node connected by the last element is always a terminal
                    node = SymbolNode(SymbolNode.NodeNature.TERMINAL)
                else:
                    node = SymbolNode()
                self.__context_node.add_child_node(symbol, node, subset_word)
                self.__node_id_index.add_node(node.get_node_id(), node)
                self.context_go_to_node_id(node.get_node_id())
            else:
                node = self.__context_get_child_node(symbol)
                self.__context_node.add_child_node(symbol, node, subset_word)
                # self.context_go_to_child_node(symbol)
                self.context_go_to_node_id(node.get_node_id())
                if i == (len(symbol_subsets) - 1):
                    self.__context_mark_node_as_terminal()

        self.context_reset()

    def __prepare_subgraph_index(self):
        subgraph_index = self.__subgraph_index

        all_symbol_nodes = self.__node_id_index.get_all_nodes()

        # each construction instance will require us to refresh the
        # subgraph structure index
        subgraph_index.clear()

        for symbol_node in all_symbol_nodes:
            subgraph_index.add_node(symbol_node.get_subgraph_words_tuple(), symbol_node)

    def __collapse_graph(self):
        """
        Reconnects redundant subgraphs by retaining exactly one
        subgraph with a particular structure and discarding
        the rest from the `__child_nodes` link within the
        respective nodes.

        NOTE: This method must only be called after
        __prepare_subgraph_index is called
        :return:
        """
        subgraph_index = self.__subgraph_index
        node_tuples_grouped_by_key = subgraph_index.get_all_node_tuples_grouped_by_key()

        for node_tuple in node_tuples_grouped_by_key:
            base_node = node_tuple[0]
            for i in range(1, len(node_tuple)):
                base_node.steal_parent_links(node_tuple[i])

    def __breath_first_search(self, operation):
        root_node = self.__get_root_node()
        node_set = set()
        visited_nodes = set()
        node_set.add(root_node)

        while len(node_set) != 0:
            new_set = set()

            for node in node_set:

                if node in visited_nodes:
                    continue  # ignore already visited nodes

                operation(node)
                visited_nodes.add(node)
                new_set.update(node.get_all_child_nodes())

            node_set.clear()
            node_set.update(new_set)

    def __prune_unreachable_nodes(self):

        unreachable_nodes = set(self.__node_id_index.get_all_nodes())

        def remove_reachable_node(cur_node):
            unreachable_nodes.remove(cur_node)

        self.__breath_first_search(remove_reachable_node)

        for node in unreachable_nodes:
            self.__node_id_index.remove_node(node)

    def simplify_graph(self):
        self.__prepare_subgraph_index()
        self.__collapse_graph()
        self.__prune_unreachable_nodes()

        # cleanup
        self.__subgraph_index.clear()

    def display_graph(self):

        def display(node):
            print(node)

        self.__breath_first_search(display)

    def __get_all_edge_and_edgelabels(self):
        edges = []
        edge_labels = {}
        terminal_nodes = []

        def accumulate(node: SymbolNode):
            temp_edges, temp_edge_labels, node_nature = node.get_edges_and_labels()
            edges.extend(temp_edges)
            edge_labels.update(temp_edge_labels)
            if node.get_node_nature() is SymbolNode.NodeNature.TERMINAL:
                terminal_nodes.append(str(node.get_node_id()))

        self.__breath_first_search(accumulate)

        return edges, edge_labels, terminal_nodes

    def plot_graph(self, edge_color='black', node_color='pink', font_color='red'):
        edges, edge_labels, terminal_nodes = self.__get_all_edge_and_edgelabels()
        G = nx.DiGraph()
        for i in range(1, len(edges) + 1):
            G.add_edges_from([edges[i - 1]], weight=1)
        # G.add_edges_from(edges)
        # pos = nx.spring_layout(G, k=0.5, iterations=50)
        pos = graphviz_layout(G, prog='dot')

        val_map = {edges[0][0]: 0.25}

        for node_id in terminal_nodes:
            val_map[node_id] = 0.0

        # val_map = {nodes[0]: 1.0,
        #            nodes[int(len(nodes) / 2)]: 0.5714285714285714,
        #            nodes[len(nodes) - 1]: 0.0}

        values = [val_map.get(node, 1.0) for node in G.nodes()]
        plt.figure()
        nx.draw(G, pos, edge_color=edge_color, width=1, linewidths=1,
                node_size=500, node_color=values, alpha=0.9,
                labels={node: node for node in G.nodes()})
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color=font_color)
        plt.axis('off')

    def __get_root_node(self):
        return self.__root_node

    def get_root_node_id(self):
        return self.__root_node.get_node_id()

    def context_get_node_id(self):
        return self.__context_node.get_node_id()

    def __context_get_node(self) -> SymbolNode:
        return self.__context_node

    def __context_get_child_node(self, symbol):
        return self.__context_get_node().get_child_node(symbol)

    def __context_mark_node_as_terminal(self):
        self.__context_get_node().mark_node_terminal()

    def __context_mark_node_as_non_terminal(self):
        self.__context_get_node().mark_node_non_terminal()

    def context_get_node_nature(self):
        return self.__context_get_node().get_node_nature()

    def context_reset(self):
        self.__context_node = self.__get_root_node()

    def context_go_to_node_id(self, node_id):
        res = self.__node_id_index.get_node_tuple(node_id)  # get_node returns a tuple

        if res is not None:
            # only the field 0 is of interest because the key uniquely associates
            # with just one node. Thus, `get_node_tuple` returns a tuple with just
            # one node
            self.__context_node = res[0]
            return True

        return False

    def context_go_to_child_node(self, symbol):
        res = self.__context_get_node().get_child_node(symbol)
        if res is not None:
            self.__context_node = res
            return True
        return False

    def context_get_all_next_node_id(self):
        return self.__context_node.get_all_child_node_id()

    def context_get_all_prev_node_id(self):
        return self.__context_node.get_all_parent_node_id()
