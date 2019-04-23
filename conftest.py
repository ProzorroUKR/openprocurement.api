import pytest
from collections import OrderedDict

from _pytest.runner import CollectReport
from py.log import Producer
from xdist.newhooks import pytest_xdist_make_scheduler as xdiast_pytest_xdist_make_scheduler
from xdist.report import report_collection_diff
from xdist.workermanage import parse_spec_config
from execnet.xspec import XSpec


class EachPoolLoadScopScheduling(object):
    def __init__(self, config, log=None):
        self.xspecs = []
        self.numnodes = OrderedDict()

        for xspecstr in parse_spec_config(config):
            xspec = XSpec(xspecstr)
            self.xspecs.append(xspec)
            if not hasattr(xspec, 'id') or not hasattr(xspec, 'pool'):
                raise AttributeError("XSpec's should contain id and pool")
            if xspec.pool not in self.numnodes:
                self.numnodes[xspec.pool] = 1
            else:
                self.numnodes[xspec.pool] += 1

        self.collection = OrderedDict()
        self.workqueues = OrderedDict()
        self.assigned_works = OrderedDict()
        self.registered_collections = OrderedDict()

        for pool_name in self.numnodes.keys():
            self.collection[pool_name] = None
            self.workqueues[pool_name] = OrderedDict()
            self.assigned_works[pool_name] = OrderedDict()
            self.registered_collections[pool_name] = OrderedDict()

        if log is None:
            self.log = Producer("loadscopesched")
        else:
            self.log = log.loadscopesched

        self.config = config

    def get_pool_name(self, node):
        for xspec in self.xspecs:
            if xspec.id == node.gateway.id:
                return xspec.pool

    @property
    def nodes(self):
        """A list of all active nodes in the scheduler."""
        nodes = []

        for assigned_works in self.assigned_works.values():
            nodes.extend(assigned_works.keys())

        return nodes

    @property
    def collection_is_completed(self):
        """Boolean indication initial test collection is complete.

        This is a boolean indicating all initial participating nodes have
        finished collection.  The required number of initial nodes is defined
        by ``.numnodes``.
        """
        return sum(len(collection) for collection in self.registered_collections.values()) >= sum(self.numnodes.values())

    @property
    def tests_finished(self):
        """Return True if all tests have been executed by the nodes."""
        if not self.collection_is_completed:
            return False

        for workqueue in self.workqueues.values():
            if workqueue:
                return False

        for assigned_work in self.assigned_works.values():
            for assigned_unit in assigned_work.values():
                if self._pending_of(assigned_unit) >= 2:
                    return False

        return True

    @property
    def has_pending(self):
        """Return True if there are pending test items.

        This indicates that collection has finished and nodes are still
        processing test items, so this can be thought of as
        "the scheduler is active".
        """

        for workqueue in self.workqueues.values():
            if workqueue:
                return True

        for assigned_work in self.assigned_works.values():
            for assigned_unit in assigned_work.values():
                if self._pending_of(assigned_unit) > 0:
                    return True

        return False

    def add_node(self, node):
        """Add a new node to the scheduler.

        From now on the node will be assigned work units to be executed.

        Called by the ``DSession.worker_workerready`` hook when it successfully
        bootstraps a new node.
        """
        assert node not in self.assigned_works[self.get_pool_name(node)]
        self.assigned_works[self.get_pool_name(node)][node] = OrderedDict()

    def remove_node(self, node):
        """Remove a node from the scheduler.

        This should be called either when the node crashed or at shutdown time.
        In the former case any pending items assigned to the node will be
        re-scheduled.

        Called by the hooks:

        - ``DSession.worker_workerfinished``.
        - ``DSession.worker_errordown``.

        Return the item being executed while the node crashed or None if the
        node has no more pending items.
        """
        workload = self.assigned_works[self.get_pool_name(node)].pop(node)
        if not self._pending_of(workload):
            return None

        # The node crashed, identify test that crashed
        for work_unit in workload.values():
            for nodeid, completed in work_unit.items():
                if not completed:
                    crashitem = nodeid
                    break
            else:
                continue
            break
        else:
            raise RuntimeError(
                "Unable to identify crashitem on a workload with pending items"
            )

        # Made uncompleted work unit available again
        self.workqueues[self.get_pool_name(node)].update(workload)

        for node in self.assigned_works[self.get_pool_name(node)]:
            self._reschedule(node)

        return crashitem

    def add_node_collection(self, node, collection):
        """Add the collected test items from a node.

        The collection is stored in the ``.registered_collections`` dictionary.

        Called by the hook:

        - ``DSession.worker_collectionfinish``.
        """

        # Check that add_node() was called on the node before
        assert node in self.assigned_works[self.get_pool_name(node)]

        # A new node has been added later, perhaps an original one died.
        if self.collection_is_completed:

            # Assert that .schedule() should have been called by now
            assert self.collection[self.get_pool_name(node)]

            # Check that the new collection matches the official collection
            if collection != self.collection[self.get_pool_name(node)]:

                other_node = next(iter(self.registered_collections[self.get_pool_name(node)].keys()))

                msg = report_collection_diff(
                    self.collection[self.get_pool_name(node)], collection, other_node.gateway.id, node.gateway.id
                )
                self.log(msg)
                return

        self.registered_collections[self.get_pool_name(node)][node] = list(collection)

    def mark_test_complete(self, node, item_index, duration=0):
        """Mark test item as completed by node.

        Called by the hook:

        - ``DSession.worker_testreport``.
        """
        nodeid = self.registered_collections[self.get_pool_name(node)][node][item_index]
        scope = self._split_scope(nodeid)

        self.assigned_works[self.get_pool_name(node)][node][scope][nodeid] = True
        self._reschedule(node)

    def _assign_work_unit(self, node):
        """Assign a work unit to a node."""
        assert self.workqueues[self.get_pool_name(node)]

        # Grab a unit of work
        scope, work_unit = self.workqueues[self.get_pool_name(node)].popitem(last=False)

        # Keep track of the assigned work
        assigned_to_node = self.assigned_works[self.get_pool_name(node)].setdefault(node, default=OrderedDict())
        assigned_to_node[scope] = work_unit

        # Ask the node to execute the workload
        worker_collection = self.registered_collections[self.get_pool_name(node)][node]
        nodeids_indexes = [
            worker_collection.index(nodeid)
            for nodeid, completed in work_unit.items()
            if not completed
        ]

        node.send_runtest_some(nodeids_indexes)

    def _split_scope(self, nodeid):
        """Determine the scope (grouping) of a nodeid.

        There are usually 3 cases for a nodeid::

            example/loadsuite/test/test_beta.py::test_beta0
            example/loadsuite/test/test_delta.py::Delta1::test_delta0
            example/loadsuite/epsilon/__init__.py::epsilon.epsilon

        #. Function in a test module.
        #. Method of a class in a test module.
        #. Doctest in a function in a package.

        This function will group tests with the scope determined by splitting
        the first ``::`` from the right. That is, classes will be grouped in a
        single work unit, and functions from a test module will be grouped by
        their module. In the above example, scopes will be::

            example/loadsuite/test/test_beta.py
            example/loadsuite/test/test_delta.py::Delta1
            example/loadsuite/epsilon/__init__.py
        """
        return nodeid.rsplit("::", 1)[0]

    def _pending_of(self, workload):
        """Return the number of pending tests in a workload."""
        pending = sum(list(scope.values()).count(False) for scope in workload.values())
        return pending

    def _reschedule(self, node):
        """Maybe schedule new items on the node.

        If there are any globally pending work units left then this will check
        if the given node should be given any more tests.
        """

        # Do not add more work to a node shutting down
        if node.shutting_down:
            return

        # Check that more work is available
        if not self.workqueues[self.get_pool_name(node)]:
            node.shutdown()
            return

        self.log("Number of units waiting for node:", len(self.workqueues[self.get_pool_name(node)]))

        # Check that the node is almost depleted of work
        # 2: Heuristic of minimum tests to enqueue more work
        if self._pending_of(self.assigned_works[self.get_pool_name(node)][node]) > 2:
            return

        # Pop one unit of work and assign it
        self._assign_work_unit(node)

    def schedule(self):
        """Initiate distribution of the test collection.

        Initiate scheduling of the items across the nodes.  If this gets called
        again later it behaves the same as calling ``._reschedule()`` on all
        nodes so that newly added nodes will start to be used.

        If ``.collection_is_completed`` is True, this is called by the hook:

        - ``DSession.worker_collectionfinish``.
        """
        assert self.collection_is_completed

        # Initial distribution already happened, reschedule on all nodes
        for pool_name in self.numnodes.keys():
            if self.collection[pool_name] is not None:
                for node in self.get_pool_nodes(pool_name):
                    self._reschedule(node)
            else:
                break
        else:
            return

        # Check that all nodes collected the same tests
        if not self._check_nodes_have_same_collection():
            self.log("**Different tests collected, aborting run**")
            return

        # Collections are identical, create the final list of items
        for pool_name in self.numnodes.keys():
            self.collection[pool_name] = list(next(iter(self.registered_collections[pool_name].values())))
            if not self.collection[pool_name]:
                return

        # Determine chunks of work (scopes)
        for pool_name in self.numnodes.keys():
            for nodeid in self.collection[pool_name]:
                scope = self._split_scope(nodeid)
                work_unit = self.workqueues[pool_name].setdefault(scope, default=OrderedDict())
                work_unit[nodeid] = False

            # Avoid having more workers than work
            extra_nodes = len(self.get_pool_nodes(pool_name)) - len(self.workqueues[pool_name])

            if extra_nodes > 0:
                self.log("Shuting down {0} nodes".format(extra_nodes))

                for _ in range(extra_nodes):
                    unused_node, assigned = self.assigned_works[pool_name].popitem(last=True)

                    self.log("Shuting down unused node {0}".format(unused_node))
                    unused_node.shutdown()

            # Assign initial workload
            for node in self.get_pool_nodes(pool_name):
                self._assign_work_unit(node)

            # Ensure nodes start with at least two work units if possible (#277)
            for node in self.get_pool_nodes(pool_name):
                self._reschedule(node)

            # Initial distribution sent all tests, start node shutdown
            if not self.workqueues[pool_name]:
                for node in self.get_pool_nodes(pool_name):
                    node.shutdown()

    def get_pool_nodes(self, name):
        return [node for node in self.nodes if self.get_pool_name(node) == name]

    def _check_nodes_have_same_collection(self):
        """Return True if all nodes have collected the same items.

        If collections differ, this method returns False while logging
        the collection differences and posting collection errors to
        pytest_collectreport hook.
        """
        same_collection_list = []

        for pool_name in self.numnodes.keys():

            node_collection_items = list(self.registered_collections[pool_name].items())
            first_node, col = node_collection_items[0]
            same_collection = True

            for node, collection in node_collection_items[1:]:
                msg = report_collection_diff(
                    col, collection, first_node.gateway.id, node.gateway.id
                )
                if not msg:
                    continue

                same_collection = False
                self.log(msg)

                if self.config is None:
                    continue

                rep = CollectReport(node.gateway.id, "failed", longrepr=msg, result=[])
                self.config.hook.pytest_collectreport(report=rep)

            same_collection_list.append(same_collection)

        return all(same_collection_list)


@pytest.hookimpl()
def pytest_xdist_make_scheduler(log, config):

    for xspecstr in parse_spec_config(config):
        xspec = XSpec(xspecstr)
        has_id = hasattr(xspec, 'id')
        has_pool = hasattr(xspec, 'pool')

        if not has_id or not has_pool:
            return xdiast_pytest_xdist_make_scheduler(config, log)

    if config.getvalue("dist") == 'each':
        return EachPoolLoadScopScheduling(config, log)
