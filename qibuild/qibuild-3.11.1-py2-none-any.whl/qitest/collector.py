## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import json
import glob
import qisrc
import qisys.ui as ui
import qisys.command
import qipy.venv

class PythonTestCollector:
    def __init__(self, python_worktree):
        self.python_worktree = python_worktree
        self.root = python_worktree.worktree.root
        self.pytest_path = str()
        self.python_path = str()
        self.projects = list()
        self.tests_path = list()
        venv_path = python_worktree.venv_path
        if venv_path:
            self.pytest_path = qipy.venv.find_script(venv_path, "py.test")
        else:
            self.pytest_path = qisys.command.find_program("py.test")
        if not self.pytest_path:
            raise Exception("pytest path is empty")


    def get_list_of_pytest(self, rep):
        pytest_list = list()
        for root, dirnames, filenames in os.walk(rep):
            pytest_list.extend(glob.glob(root + "/test_*.py"))
        return pytest_list


    def create_pytest_json(self, json_path, pytest_list, project):
        json_path = os.path.join(json_path, "pytest.json")
        json_data = list()
        for pytest in pytest_list:
            relpath = os.path.relpath(pytest, project.path)
            test_name = os.path.splitext(relpath)[0]
            test_name = test_name.replace("/", ".")
            test_name = project.name + "." + test_name
            pytest_data = dict()
            pytest_data['name'] = test_name
            pytest_data['cmd'] = list()
            pytest_data['cmd'].append(self.pytest_path)
            pytest_data['cmd'].append(pytest)
            pytest_data['working_directory'] = project.path
            pytest_data['environment'] = ""
            pytest_data['nightly'] = False
            pytest_data['pytest'] = True
            pytest_data['gtest'] = False
            pytest_data['perf'] = False
            pytest_data['timeout'] = 1000
            json_data.append(pytest_data)
        with open(json_path, "w") as o:
            o.write(json.dumps(json_data,indent=2))


    def get_test_and_write(self, project):
        test_list = self.get_list_of_pytest(project.path)
        self.tests_path.extend(test_list)
        if(test_list):
            self.create_pytest_json(project.path, test_list, project)
            ui.info(ui.green, " * ", ui.blue, project.src, ":", len(test_list))
        else:
            ui.info(ui.green, " * ", ui.red, project.src, ": (no tests found)")


    def collect(self):
        projects = list()
        for project in self.python_worktree.python_projects:
            src = project.src
            exist = False
            for p in projects:
                if(src.find(p) == 0):
                    exist = True
            if not exist:
                self.get_test_and_write(project)
            projects.append(src)
        ui.info(ui.yellow, "%i tests found" % (len(self.tests_path)), ui.reset)

