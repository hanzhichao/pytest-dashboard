import inspect
import json
import os
import time
import uuid
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

ROOT_DIR = Path(__file__).parent.parent
TEST_PATH = ROOT_DIR / 'testcases'
TESTPLAN_DIR = ROOT_DIR / 'web' / 'testplans'
REPORT_DIR = ROOT_DIR / 'web' / 'templates'




class MyPlugin:
    def __init__(self):
        self.testcases = {}

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            # print('item.originalname', item.originalname)
            # print('item.name', item.name)
            # print('item.own_markers', item.own_markers)
            # print('item.location', item.location)
            # print('item.module', item.module)
            # print('item.setup', item.setup)
            # print(dir(item))
            tags = []
            level = ''
            owner = ''
            for marker in item.iter_markers():
                if marker.args or marker.kwargs:
                    if marker.name == 'level':
                        level = f'P{marker.args[0]}'
                    elif marker.name == 'owner':
                        owner = marker.args[0]
                else:
                # print('marker', marker.name, marker.args, marker.kwargs)
                # if not marker.args and marker.kwargs:
                    tags.append(marker.name)
                # print('maker', marker.name)
            function = item.function
            code = inspect.getsource(function)
            # testcase_title = function.__doc__ or function.__name__
            nodeid = item.nodeid
            id = str(uuid.uuid4()).replace('-', '')
            self.testcases[id] = {
                'id': id,
                'name': item.name,
                'doc': function.__doc__ or '',
                'level': level,
                'tags': tags,
                'owner': owner,
                'nodeid': nodeid,
                'code': code
            }



@app.route('/')
def home():
    plugin = MyPlugin()
    temp_stdout = StringIO()
    # with redirect_stdout(temp_stdout):  # 不显示命令行输出
    pytest.main([TEST_PATH, '--co', '-q'], plugins=[plugin])
    # print(plugin.testcases)
    return render_template('./testcase_list.html', testcases=plugin.testcases.values())

@app.route('/testcase_list.json')
def testcase_list():
    plugin = MyPlugin()
    pytest.main([TEST_PATH, '--co', '-q'], plugins=[plugin])
    print(plugin.testcases)
    return jsonify(list(plugin.testcases.values()))


@app.route('/testcase_debug')
def testcase_debug():
    nodeid = request.args.get('nodeid')
    testcase_path = ROOT_DIR / nodeid
    import sys
    sys.path.append(str(ROOT_DIR))

    cmd = f'pytest {testcase_path} -vs --no-summary --no-header'
    output = os.popen(cmd)
    # print(output.read())
    return '<pre>' + output.read() + '</pre>'


@app.route('/testplan_add', methods=['POST'])
def testplan_add():
    nodeids = request.form.getlist('nodeids')
    testplan_name = request.form.get('testplan_name')
    print('nodeids', nodeids)
    testplan_file = TESTPLAN_DIR / f'{testplan_name}.json'
    with open(testplan_file, 'w', encoding='utf-8') as f:
        json.dump(nodeids, f, indent=2, ensure_ascii=False)
    return '创建成功'


@app.route('/testplan_list')
def testplan_list():
    testplans = []
    for file_name in os.listdir(TESTPLAN_DIR):
        testplan_name = file_name.replace('.json', '')
        with open(TESTPLAN_DIR / file_name) as f:
            data = json.load(f)
        testcases_count = len(data)
        create_time = time.strftime('%Y年%m月%d日 %H:%M:%S',
                                    time.localtime(os.path.getctime(TESTPLAN_DIR / file_name)))
        testplans.append({
            'testplan_name': testplan_name,
            'testcases_count': testcases_count,
            'create_time': create_time
        })
    print('testplans', testplans)
    return render_template('./testplan_list.html', testplans=testplans)


@app.route('/testplan_run', methods=['GET', 'POST'])
def testplan_run():
    plugin = MyPlugin()
    testplan_name = request.args.get('testplan_name')
    testplan_file = TESTPLAN_DIR / f'{testplan_name}.json'
    print('testplan_file', testplan_file)
    with open(testplan_file, encoding='utf-8') as f:
        nodeids = json.load(f)
    print('nodeids', nodeids)
    testcase_paths = [str(ROOT_DIR / nodeid) for nodeid in nodeids]
    import sys
    sys.path.append(str(ROOT_DIR))
    print('testcase_paths', testcase_paths)
    # os.remove(REPORT_DIR / "report.html")
    pytest.main([*testcase_paths, '-v', f'--html={REPORT_DIR / "report.html"}', '--self-contained-html'],
                plugins=[plugin])
    return redirect('/testplan_report')


@app.route('/testplan_report')
def testplan_report():
    return render_template('./testplan_report.html')


@app.route('/report')
def report():
    return render_template('./report.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
