from byn_auto.binary_automata import Graph
import matplotlib.pyplot as plt


if __name__ == "__main__":
    gc = Graph()
    gc.add_sequence([1, 0, 1, 1, 0, 1, 1])
    gc.add_sequence([1, 0, 1, 1, 0, 1, 0])
    gc.add_sequence([0, 0, 1, 1, 0, 1, 0])
    gc.add_sequence([0, 0, 1, 1, 0, 1, 1])
    gc.add_sequence([0, 0, 1, 1, 0, 1, 1])
    gc.add_sequence([1, 0, 0, 0, 0, 1, 1])

    print(" Before simplification: \n")
    gc.display_graph()
    gc.plot_graph()

    gc.simplify_graph()
    gc.simplify_graph()

    print(" \n After Simplification: \n ")

    gc.display_graph()
    gc.plot_graph()
    plt.show()