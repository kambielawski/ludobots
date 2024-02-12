"""Experiment Visualizer for the AFPO algorithm."""
import os
import sys
import re
import subprocess
from collections import Counter
import pickle
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QTabWidget, QComboBox, QToolBar, QPushButton, QAction
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

COLORS = ['red', 'blue', 'green', 'orange', 'yellow', 'purple']

def Simulate_Brain(brain_file,
                   body_file='./robots/body_quadruped.urdf',
                   world_file='./task_environments/world.sdf'):
    """Simulate a brain and return sensor/action pairs"""
    # Simulate and store simulations
    print(f'Simulating brain from file {brain_file}')
    os.system(f'python3 simulate.py DIRECT 0 {brain_file} {body_file} --objects_file {world_file} --pickle_sim True')
    with open('transient.pkl', 'rb') as pf:
        sim = pickle.load(pf)

    # Create sensor/action pairs and rank sizes
    robot = sim.robots[0]
    return robot.actionz, robot.sensorz

class DataManager():
    """Class to manage data from experiments and provide methods to access and manipulate it."""
    def __init__(self, experiment_rootdir='./experiments'):
        self.experiment_rootdir = experiment_rootdir
        self.experiment_directories = sorted([d for d in os.listdir(experiment_rootdir) if os.path.isdir(f'{experiment_rootdir}/{d}')])
        self.trials_cache = {}

    def Get_Experiment_Directories(self):
        """Return a list of all experiment directories in the root directory."""
        return self.experiment_directories

    def Get_Trials(self, dir):
        """Create a trials dictionary from the pickled files in the experiment directory."""
        if dir not in self.trials_cache: # Cache trials object if it hasn't been already
            self.trials_cache[dir] = {}
            for trial in os.listdir(f'./experiments/{dir}'):
                if trial.startswith('trial'):
                    with open(f'./experiments/{dir}/{trial}/{trial}.pkl', 'rb') as pkl:
                        self.trials_cache[dir][trial] = pickle.load(pkl)
        
        return self.trials_cache[dir]

    def Get_Experiment_Metrics(self, dir):
        """Return the selection metrics of an experiment."""
        trials = self.Get_Trials(dir)
        k = list(trials.keys())[0]
        exp_population = trials[k].afpo.population
        for solution in exp_population:
            if exp_population[solution].selection_metrics:
                all_selection_metrics = exp_population[solution].selection_metrics
                break
            elif exp_population[solution].aggregate_metrics:
                all_selection_metrics = exp_population[solution].aggregate_metrics
                break
        return all_selection_metrics

    def Get_Experiment_Constants(self, dir):
        """Return the robot constants of an experiment."""
        with open(f'./experiments/{dir}/exp_params.txt', 'r') as f:
            return eval(f.read())

    def Get_Experiment_Selection_Metrics(self, dir):
        """Return the selection metrics of an experiment."""
        trials = self.Get_Trials(dir)
        k = list(trials.keys())[0]
        selection_metrics = trials[k].afpo.selection_metrics.keys()
        return selection_metrics

    def getMetric95CI(self, trials, metric):
        """Return the 95% confidence interval for the top metric over generations."""
        best = []

        for _, trial in trials.items():
            best_over_generations = trial.afpo.history.Get_Top_Metric_Over_Generations(metric)
            best.append(best_over_generations)

        grouped_by_generation = list(zip(*best))
        top_averages = [np.mean([x[1] for x in gen]) for gen in grouped_by_generation]
        confidence_intervals = [st.t.interval(0.95, len(gen)-1, loc=top_averages[i], scale=st.sem(gen)) for i, gen in enumerate(grouped_by_generation)]
        confidence_intervals = [(ci[1][1] - ci[0][1])/2 for ci in confidence_intervals]
        return np.array(top_averages), np.array(confidence_intervals)

    def Get_Top_Robot(self, dir, metric):
        """Return the brain file, body file, and world file for the top robot in the experiment directory."""
        trials = self.Get_Trials(dir)
        # trial = trials[list(trials.keys())[0]]
        top_robots = [(trial.afpo.Get_Best_Id(metric), trial_id) for trial_id, trial in trials.items()]
        ((max_metric, max_solution_id), max_trial_id) = max(top_robots)
        
        trials[max_trial_id].afpo.population[max_solution_id].Regenerate_Brain_File(dir='.')
        brain_file = f'./brain_{max_solution_id}.nndf'

        if 'task_environment' not in trials[max_trial_id].afpo.robot_constants:
            if 'boxdisplacement' in dir:
                trials[max_trial_id].afpo.robot_constants['task_environment'] = './task_environments/box_world.sdf'
            else:
                trials[max_trial_id].afpo.robot_constants['task_environment'] = './task_environments/world.sdf'

        morphology = trials[max_trial_id].afpo.robot_constants['morphology']
        body_file = f'./robots/body_{morphology}.urdf'

        world_file = trials[max_trial_id].afpo.robot_constants['task_environment']
        
        return brain_file, body_file, world_file

    def Get_Top_Robots_All_Runs(self, dir, metric):
        print(f'\n\n{dir}\n\n')
        trials = self.Get_Trials(dir)
        top_robots = [(trial.afpo.Get_Best_Id(metric), trial_id) for trial_id, trial in trials.items()]

        # Ensure the brain file exists
        for (_, max_id), trial_id in top_robots:
            trials[trial_id].afpo.population[max_id].Regenerate_Brain_File()

        top_robots = [(f'./experiments/{dir}/brain_{max_soln_id}.nndf',
                        trials[trial_id].afpo.robot_constants['morphology'],
                        './task_environments/box_world.sdf')
                        for ((_, max_soln_id), trial_id) in top_robots]

        return top_robots


class MainWindow(QMainWindow):
    """Main window for the experiment visualizer."""
    def __init__(self):
        super().__init__()

        self.data_manager = DataManager()

        # Toolbar
        self.save_plot_action = QAction('Save Plot', self)                      # Save plot button
        self.show_top_brain_action = QAction('Show Top Brain', self)            # Show top brain button
        self.show_brains_pairplot_action = QAction('SA Pair Plot', self)     # SA pair plot
        self.show_action_plot_action = QAction('Action Distribution', self)     # Action distribution plot
        self.show_sensor_plot_action = QAction('Sensor Distribution', self)     # Sensor distribution plot
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(self.save_plot_action)
        self.toolbar.addAction(self.show_top_brain_action)
        self.toolbar.addAction(self.show_brains_pairplot_action)
        self.toolbar.addAction(self.show_action_plot_action)
        self.toolbar.addAction(self.show_sensor_plot_action)
        self.save_plot_action.triggered.connect(self.Save_Plot_Button_Onpress)
        self.show_top_brain_action.triggered.connect(self.Show_Brain_Button_Onpress)
        self.show_brains_pairplot_action.triggered.connect(self.Show_Brains_Pairplot_Onpress)
        self.show_action_plot_action.triggered.connect(self.Show_Action_Plot_Onpress)
        self.show_sensor_plot_action.triggered.connect(self.Show_Sensor_Plot_Onpress)

        # Tabs
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.activeTabs = [self.canvas1]
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.canvas1, "Tab 1")

        # Right hand side (checklist + selector)
        self.rhsWidget = QWidget(self)
        self.rhsWidgetLayout = QVBoxLayout()
        self.rhsWidget.setLayout(self.rhsWidgetLayout)
        # Metric Selector widget
        self.metricDropdownWidget = QComboBox(self)
        self.metricDropdownWidget.currentIndexChanged.connect(self.On_Metric_Selection_Update)
        # Experiment Selector widget
        self.experiment_dropdown_widget = QComboBox(self)
        self.experiment_dropdown_widget.currentIndexChanged.connect(self.On_Experiment_Selection_Update)
        # Checklist tree
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['Checklist'])

        self.rhsWidgetLayout.addWidget(self.metricDropdownWidget)
        self.rhsWidgetLayout.addWidget(self.experiment_dropdown_widget)
        self.rhsWidgetLayout.addWidget(self.tree)

        self.currentlyCheckedDirs = []
        self.currentlySelectedMetric = None

        # Add items to the tree
        self.Init_Experiment_Checklist()
        self.tree.itemChanged.connect(self.On_Checklist_Update)

        # Create the splitter
        splitter = QSplitter()
        self.setCentralWidget(splitter)
        splitter.addWidget(self.tabWidget)
        splitter.addWidget(self.rhsWidget)

        self.Plot()

    def Get_Checked_Items(self, tree_widget):
        """Return a list of all checked items in the tree widget."""
        checked_items = []
        
        # Iterate through all top-level items
        top_level_item_count = tree_widget.topLevelItemCount()
        for i in range(top_level_item_count):
            item = tree_widget.topLevelItem(i)
            
            # Check the state of the item
            if item.checkState(0) == Qt.Checked:
                checked_items.append(item.text(0))
                
        return checked_items

    def Init_Experiment_Checklist(self):
        """Populate the experiment checklist with all experiment directories."""
        for exp_dir_str in self.data_manager.Get_Experiment_Directories():
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, exp_dir_str)
            parent.setFlags(parent.flags() | Qt.ItemIsUserCheckable)
            parent.setCheckState(0, Qt.Unchecked)

    def Populate_Dropdown_Widget(self):
        """Populate the metric dropdown widget with the metrics from the currently checked directories."""
        if self.metricDropdownWidget.count() == 0:
            all_selection_metrics = []
            for dir in self.currentlyCheckedDirs:
                all_selection_metrics += list(self.data_manager.Get_Experiment_Metrics(dir).keys())
            for selection_metric in np.unique(all_selection_metrics):
                # if selection_metric not in self.metricDropdownWidget.
                self.metricDropdownWidget.addItem(selection_metric)

    def Add_Tab(self):
        """Add a new tab to the tab widget."""
        new_figure = Figure()
        new_canvas = FigureCanvas(new_figure)
        self.activeTabs.append(new_canvas)
        self.tabWidget.addTab(new_canvas, f"Tab {len(self.activeTabs)}")

    def Close_Tab(self, tabname):
        """Close the tab with the given name."""
        for i in range(len(self.tabWidget.count())):
            if self.tabWidget.tabText(i) == tabname:
                self.tabWidget.removeTab(i)
                return

    def On_Checklist_Update(self, item):
        """Update the currently checked directories."""
        if item.checkState(0) == Qt.Checked:
            self.currentlyCheckedDirs.append(item.text(0))
            self.experiment_dropdown_widget.addItem(item.text(0))
            # Load data upon check...
        else:
            print(self.currentlyCheckedDirs)
            print(item.text(0))
            print(self.currentlyCheckedDirs.index(item.text(0)))
            self.currentlyCheckedDirs.remove(item.text(0))
            self.experiment_dropdown_widget.removeItem(self.experiment_dropdown_widget.currentIndex())

        self.Populate_Dropdown_Widget()
        self.Plot()

    def On_Metric_Selection_Update(self, item_idx):
        """Update the currently selected metric."""
        print(self.metricDropdownWidget.itemText(item_idx))
        self.currentlySelectedMetric = self.metricDropdownWidget.itemText(item_idx)
        self.Plot()

    def On_Experiment_Selection_Update(self, new_id):
        pass

    def Plot(self):
        """Plot the currently selected metric over generations."""
        self.figure1.clear() # Clear the previous plot

        self.plotMetric95CI(self.currentlyCheckedDirs, self.currentlySelectedMetric)

        self.canvas1.draw()

    def plotMetric95CI(self, experiment_dirs, metric):
        """Plot the 95% confidence interval for the top metric over generations."""
        loaded_data = {}
        for exp_dir in experiment_dirs:
            loaded_data[exp_dir] = self.data_manager.Get_Trials(exp_dir)

        ax1 = self.figure1.add_subplot(111)
        # Plot each line from each loaded data
        for i, (exp_dir, trials) in enumerate(loaded_data.items()):
            plot_label = '-'.join(self.data_manager.Get_Experiment_Metrics(exp_dir))
            t1_avg_best, t1_conf_int = self.data_manager.getMetric95CI(trials, metric)
            # Plotting
            ax1.plot(range(len(t1_avg_best)), t1_avg_best, label=plot_label, color=COLORS[i])
            ax1.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color=COLORS[i], alpha=0.3)
        
        if len(experiment_dirs): # Create title (body, task environment)
            consts = self.data_manager.Get_Experiment_Constants(experiment_dirs[0])
            body = consts['morphology']
            title = f'{body}' # _{task_environment}'
        else:
            title = metric

        ax1.set_title(title)
        ax1.set_xlabel('Generation')
        ax1.set_ylabel(f'{metric} (95% CI)')
        ax1.legend()

    def Save_Plot_Button_Onpress(self):
        """Save the current plot to a file."""
        pass

    def Show_Brain_Button_Onpress(self):
        """Show the brain of the top robot in the selected experiment."""
        # Get the currently selected experiment
        current_dir = self.experiment_dropdown_widget.currentText()
        metric = self.metricDropdownWidget.currentText()

        # Extract the top brain from the current experiment
        brain_file, body_file, world_file = self.data_manager.Get_Top_Robot(current_dir, metric)
        print(brain_file, body_file, world_file)

        # Spawn subprocess to show the brain
        print(current_dir, metric)
        subprocess_run_string = ['python3', 'simulate.py', 'GUI', '0', 
                                brain_file, 
                                body_file,
                                '--objects_file', world_file,
                                '--motor_measure', 'VELOCITY',
                                '--empowerment_window_size', '500']

        sp = subprocess.Popen(subprocess_run_string, stdout=subprocess.PIPE)

        # Parse standard output from subprocess
        stdout, _ = sp.communicate()
        sp.wait()
        out_str = stdout.decode()
        fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')
        print(fitness_metrics)

    def Show_Brains_Pairplot_Onpress(self):
        """Show the sensor-action pair plot for the top N robots in the selected experiments."""
        self.figure1.clear() # Clear the previous plot
        ax1 = self.figure1.add_subplot(111)

        # Get the currently selected experiment
        checked_dirs = self.Get_Checked_Items(self.tree)
        metric = self.metricDropdownWidget.currentText()

        # Get the top robot files from all runs
        robot_files = {}
        for dir in checked_dirs:
            robots = self.data_manager.Get_Top_Robots_All_Runs(dir, metric)
            robot_files[dir] = robots
        
        # Aggregate results from each run
        for i, dir in enumerate(robot_files):
            for j, (brain_file, body, world_file) in enumerate(robot_files[dir][:10]):
                # 1000 sensors
                # Stored in a temporary directory... 
                body_file = f'./robots/body_{body}.urdf'
                print(f'=============\n{brain_file}, {body_file}, {world_file}\n===========\n')
                actions, sensors = Simulate_Brain(brain_file, body_file, world_file)
                sa_pairs = [(a,s) for a in actions for s in sensors]
                pair_counts = Counter(sa_pairs)
                size = sorted(pair_counts.values(), reverse=True)
                rank = range(1,len(size)+1)
                if j == 0:
                    label = brain_file.split('_')[4]
                    ax1.scatter(np.log10(rank), np.log10(size), color=COLORS[i], alpha=0.1, label=label)
                else:
                    ax1.scatter(np.log10(rank), np.log10(size), color=COLORS[i], alpha=0.1)
        
        ax1.set_title('')
        ax1.set_xlabel(f'Log(rank)')
        ax1.set_ylabel(f'Log(size)')
        ax1.legend()
        self.canvas1.draw()

    def Show_Action_Plot_Onpress(self):
        """Show the action plot for the top N robots in the selected experiments."""
        self.figure1.clear() # Clear the previous plot
        ax1 = self.figure1.add_subplot(111)

        # Get the currently selected experiment
        checked_dirs = self.Get_Checked_Items(self.tree)
        metric = self.metricDropdownWidget.currentText()

        # Get the top robot files from all runs
        robot_files = {}
        for dir in checked_dirs:
            robots = self.data_manager.Get_Top_Robots_All_Runs(dir, metric)
            robot_files[dir] = robots
        
        # Aggregate results from each run
        for i, dir in enumerate(robot_files):
            for j, (brain_file, body, world_file) in enumerate(robot_files[dir][:10]):
                # 1000 actions
                # Stored in a temporary directory... 
                body_file = f'./robots/body_{body}.urdf'
                print(f'=============\n{brain_file}, {body_file}, {world_file}\n===========\n')
                actions, _ = Simulate_Brain(brain_file, body_file, world_file)
                action_counts = Counter(actions)
                size = sorted(action_counts.values(), reverse=True)
                rank = range(1,len(size)+1)
                if j == 0:
                    label = brain_file.split('_')[4]
                    ax1.scatter(np.log10(rank), np.log10(size), color=COLORS[i], alpha=0.2, label=label)
                else:
                    ax1.scatter(np.log10(rank), np.log10(size), color=COLORS[i], alpha=0.2)
        
        ax1.set_title('Actions')
        ax1.set_xlabel(f'Log(Rank)')
        ax1.set_ylabel(f'Log(Size)')
        ax1.legend()
        self.canvas1.draw()

    def Show_Sensor_Plot_Onpress(self):
        """Show the sensor plot for the top N robots in the selected experiments."""
        self.figure1.clear() # Clear the previous plot
        ax1 = self.figure1.add_subplot(111)

        # Get the currently selected experiment
        checked_dirs = self.Get_Checked_Items(self.tree)
        metric = self.metricDropdownWidget.currentText()

        # Get the top robot files from all runs
        robot_files = {}
        for dir in checked_dirs:
            robots = self.data_manager.Get_Top_Robots_All_Runs(dir, metric)
            robot_files[dir] = robots
        
        # Aggregate results from each run
        for i, dir in enumerate(robot_files):
            for j, (brain_file, body, world_file) in enumerate(robot_files[dir][:10]):
                # 1000 actions
                # Stored in a temporary directory... 
                body_file = f'./robots/body_{body}.urdf'
                print(f'=============\n{brain_file}, {body_file}, {world_file}\n===========\n')
                _, sensors = Simulate_Brain(brain_file, body_file, world_file)
                sensor_counts = Counter(sensors)
                size = sorted(sensor_counts.values(), reverse=True)
                rank = range(1,len(size)+1)
                if j == 0:
                    label = brain_file.split('_')[4]
                    ax1.scatter(np.log10(rank), np.log10(size), color=COLORS[i], alpha=0.2, label=label)
                else:
                    ax1.scatter(np.log10(rank), np.log10(size), color=COLORS[i], alpha=0.2)
        
        ax1.set_title('Sensors')
        ax1.set_xlabel(f'Log(Rank)')
        ax1.set_ylabel(f'Log(Size)')
        ax1.legend()
        self.canvas1.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
