import asyncio

from online_env import OnlineEnv
from q_learning import QTableAgent
from toio_RL.common.q_plotter import QPlotter


async def test_agent(
    env,
    agent,
    q_plot_interval,
):
    q_plotter = QPlotter(env)

    try:
        state, _ = await env.reset()
        env.render()
        q_plotter.plot_q(Q=agent.Q)

        for step in range(10000):
            print(f"\n--- ステップ {step + 1} ---")
            action = agent.greedy(state)
            state, reward, _, _, _ = await env.step(action)
            env.render()
            # if step % q_plot_interval == 0:
            #   q_plotter.plot_q(Q=agent.Q)
            q_plotter.plot_q(Q=agent.Q)
            print(f"状態:{state}, 報酬:{reward}")
            await asyncio.sleep(1.0)  # 可視化が遅れるので必須
    except KeyboardInterrupt:
        print("\nCtrl+C を受け取りました。終了します。")
    finally:
        await env.close()


if __name__ == "__main__":
    """
    TODO 学習前の状態の観察
    
    準備
    1. toioのIDを入力（agent_nameが学習するtoio，target_nameが目標のtoio）
    2. 学習toioをマットにおいて，目標toioは手元においておく
    3. terminalで仮想環境にいることを確認
    4. terminalでカレントディレクトリが`toio_RL\d1_workshop1113`であることを確認．異なる場合は`cd toio_RL\d1_workshop1113'

    実行
    5. コマンド`python demo1_adapt.py`

    デモ
    6. 目標toioをマットに置く
    7. Q値のplotが表示されている（全て0，ランダムに動く）
    8. ctrl+cで停止
    """
    env = OnlineEnv(agent_name="toio-n2r", target_name="toio-22N")
    agent = QTableAgent(
        env.observation_space,
        env.action_space,
    )
    asyncio.run(test_agent(env, agent, q_plot_interval=1))
