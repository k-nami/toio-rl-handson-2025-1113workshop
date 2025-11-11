from typing import Optional
from pathlib import Path
import time

import matplotlib.pyplot as plt
import pandas as pd

from q_learning import QTableAgent
from offline_env import OfflineEnv
from toio_RL.common.q_plotter import QPlotter


def train(
    env,
    num_steps,
    agent,
    eval_env,
    eval_interval=10**3,
    eval_steps=100,
    log_q: Optional[Path] = None,
    plot_q: bool = True,
    plot_interval=10**2,
    plot_steps=20,
):
    start_timestamp = time.time()
    eval_rewards = []
    elapse_time = []
    steps = []

    state, _ = env.reset()
    if plot_q:
        q_plotter = QPlotter(eval_env)
        q_plotter.plot_q(Q=agent.Q)

    for step in range(1, num_steps + 1):
        action = agent.select_action(state)
        next_state, reward, _, _, _ = env.step(action)

        agent.update(state, action, reward, next_state, False)
        state = next_state

        if (step % eval_interval == 0) or (plot_q and step % plot_interval == 0):
            eval_reward_sum = 0
            _eval_step = 0
            eval_state, _ = eval_env.reset()
            while _eval_step < eval_steps:
                action = agent.greedy(eval_state)
                next_state, reward, _, _, _ = eval_env.step(action)
                eval_state = next_state
                eval_reward_sum += reward
                _eval_step += 1
                if plot_q and step % plot_interval == 0 and _eval_step < plot_steps:
                    q_plotter.plot_q(Q=agent.Q)
                    print(f"{step=}, {_eval_step=}")

            print(f"Evaluation: {step=}, {eval_reward_sum=}")
            eval_rewards.append(eval_reward_sum)
            elapse_time.append(time.time() - start_timestamp)
            steps.append(step)

    if log_q is not None:
        agent.save_q(log_q)
    return eval_rewards, elapse_time, steps


if __name__ == "__main__":
    """
    TODO オフラインで学習．様子を見せる（toio不要）

    準備
    1. パラメータを設定（要望があれば入力，なければ適当に）
    2. Qを可視化するか設定（DISPLAY_Q）

    実行
    3. コマンド'python demo2_train.py'

    デモ
    4. 学習中に4回，20stepの間だけQ値が表示される（toioの挙動が変わる）
    5. 最後に学習曲線が表示される（横軸は学習ステップ，縦軸は100stepの間に目標に到達した回数✕報酬に一致）
    """

    # パラメータ
    EPSILON = 0.1  # 探索率．0から1の実数（推奨0.1）
    NUM_STEPS = 10**5  # 学習ステップ数．0以上の整数（推奨10**6）
    GOAL_REWARD = 1.0  # 目標到達時の報酬．実数（推奨1.0）
    DISPLAY_Q = True  # Qの可視化有無
    Q_FILE_NAME = f"q_epsilon{str(EPSILON).replace('.', '_')}_step{str(NUM_STEPS)}_reward{str(GOAL_REWARD).replace('.', '_')}"

    env = OfflineEnv(life_range=(35, 36))
    eval_env = OfflineEnv(life_range=(35, 36))

    agent = QTableAgent(
        env.observation_space,
        env.action_space,
        alpha=0.1,  # 学習率
        gamma=0.9,  # 割引率
        epsilon=EPSILON,
    )

    eval_rewards, elapse_time, steps = train(
        env,
        eval_env=eval_env,
        agent=agent,
        num_steps=NUM_STEPS,  # 学習ステップ数
        eval_interval=(NUM_STEPS / 10),  # 評価のステップ間隔
        eval_steps=100,  #
        log_q=Path(".") / Q_FILE_NAME,  # Qテーブルの書き出し先
        plot_interval=(NUM_STEPS / 4),
        plot_steps=20,
        plot_q=DISPLAY_Q,
    )

    # csvファイルに書き出す
    df = pd.DataFrame({"step": steps, "eval_rewards": eval_rewards})
    df.to_csv("test_eval.csv")

    # 可視化する
    plt.plot(steps, eval_rewards)
    plt.xlabel("#step")
    plt.ylabel("Evaluated summed reward")
    plt.show()
