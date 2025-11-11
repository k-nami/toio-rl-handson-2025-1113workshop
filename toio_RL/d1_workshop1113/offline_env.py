from typing import Optional, Tuple, Dict, Any, List
from enum import IntEnum

import numpy as np
from gymnasium.spaces import Discrete
from gymnasium.utils import seeding

from toio_RL.common.keyboard_input import read_action, Key


class Action(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class OfflineEnv:
    """
    Offline environment for collecting a target on a grid.
    """

    def __init__(
        self,
        grid_width: int = 7,
        grid_height: int = 5,
        life_range: Tuple[int, int] = (1, 6),
        render_mode: Optional[str] = "ansi",
        goal_reward: float = 1.0,
    ) -> None:
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.n_cells = grid_width * grid_height
        self.observation_space = Discrete(self.n_cells * self.n_cells)
        self.action_space = Discrete(len(Action))

        self.life_range = life_range

        self._agent_pos: Tuple[int, int] = (0, 0)
        self._target_pos: Tuple[int, int] = (0, 0)
        self._target_life: int = 0
        self._step_count: int = 0
        self._rng: Optional[np.random.Generator] = None
        self.render_mode = render_mode

        self.goal_reward = goal_reward

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict]:
        """
        Returns: observation, info dict
        """
        self._rng, _ = seeding.np_random(seed)
        self._step_count = 0
        self._agent_pos = (
            self._rng.integers(0, self.grid_width),
            self._rng.integers(0, self.grid_height),
        )
        self._respawn_target()
        observation = self.get_observation()
        return observation, {}

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict]:
        """
        Returns: observation, reward, terminated, truncated, info dict
        """
        self._step_count += 1
        self._target_life -= 1

        dx, dy = {
            Action.UP: (0, -1),
            Action.DOWN: (0, 1),
            Action.LEFT: (-1, 0),
            Action.RIGHT: (1, 0),
        }[Action(action)]

        new_x = self._agent_pos[0] + dx
        new_y = self._agent_pos[1] + dy

        if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
            self._agent_pos = (new_x, new_y)

        reward = self.get_reward()

        if self._target_life <= 0 or self._agent_pos == self._target_pos:
            self._respawn_target()

        observation = self.get_observation()
        return observation, reward, False, False, {}

    def get_observation(self) -> int:
        return self.pos_to_index(self._agent_pos) * self.n_cells + self.pos_to_index(
            self._target_pos
        )

    def get_reward(self) -> float:
        return self.goal_reward if self._agent_pos == self._target_pos else 0.0

    # ----- utility methods -----

    def render(self) -> Optional[str]:
        """
        Render grid to console as string.
        """
        if self.render_mode != "ansi":
            return None
        grid = [["." for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        ax, ay = self._agent_pos
        tx, ty = self._target_pos
        grid[ay][ax] = "T"
        grid[ty][tx] = "A" if grid[ty][tx] != "T" else "TA"
        output = "\n".join(" ".join(row) for row in grid)
        print(
            f"{output}\nAgent: ({ax},{ay})  Target: ({tx},{ty})  Life: {self._target_life}"
        )
        return output

    def close(self) -> None:
        pass

    def pos_to_index(self, xy: Tuple[int, int]) -> int:
        # 座標(x,y)から状態indexへの変換
        return xy[1] * self.grid_width + xy[0]

    def index_to_pos(self, idx: int) -> Tuple[int, int]:
        # 状態indexから座標(x,y)への変換
        return idx % self.grid_width, idx // self.grid_width

    # ----- private methods -----

    def _respawn_target(self) -> None:
        """Randomly place the target on a free cell and reset its lifetime."""
        free = [
            self.pos_to_index((x, y))
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in (self._agent_pos, self._target_pos)
        ]
        assert self._rng is not None
        choice = self._rng.choice(free)
        self._target_pos = self.index_to_pos(choice)
        self._target_life = int(
            self._rng.integers(self.life_range[0], self.life_range[1])
        )


def test_with_keyboard() -> None:
    print(
        "矢印キーでエージェントの行動を指定（↑, ↓, ←, →）。終了は 'q' または Ctrl+C。"
    )
    mapping = {
        Key.UP.value: Action.UP,
        Key.RIGHT.value: Action.RIGHT,
        Key.DOWN.value: Action.DOWN,
        Key.LEFT.value: Action.LEFT,
    }
    env = OfflineEnv()
    obs, _ = env.reset()
    print(f"Initial Observation: {obs}")
    env.render()
    for i in range(1, 1001):
        action = read_action(mapping)
        if action is None:
            break
        obs, reward, *_ = env.step(action)
        print(f"Step: {i} Obs: {obs} Rwd: {reward}")
        env.render()
    env.close()


if __name__ == "__main__":
    test_with_keyboard()
