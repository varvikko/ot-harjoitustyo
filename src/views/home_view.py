import dateutil.parser
from PySide2.QtCore import QObject, Slot, QUrl
from PySide2.QtQml import QQmlComponent
from PySide2.QtQuick import QQuickItem
from PySide2.QtWidgets import QComboBox

from views.view import View
from controllers.project_controller import project_controller
from controllers.template_controller import template_controller
from utils.exceptions import (
    DirectoryNotEmptyError, InvalidValueError, ProjectExistsError
)
from config.config import config


class HomeView(View):
    def __init__(self, engine):
        super().__init__(engine)

        self.component = QQmlComponent(self.engine)
        self.component.loadUrl('src/views/qml/components/PreviewCard.qml')
        self.projects_list = self.root.findChild(QQuickItem, 'projects')
        self.load_projects()

    def load_projects(self):
        projects = project_controller.get_projects()

        for project in projects:
            self.add_project(project)

    def add_project(self, project):
        item = self.component.create()
        item.setProperty('project_id', project.project_id)
        item.setProperty('name', project.name)
        item.setProperty(
            'modified', f'Last modified: {self.timestamp_to_date(project.last_modified)}')
        item.setObjectName(project.project_id)
        item.setParentItem(self.projects_list)
        item.setParent(self.projects_list)

    def timestamp_to_date(self, timestamp):
        return str(dateutil.parser.isoparse(timestamp).date())

    @Slot(str, str, str)
    def create_project_clicked(self, name, path, template_name):
        try:
            project = project_controller.create_project(name, path, template_name)
            self.add_project(project)
        except InvalidValueError as err:
            self.show_error('Project creation failed', str(err))
        except DirectoryNotEmptyError:
            self.show_error('Project creation failed', 'Directory not empty')
        except ProjectExistsError:
            self.show_error('Project creation failed', 'Project exists')
        except PermissionError:
            self.show_error('Project creation failed', 'Permission denied')

    def show_error(self, title, message):
        error_dialog = self.root.findChild(QObject, 'errorDialog')
        error_dialog.setProperty('title', title)
        error_dialog.setProperty('text', message)
        error_dialog.setProperty('visible', True)

    @Slot()
    def import_project_clicked(self):
        print('import project')

    @Slot(result=str)
    def get_default_path(self):
        return config.get_value('default_project_path')

    @Slot(str)
    def request_project_removal(self, project_id):
        self.project_to_remove = project_id
        project = project_controller.get_project_by_id(project_id)
        if not project:
            return

        child = self.root.findChild(QObject, 'confirmRemovalDialog')
        child.setProperty('visible', True)

        child.setProperty(
            'text', f'Do you want to remove project {project.name}?')

    @Slot(result=str)
    def remove_confirmed(self):
        project_controller.remove_project(self.project_to_remove)

        child = self.root.findChild(QQuickItem, self.project_to_remove)
        child.deleteLater()

        return self.project_to_remove

    @Slot()
    def load_templates(self):
        templates = template_controller.get_template_names()

        dropdown = self.root.findChild(QObject, 'templateDropdown')
        dropdown.set_model([''] + templates)
