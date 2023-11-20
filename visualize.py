#!/usr/bin/env python3
import yaml
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PatchCollection
import numpy as np
import argparse
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from matplotlib.animation import FuncAnimation


Colors = ['orange', 'blue', 'green']

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return
        self.callback()

class Animation:
    def __init__(self, map_data, schedule):
        self.map_data = map_data
        self.schedule = schedule
        self.combined_schedule = self.schedule.copy()

        aspect = map_data["map"]["dimensions"][0] / map_data["map"]["dimensions"][1]
        self.fig, self.ax = plt.subplots(figsize=(4 * aspect, 4))
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        plt.xlim(-0.5, map_data["map"]["dimensions"][0] - 0.5)
        plt.ylim(-0.5, map_data["map"]["dimensions"][1] - 0.5)

        self.patches = []
        self.artists = []
        self.agents = {}
        self.agent_names = {}

        self.patches.append(Rectangle((-0.5, -0.5), map_data["map"]["dimensions"][0], map_data["map"]["dimensions"][1], facecolor='none', edgecolor='red'))

        for o in map_data["map"]["obstacles"]:
            x, y = o[0], o[1]
            self.patches.append(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='grey', edgecolor='black'))

        self.T = 0
        for d in map_data["agents"]:
            if "goal" in d:
                self.patches.append(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black', alpha=0.5))
            
            name = d["name"]
            self.agents[name] = Circle((d["start"][0], d["start"][1]), 0.3, facecolor=Colors[0], edgecolor='black')
            self.agents[name].original_face_color = Colors[0]
            self.patches.append(self.agents[name])

            if name in schedule:
                self.T = max(self.T, schedule[name][-1]["t"])
            else:
                print(f"Warning: Agent '{name}' does not have a schedule.")

            self.agent_names[name] = self.ax.text(d["start"][0], d["start"][1], name.replace('agent', ''))
            self.agent_names[name].set_horizontalalignment('center')
            self.agent_names[name].set_verticalalignment('center')
            self.artists.append(self.agent_names[name])

        self.anim = FuncAnimation(self.fig, self.animate_func, init_func=self.init_func, frames=int(self.T + 1) * 10, interval=100, blit=True, repeat=False)

    def save(self, file_name, speed):
        self.anim.save(file_name, "ffmpeg", fps=10 * speed, dpi=200)

    def show(self):
        plt.show()

    def init_func(self):
        for p in self.patches:
            self.ax.add_patch(p)
        for a in self.artists:
            self.ax.add_artist(a)
        return self.patches + self.artists

    def animate_func(self, i):
        for agent_name, agent in self.combined_schedule.items():
            pos = self.getState(i / 10, agent)
            p = (pos[0], pos[1])
            self.agents[agent_name].center = p
            self.agent_names[agent_name].set_position(p)

        for _, agent in self.agents.items():
            agent.set_facecolor(agent.original_face_color)

        agents_array = list(self.agents.values())
        for i in range(len(agents_array)):
            for j in range(i + 1, len(agents_array)):
                d1 = agents_array[i]
                d2 = agents_array[j]
                pos1 = np.array(d1.center)
                pos2 = np.array(d2.center)
                if np.linalg.norm(pos1 - pos2) < 0.7:
                    d1.set_facecolor('red')
                    d2.set_facecolor('red')
                    print("COLLISION! (agent-agent) ({}, {})".format(i, j))

        return self.patches + self.artists

    def getState(self, t, d):
        idx = 0
        while idx < len(d) and d[idx]["t"] < t:
            idx += 1
        if idx == 0 or idx == len(d):
            idx = min(idx, len(d) - 1)
            return np.array([float(d[idx]["x"]), float(d[idx]["y"])])
        posLast = np.array([float(d[idx - 1]["x"]), float(d[idx - 1]["y"])])
        posNext = np.array([float(d[idx]["x"]), float(d[idx]["y"])])
        dt = d[idx]["t"] - d[idx - 1]["t"]
        t = (t - d[idx - 1]["t"]) / dt
        pos = (posNext - posLast) * t + posLast
        return pos

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    parser.add_argument("schedule_folder", help="folder containing schedules for agents")
    parser.add_argument('--video', dest='video', default=None, help="output video file (or leave empty to show on screen)")
    parser.add_argument("--speed", type=int, default=1, help="speedup-factor")
    args = parser.parse_args()

    with open(args.map) as map_file:
        map_data = yaml.load(map_file, Loader=yaml.FullLoader)

    combined_schedule = {}

    # Initialize anim_instance with None
    anim_instance = None

    def reload_agent_schedules():
        for filename in os.listdir(args.schedule_folder):
            filepath = os.path.join(args.schedule_folder, filename)
            with open(filepath, 'r') as states_file:
                agent_schedule = yaml.load(states_file, Loader=yaml.FullLoader)
                agent_name = agent_schedule["agent"]
                combined_schedule[agent_name] = agent_schedule["schedule"]

        # Check if anim_instance has been defined before updating
        if anim_instance:
            anim_instance.combined_schedule = combined_schedule
            print("Reloaded agent schedules due to file changes")

    reload_agent_schedules()

    anim_instance = Animation(map_data, combined_schedule)

    event_handler = FileChangeHandler(callback=reload_agent_schedules)
    observer = Observer()
    observer.schedule(event_handler, path=args.schedule_folder, recursive=False)
    observer.start()

    try:
        if args.video:
            anim_instance.save(args.video, args.speed)
        else:
            anim_instance.show()
    finally:
        observer.stop()
        observer.join()

