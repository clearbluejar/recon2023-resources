# markdown callgraph gen
# @author @clearbluejar
# @category PdiffInDark
# @keybinding
# @menupath Tools.vscode.diffmatch
# @toolbar function_graph2.png

# TODO Add User Code Here

import time
import base64
import zlib
import json
import sys
import tempfile
import os
import subprocess

# don't really limit the graph
MAX_DEPTH = sys.getrecursionlimit() - 1


# this section from
class CallGraph:

    def __init__(self, root=None):
        self.graph = {}
        self.title = None
        self.count = 0
        self.max_depth = 0
        self.root = root

    def set_root(self, root):
        self.graph.setdefault(root, [])
        self.root = root

    def add_edge(self, node1, node2, depth):

        assert self.root is not None, 'root node must be set prior to adding an edge'

        self.graph.setdefault(node1, [])
        self.graph.setdefault(node2, [])

        self.graph[node1].append((node2, depth, self.count))
        self.count += 1

        # update max depth
        if depth > self.max_depth:
            self.max_depth = depth

    def print_graph(self):
        for src, dst in self.graph.items():
            print("{src}-->{dst}".format(src=src, dst=dst))

    def root_at_end(self):
        """
        Determines the direction of the graph
        """
        # if the root has no links, the root is at the end
        return len(self.graph[self.root]) == 0

    def get_direction(self):
        """
        reports calling or called if known
        """
        direction = None

        if len(self.graph) == 1:
            direction = 'unknown'
        elif self.root_at_end():
            direction = 'calling'
        else:
            direction = 'called'

        return direction

    def get_endpoints(self):

        end_nodes = set()

        if not self.root_at_end():
            for src in list(self.graph):
                dst = self.graph[src]
                # special case of loop
                if len(dst) == 0 or len(dst) == 1 and dst[0] == src:
                    end_nodes.add(src)
        else:
            destinations = []

            for src in list(self.graph):
                dst = self.graph[src]
                # special case of loop
                if len(dst) == 1 and dst[0] == src:
                    # don't append to destinations in this case
                    continue

                for d in dst:
                    destinations.append(d[0])

            end_nodes = set(self.graph.keys()).difference(set(destinations))

        return list(end_nodes)

    def get_count_at_depth(self, depth):
        """
        Returns count for nodes at a specific depth
        """

        count = 0
        for src in list(self.graph):
            dst = self.graph[src]
            for d in dst:
                if d[1] == depth:
                    count += 1

        return count

    def links_count(self):
        """
        Returns count of edges
        """

        count = 0
        for src in list(self.graph):
            dst = self.graph[src]

            for d in dst:
                count += 1

        return count

    def gen_mermaid_flow_graph(self, direction=None, shaded_nodes=None, shade_color='#339933', max_display_depth=None, endpoint_only=False, wrap_mermaid=False):
        """
        Generate MermaidJS flowchart from self.graph
        See https://mermaid.js.org/syntax/flowchart.html
        """

        # TODO mark root node with circle
        # TODO mark end_points with shape

        # used to create a key index for flowchart ids
        # once defineed, a func name can be represented by a symbol, saving space
        node_keys = {}
        node_count = 0
        existing_base_links = set()

        shade_key = 'sh'

        # use dict to preserve order of links
        links = {}

        # guess best orientation
        if not direction:

            if len(self.graph) < 350:
                direction = 'TD'
            else:
                direction = 'LR'

        mermaid_flow = '''flowchart {direction}\n{style}\n{links}\n'''

        if shaded_nodes:
            style = '''classDef {shade_key} fill:{shade_color}'''.format(shade_key=shade_key, shade_color=shade_color)
        else:
            style = ''

        if len(self.graph) == 1:
            links[self.root] = 1
        else:

            if endpoint_only:

                endpoints = self.get_endpoints()

                if len(endpoints) > 15:
                    # switch direction to LR so that are visible
                    direction = 'LR'

                for i, end in enumerate(endpoints):

                    if shaded_nodes and end in shaded_nodes:
                        end_style_class = ':::{shade_key}'.format(shade_key=shade_key)
                    else:
                        end_style_class = ''

                    if shaded_nodes and self.root in shaded_nodes:
                        root_style_class = ':::{shade_key}'.format(shade_key=shade_key)
                    else:
                        root_style_class = ''

                    if self.root_at_end():
                        link = '{i}["{end}"]{end_style_class} --> root["{root}"]{root_style_class}'.format(
                            i=i, end=end, end_style_class=end_style_class, root=self.root, root_style_class=root_style_class)
                    else:
                        link = 'root["{root}"]{root_style_class} --> {i}["{end}"]{end_style_class}'.format(
                            i=i, end=end, end_style_class=end_style_class, root=self.root, root_style_class=root_style_class)

                    links[link] = 1

            else:

                for src in list(self.graph):

                    if shaded_nodes and src in shaded_nodes:
                        src_style_class = ':::{shade_key}'.format(shade_key=shade_key)
                    else:
                        src_style_class = ''

                    for node in list(self.graph[src]):

                        depth = node[1]
                        fname = node[0]

                        if max_display_depth and depth > max_display_depth:
                            continue

                        if shaded_nodes and fname in shaded_nodes:
                            dst_style_class = ':::{shade_key}'.format(shade_key=shade_key)
                        else:
                            dst_style_class = ''

                        # Build src --> dst link
                        # Don't add duplicate links
                        # Use short ids for func name to save space with node_keys
                        if node_keys.get(src) is None:
                            node_keys[src] = node_count
                            node_count += 1
                            src_node = '{node_key_src}["{src}"]{src_style_class}'.format(
                                node_key_src=node_keys[src], src=src, src_style_class=src_style_class)
                        else:
                            src_node = '{node_key_src}{src_style_class}'.format(
                                node_key_src=node_keys[src], src_style_class=src_style_class)

                        if node_keys.get(fname) is None:
                            node_keys[fname] = node_count
                            node_count += 1
                            dst_node = '{node_key_fname}["{fname}"]{dst_style_class}'.format(
                                node_key_fname=node_keys[fname], fname=fname, dst_style_class=dst_style_class)
                        else:
                            dst_node = '{node_key_fname}{dst_style_class}'.format(
                                node_key_fname=node_keys[fname], dst_style_class=dst_style_class)

                        # record base link
                        current_base_link = '{src} --> {node_base}'.format(src=src, node_base=node[0])

                        # don't add link if another already exists
                        if not current_base_link in existing_base_links:
                            link = '{src_node} --> {dst_node}'.format(src_node=src_node, dst_node=dst_node)
                            links[link] = 1
                            existing_base_links.add(current_base_link)
                        # else:
                        #     print('Duplicate base link found!')

        mermaid_chart = mermaid_flow.format(links='\n'.join(links.keys()), direction=direction, style=style)

        if wrap_mermaid:
            mermaid_chart = _wrap_mermaid(mermaid_chart)

        return mermaid_chart

    def gen_mermaid_mind_map(self, max_display_depth=None, wrap_mermaid=False):
        """
        Generate MermaidJS mindmap from self.graph
        See https://mermaid.js.org/syntax/mindmap.html
        """

        rows = []

        mermaid_mind = '''mindmap\nroot(({root}))\n{rows}\n'''

        destinations = []

        for src in list(self.graph):
            dst = self.graph[src]
            for d in dst:
                destinations.append(d)

        last_depth = 0
        current_level_names = []
        for i, row in enumerate(sorted(destinations, key=lambda x: x[2])):
            depth = row[1]

            # skip root row
            if depth < 2 or max_display_depth and depth > max_display_depth:
                continue

            if depth < last_depth:
                # reset level names
                current_level_names = []

            if not row[0] in current_level_names:
                spaces = (depth+1)*'  '
                rows.append("{spaces}{row_base}".format(spaces=spaces, row_base=row[0]))
                last_depth = depth
                current_level_names.append(row[0])

        mermaid_chart = mermaid_mind.format(rows='\n'.join(rows), root=self.root)

        if wrap_mermaid:
            mermaid_chart = _wrap_mermaid(mermaid_chart)

        return mermaid_chart


def get_calling_funcs_memo(f):
    return list(f.getCallingFunctions(None))


def get_called_funcs_memo(f):
    return list(f.getCalledFunctions(None))


# Recursively calling to build calling graph
def get_calling(f, cgraph=CallGraph(), depth=0, visited=None, verbose=False, include_ns=True, start_time=None, max_run_time=None, max_depth=MAX_DEPTH):
    """
    Build a call graph of all calling functions
    Traverses depth first
    """

    if f == None:
        return None

    if depth == 0:
        if verbose:
            print("root({name})".format(name=f.getName(include_ns)))
        cgraph.set_root(f.getName(include_ns))
        visited = tuple()
        start_time = time.time()

    if depth > MAX_DEPTH:
        cgraph.add_edge(f.getName(include_ns), 'MAX_DEPTH_HIT - {depth}'.format(depth=depth), depth)
        return cgraph

    if max_run_time and (time.time() - start_time) > float(max_run_time):
        raise TimeoutError('time expired for {name}'.format(name=name))

    space = (depth+2)*'  '

    # loop check
    if f.getName(True) in visited:

        # calling loop
        if verbose:
            print("{space} - LOOOOP {name}".format(space=space, name=f.getName(include_ns)))

        return cgraph

    calling = get_calling_funcs_memo(f)

    visited = visited + tuple([f.getName(True)])

    if len(calling) > 0:

        depth = depth+1

        for c in calling:

            if verbose:
                print("{space} - {name}".format(space=space, name=c.getName(include_ns)))

            # Add calling edge
            cgraph.add_edge(c.getName(include_ns), f.getName(include_ns), depth)

            # Parse further functions
            cgraph = get_calling(c, cgraph, depth, visited=visited, start_time=start_time, max_run_time=max_run_time)
    else:
        if verbose:
            print('{space} - END for {name}'.format(space=space, name=f.name))

    return cgraph


def func_is_external(f):
    # sometimwa f.exExternal() failes (like with ls binary)
    return (f.isExternal() or "<EXTERNAL>" in f.getName(True))

# Recursively calling to build called graph


def get_called(f, cgraph=CallGraph(), depth=0, visited=None, verbose=False, include_ns=True, start_time=None, max_run_time=None, max_depth=MAX_DEPTH):
    """
    Build a call graph of all called functions
    Traverses depth first
    """

    if f == None:
        return None

    if depth == 0:
        if verbose:
            print("root({name})".format(name=f.getName(include_ns)))
        cgraph.set_root(f.getName(include_ns))
        visited = tuple()
        start_time = time.time()

    if depth > max_depth:
        cgraph.add_edge(f.getName(include_ns), 'MAX_DEPTH_HIT - {depth}'.format(depth=depth), depth)
        return cgraph

    if max_run_time and (time.time() - start_time) > float(max_run_time):
        raise TimeoutError('time expired for {name}'.format(name=name))

    space = (depth+2)*'  '

    # loop check
    if f.getName(True) in visited:

        # calling loop
        if verbose:
            print("{space} - LOOOOP {name}".format(space=space, name=f.getName(include_ns)))

        return cgraph

    visited = visited + tuple([f.getName(True)])

    called = get_called_funcs_memo(f)

    if len(called) > 0:

        # this check handles special case when get_called(f) is external but returns called func of itself
        # in that case ignore it
        if not (func_is_external(f) and len(called) == 1):

            depth = depth+1

            for c in called:

                if verbose:
                    print("{space} - {name}".format(space=space, name=c.getName(include_ns)))

                # Add called edge
                if func_is_external(c):

                    # force external to show namespace lib with sendind param True
                    cgraph.add_edge(f.getName(include_ns), "{name}".format(name=c.getName(True)), depth)

                else:
                    cgraph.add_edge(f.getName(include_ns), c.getName(include_ns), depth)

                    # Parse further functions
                    cgraph = get_called(c, cgraph, depth, visited=visited,
                                        start_time=start_time, max_run_time=max_run_time)

    else:
        if verbose:
            print('{space} - END for {name}'.format(space=space, name=f.name))

    return cgraph


def _wrap_mermaid(text):
    return '''```mermaid\n{name}\n```'''.format(name=text)


def gen_mermaid_url(graph, edit=False):
    """
    Generate valid mermaid live edit and image links
    # based on serialize func  https://github.com/mermaid-js/mermaid-live-editor/blob/b5978e6faf7635e39452855fb4d062d1452ab71b/src/lib/util/serde.ts#L19-L24
    """

    mm_json = {'code': graph, 'mermaid': {'theme': 'dark'}, 'updateEditor': True,
               'autoSync': True, 'updateDiagram': True, "editorMode": "code", "panZoom": True}
    base64_string = base64.urlsafe_b64encode(zlib.compress(json.dumps(mm_json).encode('utf-8'), 9)).decode('ascii')

    if edit:
        url = 'https://mermaid.live/edit#pako:{base64_string}'.format(base64_string=base64_string)
    else:
        url = 'https://mermaid.ink/img/svg/pako:{base64_string}'.format(base64_string=base64_string)

    return url


try:
    current_address = currentLocation.getFunctionEntryPoint()
except:
    current_address = currentLocation.getFunctionAddress()

func = currentProgram.getFunctionManager().getFunctionAt(current_address)

print(func)

calling_graph = get_calling(func)
called_graph = get_called(func)

calling_flow = calling_graph.gen_mermaid_flow_graph(shaded_nodes=calling_graph.get_endpoints(), wrap_mermaid=True)
calling_flow_ends = calling_graph.gen_mermaid_flow_graph(
    shaded_nodes=calling_graph.get_endpoints(), wrap_mermaid=True, endpoint_only=True)
called_flow = called_graph.gen_mermaid_flow_graph(shaded_nodes=called_graph.get_endpoints(), wrap_mermaid=True)
called_flow_ends = called_graph.gen_mermaid_flow_graph(
    shaded_nodes=called_graph.get_endpoints(), wrap_mermaid=True, endpoint_only=True)


print(calling_flow)
print(calling_flow_ends)


charts = [['calling', calling_flow], ['calling_ends', calling_flow_ends],
          ['called', called_flow], ['called_ends', called_flow_ends]]

for chart_type, chart_data in charts:

    file_name = '{}-{}-{}.md'.format(chart_type, func.getName(False), func.getEntryPoint())
    temp_dir = tempfile.gettempdir()
    file_path = str(os.path.join(temp_dir, file_name))

    with open(file_path, 'wb') as f:
        f.write(chart_data)

    print(file_path)

    # open callgraph with vscode
    subprocess.call(['code', file_path], shell=True)
