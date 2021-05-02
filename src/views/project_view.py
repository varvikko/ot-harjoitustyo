from PySide2.QtCore import QObject, Slot, QUrl
from PySide2.QtQml import QQmlComponent

from views.view import View
from controllers.project_controller import project_controller

class ProjectView(View):
    def __init__(self, engine):
        super().__init__(engine)

        self.open_projects = []
        self.tabs = {}
        self.current = None
        self.project_stack = self.root.findChild(QObject, 'projectStack')
        self.project_view = self.root.findChild(QObject, 'projectView')
        self.tab_bar = self.root.findChild(QObject, 'projectsTab')

        self.components = {
            'editor_view': QQmlComponent(self.engine, QUrl('src/views/qml/EditorView.qml')),
            'project_tab': QQmlComponent(self.engine, QUrl('src/views/qml/components/ProjectTab.qml')),
            'resource_entry': QQmlComponent(self.engine, QUrl('src/views/qml/components/ResourceEntry.qml'))
        }

    def is_project_open(self, project_id):
        return len([project for project in self.open_projects
            if project.project_id == project_id]) > 0

    @Slot(str)
    def open_project(self, project_id):
        if self.is_project_open(project_id):
            return

        project = project_controller.get_project_by_id(project_id)
        self.open_projects.append(project)

        self.create_editor_view(project)

        self.load_resources(project_id)

        self.project_view.setProperty('projectCount', len(self.open_projects))
        if not self.current:
            self.current = project_id

    def load_resources(self, project_id):
        resources = project_controller.get_resources(project_id)

        editor = self.project_stack.find_editor(project_id)
        
        for resource in resources:
            editor.add_resource(resource.name, resource.resource_id)

    def create_editor_view(self, project):
        self.project_stack.add_editor_view(project.name, project.project_id)
        
        # Add tab
        tab = self.components['project_tab'].create()
        tab.setProperty('text', project.name)
        tab.setProperty('project_id', project.project_id)
        self.tab_bar.addItem(tab)
        self.tabs[project.project_id] = tab

    @Slot(str)
    def show_project(self, project_id):
        self.project_stack.show_project(project_id)

        self.current = project_id

    @Slot(str, str)
    def open_resource(self, name, resource_id):
        source = project_controller.read_resource(resource_id, self.current)
        editor = self.project_stack.find_editor(self.current)

        editor.open_resource(name, source, resource_id)

    @Slot(str)
    def show_resource(self, resource_id):
        editor = self.project_stack.find_editor(self.current)

        editor.show_resource(resource_id)

    @Slot(str)
    def close_resource(self, resource_id):
        editor = self.project_stack.find_editor(self.current)

        editor.close_resource(resource_id)

    @Slot()
    def add_resource(self):
        print('add resource')

    @Slot()
    def save_resource(self):
        pass

    @Slot()
    def save_project(self):
        pass

    @Slot()
    def close_project(self):
        if len(self.open_projects) == 0:
            return

        print(self.current)
        editor = self.project_stack.find_editor(self.current)
        editor.deleteLater()

        # Remove tab
        tab = self.tabs[self.current]
        tab.deleteLater()
        self.tabs[self.current] = None

        self.open_projects = list(filter(lambda p: p.project_id != self.current, self.open_projects))

        if len(self.open_projects) >= 1:
            self.current = self.open_projects[-1].project_id
            self.show_project(self.current)
        else:
            self.current = None
