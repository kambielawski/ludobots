import os
import sys
import re
import subprocess
import pickle
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QTabWidget, QComboBox, QToolBar, QPushButton, QAction
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

COLORS = ['red', 'blue', 'yellow', 'green', 'orange', 'purple']

class DataManager():
    def __init__(self, experiment_rootdir='./experiments'):
        self.experiment_rootdir = experiment_rootdir
        self.experiment_directories = sorted([d for d in os.listdir(experiment_rootdir) if os.path.isdir(f'{experiment_rootdir}/{d}')])
        self.evo_runs_cache = {}

    def Get_Experiment_Directories(self):
        return self.experiment_directories

    def get_evo_runs(self, dir):
        if dir not in self.evo_runs_cache: # Cache evo_runs object if it hasn't been already
            with open(f'./experiments/{dir}/evo_runs.pickle', 'rb') as pickleFile:
                self.evo_runs_cache[dir] = pickle.load(pickleFile)
        
        return self.evo_runs_cache[dir]

    def Get_Experiment_Metrics(self, dir):
        evo_runs = self.get_evo_runs(dir)

        k = list(evo_runs.keys())[0]
        # evo_runs[k][0] <--- AFPO object
        exp_population = evo_runs[k][0].population
        # exp_population[0] <--- Solution object 
        for solution in exp_population:
            if exp_population[solution].selection_metrics:
                all_selection_metrics = exp_population[solution].selection_metrics
                break
        return all_selection_metrics

    def Get_Experiment_Constants(self, dir):
        with open(f'./experiments/{dir}/evo_runs.pickle', 'rb') as pickleFile:
            evo_runs = pickle.load(pickleFile)
        k = list(evo_runs.keys())[0]
        robot_constants = evo_runs[k][0].robot_constants

        return robot_constants

    def getMetric95CI(self, runs, metric):
        best = []

        for afpo in runs:
            best_over_generations = runs[afpo].history.Get_Top_Metric_Over_Generations(metric)
            best.append(best_over_generations)

        grouped_by_generation = list(zip(*best))
        top_averages = [np.mean([x[1] for x in gen]) for gen in grouped_by_generation]
        confidence_intervals = [st.t.interval(0.95, len(gen)-1, loc=top_averages[i], scale=st.sem(gen)) for i, gen in enumerate(grouped_by_generation)]
        confidence_intervals = [(ci[1][1] - ci[0][1])/2 for ci in confidence_intervals]
        return np.array(top_averages), np.array(confidence_intervals)

    def get_top_robot(self, dir, metric):
        evo_runs = self.get_evo_runs(dir)
        evo_runs = evo_runs[list(evo_runs.keys())[0]] 
        top_robots = [(evo_runs[exp_id].Get_Best_Id(metric), exp_id) for exp_id, afpo in enumerate(evo_runs)]
        ((max_metric, max_solution_id), max_exp_id) = max(top_robots)
        
        evo_runs[max_exp_id].population[max_solution_id].Regenerate_Brain_File(dir='.')
        brain_file = f'./brain_{max_solution_id}.nndf'

        morphology = evo_runs[max_exp_id].robot_constants['morphology']
        body_file = f'./robots/body_{morphology}.urdf'

        world_file = evo_runs[max_exp_id].robot_constants['task_environment']
        
        return brain_file, body_file, world_file


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data_manager = DataManager()

        # Toolbar
        self.save_plot_action = QAction('Save Plot', self)
        self.show_top_brain_action = QAction('Show Top Brain', self)
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(self.save_plot_action)
        self.toolbar.addAction(self.show_top_brain_action)
        self.save_plot_action.triggered.connect(self.save_plot_button_onpress)
        self.show_top_brain_action.triggered.connect(self.show_brain_button_onpress)

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
        self.experiment_dropdown_widget.currentIndexChanged.connect(self.on_experiment_selection_update)
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

    def Init_Experiment_Checklist(self):
        for exp_dir_str in self.data_manager.Get_Experiment_Directories():
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, exp_dir_str)
            parent.setFlags(parent.flags() | Qt.ItemIsUserCheckable)
            parent.setCheckState(0, Qt.Unchecked)

    def Populate_Dropdown_Widget(self):
        if self.metricDropdownWidget.count() == 0:
            all_selection_metrics = []
            for dir in self.currentlyCheckedDirs:
                all_selection_metrics += list(self.data_manager.Get_Experiment_Metrics(dir).keys())
            for selection_metric in np.unique(all_selection_metrics):
                # if selection_metric not in self.metricDropdownWidget.
                self.metricDropdownWidget.addItem(selection_metric)

    def Add_Tab(self):
        new_figure = Figure()
        new_canvas = FigureCanvas(new_figure)
        self.activeTabs.append(new_canvas)
        self.tabWidget.addTab(new_canvas, f"Tab {len(self.activeTabs)}")

    def Close_Tab(self, tabname):
        for i in range(len(self.tabWidget.count())):
            if self.tabWidget.tabText(i) == tabname:
                self.tabWidget.removeTab(i)
                return

    def On_Checklist_Update(self, item):
        print(item.text(0))

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

        print(self.currentlyCheckedDirs)
        self.Populate_Dropdown_Widget()
        self.Plot()

    def On_Metric_Selection_Update(self, item_idx):
        print(self.metricDropdownWidget.itemText(item_idx))
        self.currentlySelectedMetric = self.metricDropdownWidget.itemText(item_idx)
        self.Plot()

    def Plot(self):
        self.figure1.clear() # Clear the previous plot

        self.plotMetric95CI(self.currentlyCheckedDirs, self.currentlySelectedMetric)

        self.canvas1.draw()

    def plotMetric95CI(self, experiment_dirs, metric):
        # Load each evo_runs object from pickled file in experiment directory
        loaded_data = []
        for exp_dir in experiment_dirs:
            print(exp_dir)
            with open(f'./experiments/{exp_dir}/evo_runs.pickle', 'rb') as pickleFile:
                evo_runs = pickle.load(pickleFile)
                loaded_data.append(evo_runs)

        ax1 = self.figure1.add_subplot(111)
        # Plot each line from each loaded data
        for i, evo_runs in enumerate(loaded_data):
            exp_key = list(loaded_data[i].keys())[0]
            plot_label = '-'.join(self.data_manager.Get_Experiment_Constants(experiment_dirs[i])['objectives'])
            t1_avg_best, t1_conf_int = self.data_manager.getMetric95CI(evo_runs[exp_key], metric)
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
        # plt.savefig(f'{args.dir}/plots/95CI_gen{len(t1_avg_best)}_fit_{time.time()}.png')
        # ax1.show()

    def save_plot_button_onpress(self):
        pass

    def show_brain_button_onpress(self):
        # Get the currently selected experiment
        current_dir = self.experiment_dropdown_widget.currentText()
        metric = self.metricDropdownWidget.currentText()

        # Extract the top brain from the current experiment
        brain_file, body_file, world_file = self.data_manager.get_top_robot(current_dir, metric)
        print(brain_file, body_file, world_file)

        # Spawn subprocess to show the brain
        print(current_dir, metric)
        subprocess_run_string = ['python3', 'simulate.py', 'GUI', 
                                '0', 
                                brain_file, 
                                body_file,
                                '--objects_file', world_file,
                                '--motor_measure', 'VELOCITY',
                                '--empowerment_window_size', '500']

        sp = subprocess.Popen(subprocess_run_string, stdout=subprocess.PIPE)

        # Parse standard output from subprocess
        stdout, stderr = sp.communicate()
        sp.wait()
        out_str = stdout.decode()
        fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')
        print(fitness_metrics)

    def on_experiment_selection_update(self, new_id):
        pass
        # print(new_id)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
