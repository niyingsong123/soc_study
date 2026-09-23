#!/usr/bin/env python3
"""Executable checks for the original reference design in switch_detailed_guide.md.

Standard library only; not a NoC simulator, production RTL, CHI model, or UCIe
compliance test. Run: python3 reference_checks.py
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from math import ceil
import random
import struct
import unittest

FIELDS = [
    ("dst", 120, 8), ("src", 112, 8), ("txn", 100, 12),
    ("opcode", 96, 4), ("qos", 92, 4), ("length_minus1", 84, 8),
    ("attrs", 80, 4), ("addr", 32, 48), ("context", 16, 16),
    ("epoch", 8, 8), ("status", 0, 8),
]


def pack_head(**values: int) -> int:
    known = {name for name, _, _ in FIELDS}
    if set(values) - known:
        raise ValueError("Unknown header field")
    result = 0
    for name, shift, width in FIELDS:
        value = values.get(name, 0)
        if not 0 <= value < (1 << width):
            raise ValueError(f"{name}: value outside {width}-bit range")
        result |= value << shift
    return result


def unpack_head(head: int) -> dict[str, int]:
    if not 0 <= head < (1 << 128):
        raise ValueError("Header must be 128 bits")
    return {name: (head >> shift) & ((1 << width) - 1)
            for name, shift, width in FIELDS}


def rr_pick(requests: list[bool], start: int) -> int | None:
    if not requests or not 0 <= start < len(requests):
        raise ValueError("Invalid RR request vector / pointer")
    for offset in range(len(requests)):
        candidate = (start + offset) % len(requests)
        if requests[candidate]:
            return candidate
    return None


def sa_allocate(routes: list[list[int | None]], in_ptr: list[int],
                out_ptr: list[int]) -> list[tuple[int, int, int]]:
    """One eligible VC nomination per input, then one winner per output.

    routes[i][v] is the eligible VC's output, or None. Returns (input,VC,output).
    Updates pointers only for grants considered irrevocably consumed here.
    """
    nominations: list[tuple[int, int] | None] = []
    for i, vcs in enumerate(routes):
        v = rr_pick([o is not None for o in vcs], in_ptr[i])
        nominations.append(None if v is None else (v, int(vcs[v])))
    grants = []
    for o in range(len(out_ptr)):
        i = rr_pick([n is not None and n[1] == o for n in nominations],
                    out_ptr[o])
        if i is not None:
            v = nominations[i][0]  # type: ignore[index]
            grants.append((i, v, o))
            in_ptr[i] = (v + 1) % len(routes[i])
            out_ptr[o] = (i + 1) % len(routes)
    return grants


def credit_trial(seed: int, depth: int = 8, cycles: int = 2000) -> None:
    """Single VC, arbitrary stalls; exactly tracks C+F+Q+R=depth.

    F includes forward pipeline reservations. Credits return only after dequeue.
    This test checks resource accounting, not the complete router timing model.
    """
    rng = random.Random(seed)
    credit = depth
    forward: list[tuple[int, int]] = []
    receiver: deque[int] = deque()
    reverse: list[int] = []
    sent = received = 0
    for t in range(cycles + 100):
        credit += sum(due == t for due in reverse)
        reverse = [due for due in reverse if due != t]
        arriving = [ident for due, ident in forward if due == t]
        forward = [(due, ident) for due, ident in forward if due != t]
        receiver.extend(arriving)
        # Receive stalls stop during the drain interval.
        if receiver and (t >= cycles or rng.random() < 0.67):
            ident = receiver.popleft()
            assert ident == received, "Loss, duplication, or reorder"
            received += 1
            reverse.append(t + 3)
        if t < cycles and credit and rng.random() < 0.82:
            credit -= 1
            forward.append((t + 2, sent))
            sent += 1
        assert 0 <= credit <= depth
        assert len(receiver) <= depth
        assert credit + len(forward) + len(receiver) + len(reverse) == depth
    assert received == sent and credit == depth
    assert not forward and not reverse and not receiver


def xy_path(src: tuple[int, int], dst: tuple[int, int]) -> list[tuple]:
    x, y = src
    result = []
    while x != dst[0]:
        nx = x + (1 if dst[0] > x else -1)
        result.append(((x, y), (nx, y)))
        x = nx
    while y != dst[1]:
        ny = y + (1 if dst[1] > y else -1)
        result.append(((x, y), (x, ny)))
        y = ny
    return result


def xy_dependency_counts(size: int = 4) -> tuple[int, int, bool]:
    nodes: set[tuple] = set()
    edges: set[tuple] = set()
    coordinates = [(x, y) for x in range(size) for y in range(size)]
    for src in coordinates:
        for dst in coordinates:
            path = xy_path(src, dst)
            nodes.update(path)
            edges.update(zip(path, path[1:]))
    indegree = dict.fromkeys(nodes, 0)
    outgoing: dict[tuple, list] = defaultdict(list)
    for a, b in edges:
        outgoing[a].append(b)
        indegree[b] += 1
    ready = deque(n for n in nodes if indegree[n] == 0)
    visited = 0
    while ready:
        a = ready.popleft()
        visited += 1
        for b in outgoing[a]:
            indegree[b] -= 1
            if not indegree[b]:
                ready.append(b)
    return len(nodes), len(edges), visited == len(nodes)


def noc_arrivals(flits: int, hops: int) -> list[int]:
    """Unloaded recurrence: head 5 cycles/hop; bodies 3 and FIFO spacing.

    RC/VA apply to head; no stalls/credit exhaustion/resource competitors.
    Includes one-cycle LT per hop. Source injection is one flit per cycle.
    """
    arrivals = list(range(flits))
    for _ in range(hops):
        out = [arrivals[0] + 5]
        for t in arrivals[1:]:
            out.append(max(t + 3, out[-1] + 1))
        arrivals = out
    return arrivals


def crc32c(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF


def lrp_data(seq: int, payload: bytes, cls: int = 0, epoch: int = 1) -> bytes:
    """Original LRP-64 teaching format; NOT a UCIe frame."""
    if not 0 <= seq <= 65535 or not 0 <= cls <= 1 or len(payload) > 64:
        raise ValueError("Invalid LRP data")
    header = struct.pack("!BBHHBBHH", 0x10, cls, seq, 0, len(payload), 0, 0, epoch)
    protected = header + payload.ljust(64, b"\0")
    return protected + struct.pack("!I", crc32c(protected))


@dataclass
class LrpReceiver:
    expected: int = 0
    epoch: int = 1
    cls: int = 0
    delivered: int = 0

    def receive(self, cell: bytes) -> str:
        if len(cell) != 80 or crc32c(cell[:76]) != int.from_bytes(cell[76:], "big"):
            return "crc_error"
        vt, cls, seq, _, length, _, _, epoch = struct.unpack("!BBHHBBHH", cell[:12])
        if vt != 0x10 or cls != self.cls or length > 64 or epoch != self.epoch:
            return "format_or_epoch_error"
        delta = (seq - self.expected) & 0xFFFF
        if delta == 0:
            self.expected = (self.expected + 1) & 0xFFFF
            self.delivered += 1
            return "commit"
        return "future_nak" if delta < 0x8000 else "duplicate_ack"


class Checks(unittest.TestCase):
    def test_header_layout_and_roundtrip(self):
        mask = 0
        for _, shift, width in FIELDS:
            bits = ((1 << width) - 1) << shift
            self.assertFalse(mask & bits)
            mask |= bits
        self.assertEqual(mask, (1 << 128) - 1)
        values = dict(dst=0x12, src=0x01, txn=0xABC, opcode=2, qos=4,
                      length_minus1=255, attrs=0, addr=0x123456789AB0,
                      context=0x100, epoch=3, status=0)
        self.assertEqual(unpack_head(pack_head(**values)), values)
        with self.assertRaises(ValueError):
            pack_head(txn=4096)

    def test_rr_rotation(self):
        pointer, winners = 0, []
        for _ in range(15):
            winner = rr_pick([True] * 5, pointer)
            winners.append(winner)
            pointer = (winner + 1) % 5
        self.assertEqual(winners, list(range(5)) * 3)
        self.assertIsNone(rr_pick([False] * 5, 3))

    def test_sa_matching_random(self):
        rng = random.Random(20260924)
        ip, op = [0] * 5, [0] * 5
        for _ in range(10000):
            routes = [[rng.choice([None, 0, 1, 2, 3, 4]) for _ in range(4)]
                      for _ in range(5)]
            grants = sa_allocate(routes, ip, op)
            self.assertEqual(len({g[0] for g in grants}), len(grants))
            self.assertEqual(len({g[2] for g in grants}), len(grants))
            for i, v, o in grants:
                self.assertEqual(routes[i][v], o)

    def test_sa_not_maximum_matching(self):
        # I0 has E and N candidates; I1 has E. I0 nominates E, so N stays idle.
        grants = sa_allocate([[0, 1], [0, None]], [0, 0], [1, 0])
        self.assertEqual(grants, [(1, 0, 0)])
        self.assertEqual(len({(0, 1), (1, 0)}), 2)  # feasible two-edge matching

    def test_credit_conservation(self):
        for seed in range(100):
            credit_trial(seed)

    def test_credit_is_not_vc_ownership(self):
        depth, credits, busy = 8, 8, True
        credits -= 1  # send the head of a longer packet
        credits += 1  # downstream consumes head; NOT tail, no free indication
        self.assertEqual(credits, depth)
        self.assertTrue(busy)  # cannot assign this VC to a different packet
        credits -= 1  # tail later departs
        credits += 1  # its returned credit carries FREE
        busy = False
        self.assertFalse(busy)

    def test_xy_dependency_graph(self):
        nodes, edges, acyclic = xy_dependency_counts()
        self.assertEqual(nodes, 48)
        self.assertGreater(edges, 0)
        self.assertTrue(acyclic)

    def test_pipeline_and_budget(self):
        times = noc_arrivals(17, 3)
        self.assertEqual((times[0], times[-1]), (15, 31))
        fixed_ns = 2 + 15 + 4 + 8 + 15 + 2
        request_ns = fixed_ns + ceil(24 / 64) * 80 / 32
        response_ns = fixed_ns + 2 * 16 + ceil(280 / 64) * 80 / 32
        rtt_ns = request_ns + 80 + response_ns
        self.assertEqual((request_ns, response_ns, rtt_ns), (48.5, 90.5, 219.0))
        self.assertEqual(ceil(12 * rtt_ns / 256), 11)
        self.assertEqual(5 * 4 * 8 * 130 // 8, 2600)

    def test_lrp_crc_replay_and_wrap(self):
        self.assertEqual(crc32c(b"123456789"), 0xE3069283)
        rx = LrpReceiver()
        c0, c1, c2 = (lrp_data(i, b"payload") for i in range(3))
        self.assertEqual(rx.receive(c0), "commit")
        self.assertEqual(rx.receive(c0), "duplicate_ack")
        bad = bytearray(c1)
        bad[13] ^= 1
        self.assertEqual(rx.receive(bytes(bad)), "crc_error")
        self.assertEqual(rx.receive(c2), "future_nak")
        self.assertEqual(rx.receive(c1), "commit")
        self.assertEqual(rx.receive(c2), "commit")
        self.assertEqual(rx.delivered, 3)
        rx = LrpReceiver(expected=65535)
        self.assertEqual(rx.receive(lrp_data(65535, b"a")), "commit")
        self.assertEqual(rx.receive(lrp_data(0, b"b")), "commit")
        self.assertEqual(rx.receive(lrp_data(65535, b"a")), "duplicate_ack")
        self.assertEqual(rx.receive(lrp_data(1, b"c", epoch=2)), "format_or_epoch_error")


if __name__ == "__main__":
    print("Scope: algebra / small reference algorithms, NOT complete RTL verification.")
    print("4x4 XY channel dependency graph:", xy_dependency_counts())
    print("17-flit / 3-hop arrival cycles:", noc_arrivals(17, 3))
    unittest.main(verbosity=2)
