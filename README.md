# ROS-LLM Replication + Extensions

This is a replication of the **ROS-LLM** framework (Mower et al., 2024/2026) — connecting ROS
to a large language model agent for embodied AI task execution — done as a class project, with
two original extensions on top of the base framework.

* Original paper: [arXiv:2406.19741](https://arxiv.org/abs/2406.19741)
* Original code: [huawei-noah/HEBO/ROSLLM](https://github.com/huawei-noah/HEBO/tree/master/ROSLLM)
* Original website: [rosllm.github.io](https://rosllm.github.io/)

All credit for the base ROS-LLM framework (`agent_comm`, `behavior_executor`, `rosllm_msgs`,
`rosllm_srvs`, and the external `BehaviorTree.ROS` / `executive_smach` packages) goes to the
original authors. See their citation below.

## What I built on top of it

Running the base framework on the turtlesim example surfaced two practical gaps: the LLM-driven
turtle would repeatedly drive into the simulation walls, and it had no way to reliably act on
follow-up instructions like "do that again." I added:

* **`rosllm_example/scripts/wall_aware_controller.py`** — a closed-loop controller for the
  turtlesim example that detects when the turtle is approaching a wall and runs a cooldown-gated
  escape sequence (back away, turn away from the wall, re-center) instead of letting the LLM's
  raw command drive it into the boundary. Also keeps a short rolling memory of the last few
  executed commands so "repeat"/"previous" instructions can be handled without another LLM call.

* **`agent_comm/scripts/action_memory.py`** — a lightweight action-memory module that sits
  between the natural-language instruction and the LLM call. It detects repeat-intent phrasing
  ("do that again," "same as before," "run X again," etc.) via regex pattern matching, stores a
  history of past instruction → action pairs, and can recall either the most recent action or a
  specific named one from history — avoiding an unnecessary round-trip to the LLM for
  instructions the system has already resolved before.

Together these were used as a working baseline for further research into agentic robot control.

## Packages

* `agent_comm` — communication interface with the AI agent (base framework), extended here with
  `action_memory.py`
* `behavior_executor` — nodes for executing LLM-produced behaviors in ROS (base framework)
* `rosllm_msgs` / `rosllm_srvs` — common message/service types (base framework)
* `rosllm_example` — turtlesim example (base framework), extended here with
  `wall_aware_controller.py`
* `extern/` — `BehaviorTree.ROS` and `executive_smach` (base framework, external)

## Install

Requires ROS Noetic and [catkin_tools](https://catkin-tools.readthedocs.io/en/latest/installing.html).

```bash
source /opt/ros/noetic/setup.bash
mkdir -p rosllm_ws/src && cd rosllm_ws
catkin init
git clone --recursive https://github.com/huawei-noah/HEBO.git   # clone into rosllm_ws/, NOT src/
cd src
ln -s ../HEBO/ROSLLM/
rosdep install -i -r -y --from-paths . --ignore-src
pip3 install openai PyYAML gradio whisper
catkin build -s
```

Then copy `wall_aware_controller.py` into `rosllm_example/scripts/` and `action_memory.py` into
`agent_comm/scripts/` (already included in this repo's directory layout).

## Running the turtlesim example with the extensions

```bash
roscore
roslaunch rosllm_example example.launch
rosrun rosllm_example wall_aware_controller.py
rosrun agent_comm ros_agent_srv ...params...
```

## Citation

If you use the ROS-LLM framework, please cite the original authors:

```
@misc{mower2024rosllmrosframeworkembodied,
      title={ROS-LLM: A ROS framework for embodied AI with task feedback and structured reasoning},
      author={Christopher E. Mower and Yuhui Wan and Hongzhan Yu and Antoine Grosnit and Jonas Gonzalez-Billandon and Matthieu Zimmer and Jinlong Wang and Xinyu Zhang and Yao Zhao and Anbang Zhai and Puze Liu and Davide Tateo and Cesar Cadena and Marco Hutter and Jan Peters and Guangjian Tian and Yuzheng Zhuang and Kun Shao and Xingyue Quan and Jianye Hao and Jun Wang and Haitham Bou-Ammar},
      year={2024},
      eprint={2406.19741},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2406.19741},
}
```
