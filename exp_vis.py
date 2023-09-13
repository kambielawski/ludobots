import os
import sys
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
        self.experiment_directories = [d for d in os.listdir(experiment_rootdir) if os.path.isdir(f'{experiment_rootdir}/{d}')]

    def Get_Experiment_Directories(self):
        return self.experiment_directories

    def Get_Experiment_Metrics(self, dir):
        with open(f'./experiments/{dir}/evo_runs.pickle', 'rb') as pickleFile:
            evo_runs = pickle.load(pickleFile)

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dataManager = DataManager()

        # Toolbar
        self.savePlotAction = QAction('Save Plot', self)
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(self.savePlotAction)

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
        # Selector widget
        self.metricDropdownWidget = QComboBox(self)
        self.metricDropdownWidget.currentIndexChanged.connect(self.On_Metric_Selection_Update)
        # Checklist tree
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['Checklist'])

        self.rhsWidgetLayout.addWidget(self.metricDropdownWidget)
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
        for exp_dir_str in self.dataManager.Get_Experiment_Directories():
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, exp_dir_str)
            parent.setFlags(parent.flags() | Qt.ItemIsUserCheckable)
            parent.setCheckState(0, Qt.Unchecked)

    def Populate_Dropdown_Widget(self):
        # Remove current metrics in dropdown
        # self.metricDropdownWidget.clear()
        all_selection_metrics = []
        for dir in self.currentlyCheckedDirs:
            all_selection_metrics += list(self.dataManager.Get_Experiment_Metrics(dir).keys())
        for selection_metric in np.unique(all_selection_metrics):
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
            # Load data upon check...
        else:
            print(self.currentlyCheckedDirs)
            print(item.text(0))
            print(self.currentlyCheckedDirs.index(item.text(0)))
            self.currentlyCheckedDirs.remove(item.text(0))

        print(self.currentlyCheckedDirs)
        self.Populate_Dropdown_Widget()
        self.Plot()

    def On_Metric_Selection_Update(self, item_idx):
        print(self.metricDropdownWidget.itemText(item_idx))
        self.currentlySelectedMetric = self.metricDropdownWidget.itemText(item_idx)
        self.Plot()

    def Plot(self):
        # Clear the previous plot
        self.figure1.clear()

        # directories = [f'{self.dataManager.experiment_rootdir}/{dir}' for dir in self.currentlyCheckedDirs]
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
            exp_label = list(loaded_data[i].keys())[0]
            t1_avg_best, t1_conf_int = self.dataManager.getMetric95CI(evo_runs[exp_label], metric)
            # Plotting
            ax1.plot(range(len(t1_avg_best)), t1_avg_best, label=exp_label, color=COLORS[i])
            ax1.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color=COLORS[i], alpha=0.3)
        
        if len(experiment_dirs): # Create title (body, task environment)
            consts = self.dataManager.Get_Experiment_Constants(experiment_dirs[0])
            body = consts['morphology']
            task_environment = consts['task_environment']
            # selections = '-'.join(consts['objectives'])
            title = f'{body}_{task_environment}'
        else:
            title = metric

        ax1.set_title(title)
        ax1.set_xlabel('Generation')
        ax1.set_ylabel(f'{metric} (95% CI)')
        ax1.legend()
        # plt.savefig(f'{args.dir}/plots/95CI_gen{len(t1_avg_best)}_fit_{time.time()}.png')
        # ax1.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
