import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive rendering
import matplotlib.pyplot as plt
import numpy as np


class ProjectManagementApp:
    def __init__(self):
        self.activities = {}
        self.predecessors = {}
        self.deadlines = {}
        self.adjusted_start_times = {}
        self.max_resources = 10
        self.resources_timeline = defaultdict(int)
        self.cash_injections = {}

    def add_activity(self, name, duration, resources, predecessors, resources_per_unit_cost, total_cost, crash_duration, crash_cost, deadline=None):
        self.activities[name] = {
            'duration': duration,
            'resources': resources,
            'resources_per_unit_cost': resources_per_unit_cost,
            'total_cost': total_cost,
            'crash_duration': crash_duration,
            'crash_cost': crash_cost
        }
        self.deadlines[name] = deadline
        if name not in self.predecessors:
            self.predecessors[name] = set()
        self.predecessors[name].update(predecessors)

    def get_start_time(self, node):
        # Use adjusted start time if available
        return self.adjusted_start_times.get(node, self.calculate_earliest_start_times().get(node, 0))

    def calculate_earliest_start_times(self):
        aon_graph = nx.DiGraph()

        for activity, preds in self.predecessors.items():
            for pred in preds:
                aon_graph.add_edge(pred, activity)

        topo_sort = list(nx.topological_sort(aon_graph))

        earliest_start = {}
        for node in topo_sort:
            if not list(aon_graph.predecessors(node)):
                earliest_start[node] = 0
            else:
                earliest_start[node] = max([earliest_start[pred] + self.activities[pred]['duration'] for pred in aon_graph.predecessors(node)])

        # Ensure all activities have an initial start time in adjusted_start_times
        for activity in self.activities:
            if activity not in self.adjusted_start_times:
                self.adjusted_start_times[activity] = earliest_start.get(activity, 0)

        return earliest_start


    def calculate_latest_finish_times(self):
        aon_graph = nx.DiGraph()

        for activity, preds in self.predecessors.items():
            for pred in preds:
                aon_graph.add_edge(pred, activity)

        topo_sort = list(nx.topological_sort(aon_graph))
        earliest_start = self.calculate_earliest_start_times()
        latest_finish = {}
        max_earliest_finish = max(earliest_start[node] + self.activities[node]['duration'] for node in earliest_start)

        for node in reversed(topo_sort):
            if not list(aon_graph.successors(node)):
                latest_finish[node] = max_earliest_finish
            else:
                latest_finish[node] = min(latest_finish[succ] - self.activities[node]['duration'] for succ in aon_graph.successors(node))
            deadline = self.deadlines.get(node)
            if deadline is not None:
                latest_finish[node] = min(latest_finish[node], deadline)

        return latest_finish

    def calculate_critical_path(self):
        aon_graph = nx.DiGraph()

        for activity, preds in self.predecessors.items():
            for pred in preds:
                aon_graph.add_edge(pred, activity)

        topo_sort = list(nx.topological_sort(aon_graph))

        earliest_start = {}
        earliest_finish = {}
        for node in topo_sort:
            if not list(aon_graph.predecessors(node)):
                earliest_start[node] = 0
            else:
                earliest_start[node] = max([earliest_finish[pred] for pred in aon_graph.predecessors(node)])
            earliest_finish[node] = earliest_start[node] + self.activities[node]['duration']

        latest_start = {}
        latest_finish = self.calculate_latest_finish_times()
        for node in reversed(topo_sort):
            if not list(aon_graph.successors(node)):
                latest_finish[node] = earliest_finish[node]
            else:
                latest_finish[node] = min([latest_start[succ] for succ in aon_graph.successors(node)])
            latest_start[node] = latest_finish[node] - self.activities[node]['duration']

        critical_path = [node for node in topo_sort if earliest_start[node] == latest_start[node]]

        # Calculate floats
        total_float = {node: latest_finish[node] - earliest_finish[node] for node in aon_graph.nodes()}
        free_float = {node: min([(earliest_start[succ] - earliest_finish[node]) for succ in aon_graph.successors(node)], default=total_float[node]) for node in aon_graph.nodes()}

        return {
            'critical_path': ' -> '.join(critical_path),
            'early_start': earliest_start,
            'late_start': latest_start,
            'early_finish': earliest_finish,
            'late_finish': latest_finish,
            'total_float': total_float,
            'free_float': free_float
        }

    def generate_aoa(self, filename='static/aoa_graph.png'):
        plt.switch_backend('Agg')  # Use non-GUI backend to avoid warnings
        aoa_graph = nx.DiGraph()
        event_counter = 1
        events = {}

        for activity, preds in self.predecessors.items():
            if preds:
                for pred in preds:
                    start_event = events.get(pred, event_counter)
                    if pred not in events:
                        events[pred] = start_event
                        event_counter += 1
                    end_event = events.get(activity, event_counter)
                    if activity not in events:
                        events[activity] = end_event
                        event_counter += 1
                    aoa_graph.add_edge(start_event, end_event, label=activity)
            else:
                start_event = event_counter
                event_counter += 1
                end_event = event_counter
                event_counter += 1
                events[activity] = end_event
                aoa_graph.add_edge(start_event, end_event, label=activity)

        pos = nx.spring_layout(aoa_graph)
        labels = nx.get_edge_attributes(aoa_graph, 'label')
        
        # Customize node and edge styles
        node_options = {"node_size": 700, "node_color": "skyblue", "font_size": 10, "font_weight": "bold"}
        edge_options = {"edge_color": "gray", "width": 2, "alpha": 0.6}
        label_options = {"font_size": 8, "font_color": "red", "font_weight": "bold", "horizontalalignment": "center", "verticalalignment": "center"}

        nx.draw(aoa_graph, pos, with_labels=True, **node_options)
        nx.draw_networkx_edges(aoa_graph, pos, **edge_options)
        nx.draw_networkx_edge_labels(aoa_graph, pos, edge_labels=labels, **label_options)
        
        plt.title("Activity on Arrow (AOA) Diagram")
        plt.savefig(filename)
        plt.close()

    def generate_aon(self, filename='static/aon_graph.png'):
        plt.switch_backend('Agg')  # Use non-GUI backend to avoid warnings
        aon_graph = nx.DiGraph()

        for activity, preds in self.predecessors.items():
            for pred in preds:
                aon_graph.add_edge(pred, activity)

        pos = nx.spring_layout(aon_graph)
        
        # Customize node and edge styles
        node_options = {"node_size": 700, "node_color": "lightgreen", "font_size": 10, "font_weight": "bold"}
        edge_options = {"edge_color": "black", "width": 2, "alpha": 0.7}
        label_options = {"font_size": 8, "font_color": "blue", "font_weight": "bold", "horizontalalignment": "center", "verticalalignment": "center"}

        nx.draw(aon_graph, pos, with_labels=True, **node_options)
        nx.draw_networkx_edges(aon_graph, pos, **edge_options)
        
        plt.title("Activity on Node (AON) Diagram")
        plt.savefig(filename)
        plt.close()

    def plot_duration_vs_resources(self, before_smoothing=True, filename='static/duration_vs_resources.png'):
        resources_timeline = defaultdict(int)
        all_activities = set(self.activities.keys())

        for node in all_activities:
            duration = self.activities[node]['duration']
            resources = self.activities[node]['resources']
            start_time = self.get_start_time(node)

            for t in range(start_time, start_time + duration):
                resources_timeline[t] += sum(resources.values())

        time_points = sorted(resources_timeline.keys())
        resources_used = [resources_timeline[t] for t in time_points]

        plt.switch_backend('Agg')
        plt.figure(figsize=(10, 6))
        plt.step(time_points, resources_used, where='post', color='b', linewidth=2)
        plt.title('Cumulative Duration vs Resources Used (Before Smoothing)')
        plt.xlabel('Cumulative Duration (days)')
        plt.ylabel('Resources Used')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

    def plot_sequence_of_events(self, critical_path, before_smoothing=True, filename='static/sequence_of_events.png'):
        earliest_start = self.calculate_earliest_start_times()
        latest_finish = self.calculate_latest_finish_times()
        sorted_activities = sorted(self.activities.keys(), key=lambda x: earliest_start[x])

        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.get_cmap('tab20', len(critical_path) + 1)
        non_critical_tracks = [[] for _ in range(len(self.activities))]

        for activity in sorted_activities:
            if activity not in critical_path:
                min_start_time = earliest_start[activity]
                for track in non_critical_tracks:
                    if not track or track[-1]['end_time'] <= min_start_time:
                        start_time = min_start_time
                        end_time = start_time + self.activities[activity]['duration']
                        track.append({'activity': activity, 'start_time': start_time, 'end_time': end_time})
                        break

        for i, activity in enumerate(sorted_activities):
            if activity in critical_path:
                start_time = earliest_start[activity]
                ax.barh("Critical Path", self.activities[activity]['duration'], left=start_time, color=colors(i), alpha=0.6)
                ax.text(start_time + self.activities[activity]['duration'] / 2, -0.2, activity, ha='center', va='center')
            else:
                for track_index, track in enumerate(non_critical_tracks):
                    for task in track:
                        if task['activity'] == activity:
                            ax.barh(f"Non-Critical Path {track_index}", self.activities[activity]['duration'], left=task['start_time'], color=colors(i), alpha=0.6)
                            ax.text(task['start_time'] + self.activities[activity]['duration'] / 2, track_index + 0.8, activity, ha='center', va='center')

                            if not before_smoothing:
                                total_float, free_float = self.calculate_floats()
                                total_float_time = total_float.get(activity, 0)
                                ax.barh(f"Non-Critical Path {track_index}", total_float_time, left=task['start_time'] + self.activities[activity]['duration'], color='gray', alpha=0.3, linestyle='dotted')

        ax.set_xlabel('Cumulative Duration (days)')
        ax.set_ylabel('Activities')
        ax.set_title('Sequence of Events in Project' + (' (Before Smoothing)' if before_smoothing else ' (After Smoothing)'))
        ax.set_ylim(-0.5, len(non_critical_tracks) + 0.5)
        ax.xaxis.grid(True)

        ax.legend().set_visible(False)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

    def plot_resource_smoothing(self, filename='static/resource_smoothing_gantt_chart.png'):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from collections import defaultdict

        # Calculate necessary data
        critical_path_data = self.calculate_critical_path()
        critical_path = critical_path_data['critical_path'].split(' -> ')
        adjusted_start = {**self.calculate_earliest_start_times(), **self.adjusted_start_times}

        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.get_cmap('tab20', len(self.activities))

        # Fixed y-positions for each activity
        activity_positions = {}
        track_assignments = defaultdict(list)

        # Track index assignment
        current_non_critical_track = 0

        # Initialize track positions
        for activity_name in self.activities.keys():
            if activity_name in critical_path:
                activity_positions[activity_name] = 0  # Critical path y-position
            else:
                predecessors = self.predecessors.get(activity_name, [])
                # If the activity has predecessors that are not critical, ensure it shares the track
                track_found = False
                for track, activities in track_assignments.items():
                    if all(pred in activities for pred in predecessors):
                        activity_positions[activity_name] = track
                        track_assignments[track].append(activity_name)
                        track_found = True
                        break

                if not track_found:
                    # New track if no suitable track is found
                    current_non_critical_track += 1
                    activity_positions[activity_name] = current_non_critical_track
                    track_assignments[current_non_critical_track].append(activity_name)

        # Plot activities
        for activity_name, position in activity_positions.items():
            duration = self.activities[activity_name]['duration']
            start_time = adjusted_start.get(activity_name, 0)  # Use adjusted start time

            # Choose color based on activity name hash
            color = colors(hash(activity_name) % len(colors.colors))
            ax.barh(position, duration, left=start_time, color=color, alpha=0.6)
            ax.text(start_time + duration / 2, position, activity_name, ha='center', va='center')

        # Prepare y-ticks and labels
        max_tracks = max(activity_positions.values())
        y_ticks = list(range(max_tracks + 1))
        y_labels = ['Critical Path'] + [f'Non-Critical Path {i}' for i in range(1, max_tracks + 1)]

        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)

        plt.xlabel('Days')
        plt.ylabel('Activities')
        plt.title('Gantt Chart with Resource Leveling')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()


    def adjust_non_critical_path_activity(self, activity_name, new_start_time):
        critical_path_data = self.calculate_critical_path()
        total_float = critical_path_data['total_float']
        free_float = critical_path_data['free_float']
        earliest_start = self.calculate_earliest_start_times()

        if activity_name not in self.activities:
            raise ValueError("Invalid activity name.")

        if free_float.get(activity_name, 0) <= 0:
            raise ValueError("The selected activity is either on the critical path or has no free float.")

        current_start_time = earliest_start[activity_name]
        if new_start_time > current_start_time + free_float[activity_name]:
            raise ValueError("The new start time exceeds the free float available.")

        # Update start time logic
        self.adjusted_start_times[activity_name] = new_start_time

        # Display the updated Gantt chart
        self.plot_resource_smoothing('static/resource_smoothing_gantt_chart.png')

        return f"New start time for '{activity_name}' is set to {new_start_time}"

    def plot_cumulative_costs_over_time(self):
        time_points = []
        cumulative_costs = []
        cumulative_cost = 0

        # Calculate the total duration based on latest finish times
        latest_finish = self.calculate_latest_finish_times()
        total_duration = max(latest_finish.values())

        for t in range(total_duration + 1):  # Include time point 0
            # Reset daily cost at the start of each day
            daily_cost = 0

            # Calculate cumulative cost at current time
            for activity_name, activity_data in self.activities.items():
                start_time = self.get_start_time(activity_name)
                duration = activity_data['duration']
                resources = activity_data['resources']
                resources_per_unit_cost = activity_data['resources_per_unit_cost']

                # Calculate total cost based on resources and per-unit costs
                for resource, amount in resources.items():
                    unit_cost = resources_per_unit_cost.get(resource, 0)
                    daily_cost += (amount * unit_cost) / duration

                # Check if the activity is ongoing or has started
                if start_time <= t < start_time + duration:
                    cumulative_cost += daily_cost

            # Append current cumulative cost to list
            time_points.append(t)
            cumulative_costs.append(cumulative_cost)

        return time_points, cumulative_costs


    def plot_Scurve(self):
        # Calculate cumulative costs over time
        time_points_cumulative, cumulative_costs = self.plot_cumulative_costs_over_time()

        # Sort cash injections by time
        time_points_cash = sorted(self.cash_injections.keys())
        amounts = [self.cash_injections[time_point] for time_point in time_points_cash]

        # Create a figure and axes for plotting
        fig, ax1 = plt.subplots(figsize=(12, 8))

        # Plot cumulative costs
        ax1.plot(time_points_cumulative, cumulative_costs, marker='o', color='b', label='Cumulative Costs')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Cumulative Cost ($)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        # Always define ax2
        ax2 = ax1.twinx()

        # Plot cash injections if available
        if time_points_cash and amounts:
            ax2.step(time_points_cash, amounts, where='post', color='r', label='Cash Injections', linewidth=2, alpha=0.7)
            ax2.set_ylabel('Cash Injection Amount ($)', color='r')
            ax2.tick_params(axis='y', labelcolor='r')

        # Determine the maximum value for both cumulative costs and cash injections
        max_cost = max(cumulative_costs) if cumulative_costs else 0
        max_injection = max(amounts) if amounts else 0
        max_value = max(max_cost, max_injection) * 1.1  # Add a 10% margin for clarity

        # Set the same limits for both y-axes
        ax1.set_ylim(0, max_value)
        ax2.set_ylim(0, max_value)

        # Title and grid
        plt.title('Cumulative Costs and Cash Injections Over Time')
        ax1.grid(True)

        # Legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.tight_layout()

        # Save the plot to a file instead of showing it
        plt.savefig('static/s_curve.png')  # Saves the figure as 's_curve.png' in the 'static' directory
        plt.close()  # Close the plot to free up memory



    def input_cash_injections(self):
        print("Enter cash injections at specific time points. Enter 'done' to finish.")

        while True:
            time_input = input("Time point (integer): ").strip()
            if time_input.lower() == 'done':
                break
            try:
                time_point = int(time_input)
                amount = float(input(f"Enter cash injection amount at time {time_point}: "))
                self.cash_injections[time_point] = amount
                print(f"Cash injection of ${amount} added at time {time_point}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer for time point and a float for amount.")

        print("\nCash injections recorded:")
        for time_point, amount in self.cash_injections.items():
            print(f"At time point {time_point}: ${amount}")

    def plot_cash_injections(self):
        if not self.cash_injections:
            print("No cash injections recorded.")
            return

        time_points = sorted(self.cash_injections.keys())
        amounts = [self.cash_injections[time_point] for time_point in time_points]

        plt.figure(figsize=(10, 6))
        plt.step(time_points, amounts, where='post', label='Cash Injections')
        plt.xlabel('Time')
        plt.ylabel('Cash Injection Amount ($)')
        plt.title('Cash Injections Over Time')
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        plt.show()



    def crash_activity(self, activity_name, crash_duration):
        if activity_name in self.activities:
            current_duration = self.activities[activity_name]['duration']
            min_duration = crash_duration  # Ensure duration does not go below zero

            if min_duration < current_duration:
                self.activities[activity_name]['duration'] = min_duration
                print(f"Activity '{activity_name}' crashed successfully to {min_duration} days (from {current_duration} days).")
            else:
                print(f"Activity '{activity_name}' already crashed to its minimum duration.")
        else:
            print(f"Error: Activity '{activity_name}' not found.")

    def crash_activities_until_irreducible_path(self, crash_budget):
        current_critical_path = self.calculate_critical_path()
        original_critical_path = current_critical_path.copy()
        crashed_activities = set()  # Track activities that have already been crashed
        remaining_budget = crash_budget  # Track remaining budget

        while True:
            # Find the least expensive activity to crash on the current critical path within the budget
            least_expensive_activity = None
            least_expensive_total_crash_cost = float('inf')
            lowest_crash_cost_per_day_activity = None
            lowest_crash_cost_per_day = float('inf')

            for activity in self.activities:
                if activity not in crashed_activities:
                    current_duration = self.activities[activity]['duration']
                    crash_duration = self.activities[activity]['crash_duration']
                    crash_cost_per_day = self.activities[activity]['crash_cost']

                    if crash_duration > 0:  # Only consider activities that can still be crashed
                        days_reduced = current_duration - crash_duration
                        total_crash_cost = crash_cost_per_day * days_reduced

                        if crash_cost_per_day < lowest_crash_cost_per_day:
                            if total_crash_cost <= remaining_budget:
                                least_expensive_activity = activity
                                least_expensive_total_crash_cost = total_crash_cost

            if least_expensive_activity is None:
                break  # No more activities to crash within budget

            # Crash the least expensive activity on the current critical path
            crash_duration = self.activities[least_expensive_activity]['crash_duration']
            self.crash_activity(least_expensive_activity, crash_duration)

            # Deduct the total crash cost from the remaining crash budget
            remaining_budget -= least_expensive_total_crash_cost

            # Add the activity to crashed_activities to prevent further crashing
            crashed_activities.add(least_expensive_activity)

            # Recalculate the critical path after crashing an activity
            current_critical_path = self.calculate_critical_path()

            # Check if the critical path has changed; if not, continue crashing
            if current_critical_path == original_critical_path:
                continue

            # Update original critical path to the new critical path found
            original_critical_path = current_critical_path.copy()

        print("Irreducible path achieved with all activities at their minimum crash durations.")
        print(f"Remaining budget after crashing: ${remaining_budget:.2f}")
        return original_critical_path




