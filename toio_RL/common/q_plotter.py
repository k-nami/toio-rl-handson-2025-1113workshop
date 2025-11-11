from itertools import product

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Rectangle


def conv2state(env, agent_xy: tuple) -> int:
    """Compute linear state index from agent and target positions."""
    ax, ay = agent_xy
    tx, ty = env._target_pos
    idx_agent = ay * env.grid_width + ax
    idx_target = ty * env.grid_width + tx
    return idx_agent * (env.grid_width * env.grid_height) + idx_target


def framing_cells(env):
    return [
        (env._agent_pos, "blue"),
        (env._target_pos, "red"),
    ]


class QPlotter:
    """
    Visualize Q-values for a grid world environment.
    Splits each cell into 4 triangles corresponding to actions:
    0: UP, 1: RIGHT, 2: DOWN, 3: LEFT.
    """

    def __init__(
        self,
        env,
        conv2state: callable = conv2state,
        framing_cells: callable = framing_cells,
    ):
        """
        env: environment with attributes:
            - grid_width (int)
            - grid_height (int)
            - action_space.n == 4
        """
        self.env = env
        self.width = env.grid_width
        self.height = env.grid_height
        self.num_actions = env.action_space.n
        if self.num_actions != 4:
            raise ValueError("QPlotter supports exactly 4 actions")

        self.colorbar = None
        self.conv2state = conv2state
        self.framing_cells = framing_cells
        self.fig = None

    def plot_q(
        self,
        Q: np.ndarray,
        cmap: str = "RdYlGn_r",
        vmin: float = None,
        vmax: float = None,
    ):
        """
        Q: array of shape (num_states, 4)
        cmap: matplotlib colormap name
        vmin, vmax: color scale limits
        """
        plt.ion()
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(self.width, self.height))
            self.fig.show()
        norm = Normalize(
            vmin=(Q.min() if vmin is None else vmin),
            vmax=(Q.max() if vmax is None else vmax),
        )
        mapper = ScalarMappable(norm=norm, cmap=cmap)

        self.ax.clear()
        patches, colors = [], []

        # build triangles and color values
        for x, y in product(range(self.width), range(self.height)):
            cx, cy = x + 0.5, y + 0.5
            for action, tri in {
                0: [(x, y), (x + 1, y), (cx, cy)],  # UP
                1: [(x + 1, y + 1), (x, y + 1), (cx, cy)],  # DOWN
                2: [(x, y + 1), (x, y), (cx, cy)],  # LEFT
                3: [(x + 1, y), (x + 1, y + 1), (cx, cy)],  # RIGHT
            }.items():
                patches.append(Polygon(tri, closed=True))
                obs = self.conv2state(self.env, (x, y))
                q_val = Q[obs, action]
                colors.append(mapper.to_rgba(q_val))
                cx = sum(pt[0] for pt in tri) / 3
                cy = sum(pt[1] for pt in tri) / 3
                self.ax.text(
                    cx,
                    cy,
                    f"{q_val:.2f}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=8,
                )

        collection = PatchCollection(patches, facecolors=colors, edgecolors="black")
        self.ax.add_collection(collection)

        # draw agent and target rectangles
        for pos, color in self.framing_cells(self.env):
            rect = Rectangle(
                pos, width=1, height=1, fill=False, edgecolor=color, linewidth=10
            )
            self.ax.add_patch(rect)

        # format axes
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_xticks(np.arange(self.width + 1))
        self.ax.set_yticks(np.arange(self.height + 1))
        self.ax.grid(True)
        self.ax.invert_yaxis()
        self.ax.set_title("Q-function Visualization")

        # update or create colorbar
        if self.colorbar is None:
            self.colorbar = self.fig.colorbar(
                mapper, ax=self.ax, fraction=0.046, pad=0.04, label="Q value"
            )
        else:
            self.colorbar.update_normal(mapper)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)
