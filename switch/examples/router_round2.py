#!/usr/bin/env python3
"""Round-2 original teaching model: finite-buffer mesh and local checks.

NOT RTL, gem5, BookSim, UCIe, CHI, or a proof of general deadlock freedom.
A step reads old state, plans RC/VA/SA, then commits; same-edge arrivals and
credits cannot be used by that step. Source NI uses an ideal ready/valid
injection interface. All router-to-router and router-to-sink links use credits.
Run: python3 router_round2.py [--report result.json]
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
import itertools
import json
from pathlib import Path
import random
import unittest

E, W, N, S, L = range(5)
DELTA = {E: (1, 0), W: (-1, 0), N: (0, 1), S: (0, -1)}
OPPOSITE = {E: W, W: E, N: S, S: N}


def rr(requests: list[bool], pointer: int) -> int | None:
    if not requests or not 0 <= pointer < len(requests):
        raise ValueError("Invalid RR vector or pointer")
    return next((k for d in range(len(requests))
                 if requests[k := (pointer + d) % len(requests)]), None)


def input_first(routes: list[list[int | None]], ip: list[int], op: list[int]):
    """Pure evaluation: grants are (input, VC, output); no state is changed."""
    nominations = []
    for i, row in enumerate(routes):
        v = rr([o is not None for o in row], ip[i])
        nominations.append(None if v is None else (v, row[v]))
    grants = []
    for o in range(len(op)):
        i = rr([n is not None and n[1] == o for n in nominations], op[o])
        if i is not None:
            grants.append((i, nominations[i][0], o))
    return grants


def islip(matrix: list[list[bool]], accept: list[int], grant: list[int],
          iterations: int) -> list[tuple[int, int]]:
    """Original request/grant/accept policy, without NoC credit integration.

    Each returned match is assumed consumed. Pointer updates are for accepted
    matches in iteration zero ONLY. It need not produce a maximum matching.
    """
    ni, no = len(matrix), len(grant)
    used_i, used_o = set(), set()
    matches = []
    for iteration in range(iterations):
        offered = {}
        for o in range(no):
            if o in used_o:
                continue
            i = rr([i not in used_i and matrix[i][o] for i in range(ni)], grant[o])
            if i is not None:
                offered[o] = i
        chosen = []
        for i in range(ni):
            if i not in used_i:
                o = rr([offered.get(o) == i for o in range(no)], accept[i])
                if o is not None:
                    chosen.append((i, o))
        for i, o in chosen:
            used_i.add(i)
            used_o.add(o)
            matches.append((i, o))
            if iteration == 0:
                accept[i], grant[o] = (o + 1) % no, (i + 1) % ni
        if not chosen:
            break
    return matches


@dataclass(frozen=True)
class Packet:
    ident: int
    src: tuple[int, int]
    dst: tuple[int, int]
    vn: int
    length: int


@dataclass(frozen=True)
class Flit:
    packet: Packet
    index: int

    @property
    def head(self):
        return self.index == 0

    @property
    def tail(self):
        return self.index == self.packet.length - 1


@dataclass
class InputVC:
    q: deque = field(default_factory=deque)
    state: str = "IDLE"
    packet: int = -1
    generation: int = 0
    route: int = -1
    outvc: int = -1


@dataclass
class OutputVC:
    credit: int
    owner: tuple[int, int, int, int] | None = None  # input, VC, generation, packet
    draining: bool = False


class Mesh:
    """R0-like mesh, no speculative bypass, no clock-domain crossings.

    Head: capture edge 0, RC1, VA2, SA3, next capture5. Bodies inherit route.
    Forward delay=2 includes ST+LT. Reverse delay is configurable (>=1).
    One source flit/node/edge, one sink pop/node/edge. Four VCs, two per VN.
    """
    vcs = 4

    def __init__(self, width=2, height=2, depth=8, reverse_delay=1,
                 seed=0, sink_probability=1.0, sink_block_until=0, source_gap=1):
        if min(width, height, depth, reverse_delay, source_gap) < 1:
            raise ValueError("Dimensions, depth and delays must be positive")
        if not 0 < sink_probability <= 1:
            raise ValueError("Sink probability must be in (0,1]")
        self.width, self.height, self.depth = width, height, depth
        self.reverse_delay, self.gap = reverse_delay, source_gap
        self.prob, self.block_until = sink_probability, sink_block_until
        self.rng = random.Random(seed)
        self.nodes = list(itertools.product(range(width), range(height)))
        self.inputs = {n: [[InputVC() for _ in range(4)] for _ in range(5)]
                       for n in self.nodes}
        self.outputs = {}
        self.dest = {}
        self.upstream = {}
        for n in self.nodes:
            for o in range(5):
                if o == L:
                    self.dest[n, o] = (n, L)
                else:
                    dx, dy = DELTA[o]
                    neighbor = (n[0] + dx, n[1] + dy)
                    if neighbor not in self.inputs:
                        continue
                    self.dest[n, o] = (neighbor, OPPOSITE[o])
                    self.upstream[neighbor, OPPOSITE[o]] = (n, o)
                self.outputs[n, o] = [OutputVC(depth) for _ in range(4)]
        self.sinks = {n: [deque() for _ in range(4)] for n in self.nodes}
        self.ip = {n: [0] * 5 for n in self.nodes}
        self.op = {n: [0] * 5 for n in self.nodes}
        self.vap = {k: [0] * 4 for k in self.outputs}
        self.sink_pointer = dict.fromkeys(self.nodes, 0)
        self.pending = {n: deque() for n in self.nodes}
        self.source_active = dict.fromkeys(self.nodes, None)
        self.forward = defaultdict(list)  # edge -> (link, outvc, immutable flit)
        self.reverse = defaultdict(list)  # edge -> (link, outvc, free, packet)
        self.packets = {}
        self.expected = Counter()
        self.arrivals = defaultdict(list)
        self.completions = {}
        self.trace = []
        self.stats = Counter()
        self.t = 0

    def add(self, packet: Packet):
        if (packet.ident in self.packets or packet.src not in self.inputs
                or packet.dst not in self.inputs or packet.vn not in (0, 1)
                or packet.length < 1):
            raise ValueError("Invalid or duplicate packet")
        self.packets[packet.ident] = packet
        self.pending[packet.src].append(packet)

    @staticmethod
    def route(node, dst):
        if dst[0] != node[0]:
            return E if dst[0] > node[0] else W
        if dst[1] != node[1]:
            return N if dst[1] > node[1] else S
        return L

    def note(self, event, **info):
        # Keep short traces for review; assertions run throughout the simulation.
        if len(self.trace) < 400:
            self.trace.append(dict(edge=self.t, event=event, **info))

    def receive(self, node, port, v, flit):
        q = self.inputs[node][port][v]
        assert len(q.q) < self.depth
        assert v // 2 == flit.packet.vn
        if flit.head:
            assert q.state == "IDLE" and not q.q
            q.state, q.packet = "RC", flit.packet.ident
            q.generation += 1
            q.route = q.outvc = -1
        else:
            assert q.state != "IDLE" and q.packet == flit.packet.ident
        q.q.append(flit)

    def return_credit(self, key, v, flit):
        self.reverse[self.t + self.reverse_delay].append(
            (key, v, flit.tail, flit.packet.ident))

    def step(self):
        # All decisions in this section see pre-edge state.
        rc_jobs, va_requests, sa_jobs = [], defaultdict(list), []
        injections, sink_jobs = [], []
        for n in self.nodes:
            for i, rows in enumerate(self.inputs[n]):
                for v, q in enumerate(rows):
                    if q.state == "RC":
                        rc_jobs.append((n, i, v, self.route(n, self.packets[q.packet].dst)))
                    elif q.state == "WAIT_VA":
                        allowed = range(2 * self.packets[q.packet].vn,
                                        2 * self.packets[q.packet].vn + 2)
                        free = [w for w in allowed if self.outputs[n, q.route][w].owner is None]
                        if free:
                            # Alternate candidates; per-output-VC RR resolves competition.
                            w = free[(q.generation + i + v) % len(free)]
                            va_requests[(n, q.route, w)].append((i, v))
            routes = [[None] * 4 for _ in range(5)]
            for i, rows in enumerate(self.inputs[n]):
                for v, q in enumerate(rows):
                    if q.state == "ACTIVE" and q.q:
                        ov = self.outputs[n, q.route][q.outvc]
                        if ov.credit > 0:
                            routes[i][v] = q.route
                        else:
                            self.stats["vc_credit_stall_observations"] += 1
                    if q.state == "ACTIVE" and not q.q:
                        self.stats["empty_but_owned_observations"] += 1
            sa_jobs.extend((n, i, v, o) for i, v, o in
                           input_first(routes, self.ip[n], self.op[n]))
            if self.t >= self.block_until and self.rng.random() < self.prob:
                v = rr([bool(q) for q in self.sinks[n]], self.sink_pointer[n])
                if v is not None:
                    sink_jobs.append((n, v))
            if self.t % self.gap == 0:
                active = self.source_active[n]
                if active is None and self.pending[n]:
                    p = self.pending[n][0]
                    candidates = [v for v in range(p.vn * 2, p.vn * 2 + 2)
                                  if self.inputs[n][L][v].state == "IDLE"]
                    if candidates:
                        injections.append((n, candidates[0], p, 0))
                elif active is not None:
                    p, v, index = active
                    if len(self.inputs[n][L][v].q) < self.depth:
                        injections.append((n, v, p, index))
        va_jobs = []
        for (n, o, w), applicants in va_requests.items():
            choices = {i * 4 + v: (i, v) for i, v in applicants}
            winner = rr([a in choices for a in range(20)], self.vap[n, o][w])
            i, v = choices[winner]
            va_jobs.append((n, i, v, o, w))
        # Irrevocable commits; no subsequent evaluator reads these changes this edge.
        for n, v in sink_jobs:
            flit = self.sinks[n][v].popleft()
            assert self.expected[flit.packet.ident] == flit.index
            self.expected[flit.packet.ident] += 1
            self.stats["delivered_flits"] += 1
            self.sink_pointer[n] = (v + 1) % 4
            self.return_credit((n, L), v, flit)
            if flit.tail:
                assert flit.packet.ident not in self.completions
                self.completions[flit.packet.ident] = self.t
        for n, i, v, o in sa_jobs:
            q = self.inputs[n][i][v]
            w, generation = q.outvc, q.generation
            ov = self.outputs[n, o][w]
            assert ov.owner == (i, v, generation, q.packet)
            assert ov.credit > 0 and not ov.draining
            flit = q.q.popleft()
            ov.credit -= 1
            self.forward[self.t + 2].append(((n, o), w, flit))
            self.ip[n][i], self.op[n][o] = (v + 1) % 4, (i + 1) % 5
            self.stats["sa_commits"] += 1
            self.note("SA", node=n, input=i, vc=v, output=o,
                      outvc=w, packet=flit.packet.ident, flit=flit.index)
            if i != L:
                self.return_credit(self.upstream[n, i], v, flit)
            if flit.tail:
                assert not q.q
                q.state, q.packet, q.route, q.outvc = "IDLE", -1, -1, -1
                ov.draining = True
        for n, i, v, o in rc_jobs:
            q = self.inputs[n][i][v]
            q.route, q.state = o, "WAIT_VA"
        for n, i, v, o, w in va_jobs:
            q, ov = self.inputs[n][i][v], self.outputs[n, o][w]
            assert ov.owner is None and ov.credit == self.depth
            q.outvc, q.state = w, "ACTIVE"
            ov.owner, ov.draining = (i, v, q.generation, q.packet), False
            self.vap[n, o][w] = (i * 4 + v + 1) % 20
        for key, v, free, ident in self.reverse.pop(self.t, []):
            ov = self.outputs[key][v]
            assert ov.owner is not None and ov.owner[3] == ident
            ov.credit += 1
            if free:
                assert ov.draining and ov.credit == self.depth
                ov.owner, ov.draining = None, False
                self.stats["tail_free_returns"] += 1
        for key, v, flit in self.forward.pop(self.t, []):
            node, port = self.dest[key]
            if key[1] == L:
                assert flit.packet.dst == node
                assert len(self.sinks[node][v]) < self.depth
                self.sinks[node][v].append(flit)
                self.arrivals[flit.packet.ident].append(self.t)
            else:
                self.receive(node, port, v, flit)
        for n, v, p, index in injections:
            if index == 0:
                assert self.pending[n].popleft() == p
            self.receive(n, L, v, Flit(p, index))
            self.stats["injected_flits"] += 1
            self.source_active[n] = None if index + 1 == p.length else (p, v, index + 1)
        self.check()
        self.t += 1

    def check(self):
        f, r = Counter(), Counter()
        for events in self.forward.values():
            for key, v, _ in events:
                f[key, v] += 1
        for events in self.reverse.values():
            for key, v, _, _ in events:
                r[key, v] += 1
        for key, row in self.outputs.items():
            node, port = self.dest[key]
            for v, ov in enumerate(row):
                queue = self.sinks[node][v] if key[1] == L else self.inputs[node][port][v].q
                assert 0 <= ov.credit <= self.depth
                assert len(queue) <= self.depth
                assert ov.credit + f[key, v] + len(queue) + r[key, v] == self.depth
                if ov.owner is None:
                    assert ov.credit == self.depth and not ov.draining
        for n in self.nodes:
            for i, row in enumerate(self.inputs[n]):
                for v, q in enumerate(row):
                    assert 0 <= len(q.q) <= self.depth
                    if q.state == "IDLE":
                        assert not q.q
                    if q.state == "ACTIVE":
                        assert self.outputs[n, q.route][q.outvc].owner == (
                            i, v, q.generation, q.packet)
                    assert all(flit.packet.ident == q.packet for flit in q.q)
        self.stats["invariant_edges"] += 1

    def drained(self):
        return (len(self.completions) == len(self.packets)
                and not self.forward and not self.reverse
                and all(ov.owner is None for row in self.outputs.values() for ov in row))

    def run(self, limit=20000):
        while self.t < limit and not self.drained():
            self.step()
        if not self.drained():
            raise AssertionError(f"No drain by edge {limit}: {len(self.completions)}/{len(self.packets)}")
        assert self.stats["delivered_flits"] == sum(p.length for p in self.packets.values())
        assert self.stats["injected_flits"] == self.stats["delivered_flits"]
        return self.t


class SharedPool:
    """Separate physical storage from irrevocably promised slot tokens."""
    def __init__(self, capacity=8, vcs=2):
        self.capacity = capacity
        self.u = capacity
        self.c, self.f, self.r = [0] * vcs, [0] * vcs, [0] * vcs
        self.queues = [deque() for _ in range(vcs)]

    def promise(self, v, count):
        if not 0 <= count <= self.u:
            raise ValueError("Cannot promise already committed capacity")
        self.u -= count
        self.c[v] += count
        self.check()

    def send(self, v):
        assert self.c[v] > 0
        self.c[v] -= 1
        self.f[v] += 1
        self.check()

    def receive(self, v, value):
        assert self.f[v] > 0
        self.f[v] -= 1
        self.queues[v].append(value)
        self.check()

    def pop(self, v):
        value = self.queues[v].popleft()
        self.r[v] += 1
        self.check()
        return value

    def credit_return(self, v):
        assert self.r[v] > 0
        self.r[v] -= 1
        self.c[v] += 1
        self.check()

    def check(self):
        assert self.u + sum(self.c + self.f + self.r) + sum(map(len, self.queues)) == self.capacity
        assert min([self.u] + self.c + self.f + self.r) >= 0


class LinkedPool:
    """Per-input 1R/1W shared flit pool; pointers are explicit registers.

    One pop and one append per tick. No same-edge reuse of the just-freed slot.
    Data read returns the old item. No SRAM latency or banking is modeled.
    """
    def __init__(self, size=8, queues=4):
        self.free = set(range(size))
        self.head, self.tail = [None] * queues, [None] * queues
        self.count = [0] * queues
        self.next, self.data = [None] * size, [None] * size

    def tick(self, dequeue=None, enqueue=None):
        # Reject illegal calls before mutating state.
        if dequeue is not None and (not 0 <= dequeue < len(self.count) or not self.count[dequeue]):
            raise ValueError("Cannot pop empty/invalid queue")
        if enqueue is not None and not 0 <= enqueue[0] < len(self.count):
            raise ValueError("Invalid enqueue queue")
        # Reserve append address from OLD free set; no combinational recycle.
        address = None
        if enqueue is not None:
            if not self.free:
                raise ValueError("No old-state free slot")
            address = min(self.free)
            self.free.remove(address)
        removed, value = None, None
        if dequeue is not None:
            q = dequeue
            if not self.count[q]:
                raise ValueError("Cannot pop empty queue")
            removed, value = self.head[q], self.data[self.head[q]]
            self.head[q] = self.next[removed]
            self.count[q] -= 1
            if not self.count[q]:
                self.head[q] = self.tail[q] = None
        if enqueue is not None:
            q, item = enqueue
            self.data[address], self.next[address] = item, None
            if self.count[q]:
                self.next[self.tail[q]] = address
            else:
                self.head[q] = address
            self.tail[q] = address
            self.count[q] += 1
        if removed is not None:
            self.free.add(removed)
            self.data[removed] = self.next[removed] = None
        self.check()
        return value

    def check(self):
        used = set()
        for q, count in enumerate(self.count):
            address, last = self.head[q], None
            for _ in range(count):
                assert address is not None and address not in used and address not in self.free
                used.add(address)
                last, address = address, self.next[address]
            assert address is None and last == self.tail[q]
        assert len(used) + len(self.free) == len(self.data)


def experiment(seed, width=2, height=2, packets=96):
    rng = random.Random(seed)
    model = Mesh(width, height, depth=rng.choice([2, 4, 8]),
                 reverse_delay=rng.choice([1, 2, 4]), seed=seed,
                 sink_probability=0.61, sink_block_until=25)
    for ident in range(packets):
        model.add(Packet(ident, rng.choice(model.nodes), rng.choice(model.nodes),
                         rng.randrange(2), rng.choice([1, 2, 5, 17])))
    model.run()
    return dict(seed=seed, width=width, height=height, packets=packets,
                depth=model.depth, reverse_delay=model.reverse_delay,
                edges=model.t, **model.stats)


class Checks(unittest.TestCase):
    def test_01_rr(self):
        p, got = 0, []
        for _ in range(15):
            w = rr([True] * 5, p)
            got.append(w)
            p = (w + 1) % 5
        self.assertEqual(got, list(range(5)) * 3)
        self.assertIsNone(rr([False] * 5, 4))

    def test_02_all_three_by_three_matching_graphs(self):
        for bits in range(512):
            matrix = [[bool(bits & (1 << (i * 3 + o))) for o in range(3)] for i in range(3)]
            for pointer in range(3):
                m = islip(matrix, [pointer] * 3, [pointer] * 3, 3)
                self.assertEqual(len(m), len({i for i, _ in m}))
                self.assertEqual(len(m), len({o for _, o in m}))
                self.assertTrue(all(matrix[i][o] for i, o in m))
                # Converged result is maximal, not necessarily maximum.
                for i in set(range(3)) - {i for i, _ in m}:
                    for o in set(range(3)) - {o for _, o in m}:
                        self.assertFalse(matrix[i][o])

    def test_03_first_iteration_pointer_update(self):
        a, g = [0, 0], [0, 0]
        self.assertEqual(islip([[True] * 2 for _ in range(2)], a, g, 2), [(0, 0), (1, 1)])
        self.assertEqual((a, g), ([1, 0], [1, 0]))

    def test_04_input_first_loses_parallelism(self):
        routes = [[0, 1], [0, None]]
        self.assertEqual(input_first(routes, [0, 0], [1, 0]), [(1, 0, 0)])
        self.assertEqual(set(islip([[True, True], [True, False]], [0, 0], [1, 0], 2)),
                         {(0, 1), (1, 0)})

    def test_05_unloaded_pipeline(self):
        model = Mesh(3, 1)
        model.add(Packet(0, (0, 0), (2, 0), 0, 17))
        model.run()
        self.assertEqual(model.arrivals[0], list(range(15, 32)))
        self.assertEqual(model.completions[0], 32)  # endpoint consumes one edge later

    def test_06_short_packet_and_source_bubbles(self):
        model = Mesh(2, 1, source_gap=4)
        model.add(Packet(0, (0, 0), (1, 0), 0, 17))
        model.add(Packet(1, (0, 0), (1, 0), 0, 1))
        model.run()
        self.assertGreater(model.stats["empty_but_owned_observations"], 0)
        self.assertEqual(len(model.completions), 2)

    def test_07_credit_depth_and_return_delay(self):
        last = []
        for d, delay in [(1, 1), (8, 1), (8, 12)]:
            model = Mesh(3, 1, depth=d, reverse_delay=delay)
            model.add(Packet(0, (0, 0), (2, 0), 0, 17))
            model.run()
            last.append(model.arrivals[0][-1])
        self.assertGreater(last[0], last[1])
        self.assertGreater(last[2], last[1])

    def test_08_sink_stall_resume(self):
        model = Mesh(2, 2, depth=2, sink_block_until=100)
        for i in range(16):
            model.add(Packet(i, model.nodes[i % 4], (1, 1), i % 2, 17))
        model.run()
        self.assertGreater(model.stats["vc_credit_stall_observations"], 0)
        self.assertTrue(all(t >= 100 for t in model.completions.values()))

    def test_09_mixed_mesh_traffic(self):
        for seed in range(12):
            experiment(seed)
        for seed in range(4):
            experiment(seed + 100, 3, 3, 144)

    def test_10_credit_promise_not_physical_free(self):
        p = SharedPool(8)
        p.promise(0, 8)
        self.assertEqual(sum(map(len, p.queues)), 0)  # SRAM physically empty
        with self.assertRaises(ValueError):
            p.promise(1, 1)
        p.send(0)
        p.receive(0, "data")
        self.assertEqual(p.pop(0), "data")
        p.credit_return(0)
        self.assertEqual((p.c, p.u), ([8, 0], 0))

    def test_11_linked_pool_simultaneous_cases(self):
        pool = LinkedPool()
        pool.tick(enqueue=(0, "old"))
        self.assertEqual(pool.tick(dequeue=0, enqueue=(0, "new")), "old")
        self.assertEqual(pool.count[0], 1)
        self.assertEqual(pool.tick(dequeue=0), "new")
        rng, expected = random.Random(7), [deque() for _ in range(4)]
        for t in range(10000):
            nonempty = [q for q in range(4) if expected[q]]
            pop = rng.choice(nonempty) if nonempty and rng.random() < .7 else None
            put = (rng.randrange(4), t) if pool.free and rng.random() < .7 else None
            result = pool.tick(pop, put)
            if pop is not None:
                self.assertEqual(result, expected[pop].popleft())
            if put is not None:
                expected[put[0]].append(put[1])
            self.assertEqual(pool.count, list(map(len, expected)))

    def test_12_fault_is_detected(self):
        model = Mesh(1, 1)
        model.outputs[((0, 0), L)][0].credit += 1
        with self.assertRaises(AssertionError):
            model.check()

    def test_13_tail_generation_snapshot(self):
        model = Mesh(2, 1, depth=8, reverse_delay=8)
        for i in range(24):
            model.add(Packet(i, (0, 0), (1, 0), 0, 1))
        model.run()
        self.assertEqual(len(model.completions), 24)
        self.assertGreater(model.inputs[(0, 0)][L][0].generation, 1)

    def test_14_invalid_linked_pool_call_is_atomic(self):
        pool = LinkedPool()
        before = (pool.free.copy(), pool.count.copy())
        with self.assertRaises(ValueError):
            pool.tick(dequeue=0, enqueue=(1, "data"))
        self.assertEqual(before, (pool.free, pool.count))
        pool.check()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    if not result.wasSuccessful():
        raise SystemExit(1)
    report = dict(scope="Original synchronous finite-buffer transport model; not RTL/compliance/formal proof",
                  tests_run=result.testsRun, errors=len(result.errors), failures=len(result.failures),
                  random_runs=[experiment(s) for s in range(12)] +
                              [experiment(s + 100, 3, 3, 144) for s in range(4)])
    depths = []
    for d, delay in [(1, 1), (8, 1), (8, 12)]:
        model = Mesh(3, 1, depth=d, reverse_delay=delay)
        model.add(Packet(0, (0, 0), (2, 0), 0, 17))
        model.run()
        depths.append(dict(depth=d, reverse_delay=delay, first=model.arrivals[0][0],
                           last=model.arrivals[0][-1], drained_edge=model.t))
    report["credit_sweep"] = depths
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(tests_run=result.testsRun, credit_sweep=depths), indent=2))


if __name__ == "__main__":
    main()
