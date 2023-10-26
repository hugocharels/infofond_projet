import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

########################################
#                UTILS                 #
########################################
LAMBDA = 10
DEFAULT_LAYOUT = nx.kamada_kawai_layout
LAYOUTS = {
    'spring': nx.spring_layout,
    'kk': nx.kamada_kawai_layout,
    'kamada-kawai': nx.kamada_kawai_layout,
    'planar': nx.planar_layout,
    'plane': nx.planar_layout,
    'default': DEFAULT_LAYOUT,
}

def rotate_vector(v: np.ndarray, angle: float) -> np.ndarray:
    c = np.cos(angle)
    s = np.sin(angle)
    M = np.array([[c, -s], [s, c]])
    return M @ v

def fa2graph(fa) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_nodes_from(fa.states)
    edges = dict()
    for q in fa.states:
        for qprime in fa.states:
            transitions = []
            for s in fa.input_symbols:
                delta = fa.transitions[q].get(s, ())
                if not isinstance(delta, (set, frozenset)):
                    delta = {delta}
                if qprime in delta:
                    transitions.append(s if s != '' else 'ε')
            transitions = ','.join(sorted(transitions))
            if transitions:
                G.add_edge(q, qprime, label=transitions)
    return G

def _draw_edge(pos: dict, u: int, v: int, label: str, ax) -> None:
    A = pos[u]
    B = pos[v]
    C = (A+B) / 2
    r = rotate_vector(B-A, np.pi/2)
    r /= np.hypot(*r)
    ell = np.hypot(*(B-A))
    h = ell / (2 * np.tan(np.pi / LAMBDA))
    O = C + r * h
    radius = A-O
    R = np.hypot(*radius)
    phi = np.arccos((A[0]-O[0]) / R)
    if not np.allclose(O[1] + R*np.sin(phi), A[1]):
        phi = -phi
    t = np.linspace(0, 1, 101)
    xs = O[0] + R * np.cos(2*np.pi / LAMBDA * t + phi)
    ys = O[1] + R * np.sin(2*np.pi / LAMBDA * t + phi)
    xy = np.vstack([xs, ys]).T
    mid = t.size // 2
    M = xy[mid]
    ax.plot(xs, ys, 'k', zorder=0)
    ax.annotate('', xytext=xy[-10], xy=xy[-9],
        arrowprops={'arrowstyle': '-|>', 'color': 'k', 'mutation_scale': 15},
    )
    ax.annotate('', xytext=xy[9], xy=xy[10],
        arrowprops={'arrowstyle': '-|>', 'color': 'k', 'mutation_scale': 15},
    )
    ax.annotate(label, xytext=M, xy=M, size=12,
        bbox={'fc': 'white', 'ec': 'white'}, ha='center', va='center'
    )

def _draw_loop(pos: dict, v: int, label: str, ax) -> None:
    A = pos[v]
    t = np.linspace(0.05, .95, 101)
    O = A - np.asarray((.2, 0))
    xs = O[0] + .2*np.cos(2*np.pi*t)
    ys = O[1] + .1*np.sin(2*np.pi*t)
    xy = np.vstack([xs, ys]).T
    mid = t.size // 2
    M = xy[mid]
    ax.plot(xs, ys, ':', c='grey')
    ax.annotate('', xytext=xy[-10], xy=xy[-9],
        arrowprops={'arrowstyle': '-|>', 'color': 'grey', 'mutation_scale': 15}
    )
    ax.annotate('', xytext=xy[9], xy=xy[10],
        arrowprops={'arrowstyle': '-|>', 'color': 'grey', 'mutation_scale': 15}
    )
    ax.annotate(label, xytext=M, xy=M, size=12,
        bbox={'fc': 'white', 'ec': 'white'}, ha='center', va='center', color='grey'
    )

def _draw_edges(G: nx.DiGraph, pos: dict) -> None:
    ax = plt.gca()
    ax.axis('equal')
    for i, (u, v, prop) in enumerate(G.edges.data()):
        label = prop['label']
        if u == v:
            _draw_loop(pos, v, label, ax)
        else:
            _draw_edge(pos, u, v, label, ax)

def show_automaton(fa, layout: str='spring'):
    if layout not in LAYOUTS:
        print(f'Unknown layout {layout}, defaulting to "spring"')
        layout = DEFAULT_LAYOUT
    else:
        layout = LAYOUTS[layout]
    G = fa2graph(fa)
    pos = layout(G)
    nx.draw_networkx_nodes(G, pos=pos, nodelist=list(fa.final_states), node_size=450, edgecolors='black')
    nx.draw_networkx_nodes(G, pos=pos, node_size=250, edgecolors='black')
    nx.draw_networkx_labels(G, pos=pos)
    _draw_edges(G, pos)
    plt.gcf().tight_layout()
    plt.show()

if os.name.lower() == 'nt':
    os.system('color')

WHITE = '\033[0m'
RED   = '\033[31m'
GREEN = '\033[32m'
BLUE  = '\033[34m'

def _colour(text, colour):
    return f'{colour}{text}{WHITE}'

def red(text):
    return _colour(text, RED)

def green(text):
    return _colour(text, GREEN)

def blue(text):
    return _colour(text, BLUE)

