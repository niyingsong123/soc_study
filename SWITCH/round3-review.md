# SWITCH Round 3: NI Contract and Resource Review

Date: 2026-09-25. Scope: the v2.3 revision of [the existing guide](../SWITCH/switch_detailed_guide.md), authorized by U35. This is a review and handoff record, not a second technical paper or a new external-source note.

## Baseline and evidence

Before editing, the GitHub main reference and local HEAD both resolved to `8c70f1d4086d97600c0b44ed1c51c9e94aa98171`. Existing uncommitted work, including CF planning, was preserved. The second-round Router implementation and result file were not edited or rerun.

- R8: reused the existing AXI IHI 0022H note and rechecked A3.1–A3.3 handshake/stability and write-response dependencies, A3.4 burst/error termination, A4.4 memory attributes, and A6.5–A6.6 observation/ordering. Relevant locations include PDF pages 40–46, 48, 60, 69–70 and 88–89 (one-based PDF pages). The previous A5 reading remains the write-data-ordering reference; this round does not claim a new full-specification reading.
- R7: rechecked FlooNoC v1 §III-A and §III-A1/2 for response reservation, reorder-table retirement and same-ID destination restrictions. The paper's ordering assumptions were kept explicit rather than imported as universal multi-VC behavior.
- R22: reused its saved gem5 v24.1.0.1 reading record. A fresh online source fetch did not succeed; no new source-code coverage or gem5 execution is claimed.
- The capacities, admission policy, conservative domain serialization, target service model and scenarios are original teaching choices. They are not verified AMD topology or protocol facts.

Primary-source links and detailed reading boundaries remain in [R8](sources/R8-axi-ordering-contract.md), [R7](sources/R7-floonoc-paper.md) and [R22](sources/R22-garnet-network-interface.md).

## Contract review scenarios

These rows record document-level event reasoning. They are not automated AXI protocol tests. A legal source eventually provides accepted write data, targets eventually service or report an error, consumers eventually accept results, and the selected schedulers provide service; arbitrary transport corruption and reset recovery remain outside this round's completion claim.

| Case | Events examined | Required outcome and review finding |
| --- | --- | --- |
| AW first | Admit AW; delay W; then transfer N beats | Entry, domain, AW association and payload slot remain allocated. Only the last valid W handshake releases the association element. |
| W first | Hold WVALID while no matching AW exists; subsequently admit AW | No early W acceptance or guessed identity. Source holds its beat; registered WREADY can be offered after the matching allocation. |
| Simultaneous AW/W | Both VALID signals appear while the association FIFO is empty | The chosen baseline admits AW first and accepts W subsequently. No same-edge address bypass is assumed. |
| Two accepted writes | AW(A), AW(B), W(A,0..last), W(B,0..last) | W is bound to the FIFO head, even if B's destination is faster. Payload storage and AW-order storage have distinct release points. |
| Different IDs | Slow A and fast B are already admitted; B returns first | B can become the next R burst without releasing A's reservation. The R output remains locked once selected. |
| Same ID, different target | C follows A in the same read domain | C cannot be admitted until A retires. A vacant read slot alone does not clear domain busy. An unaccepted address can cause upstream HOL. |
| Same numeric ID at two sources | S0 and S1 both use AXI ID 7 and may use local TxnID 7 | Source identity remains part of the return key. No table entry or result is aliased across sources. |
| Read/write directions | Equal ARID/AWID values; a dependent read after a write | Separate domains do not create a cross-channel fence. The reference write-then-read example waits for successful B and uses the stated SRAM visibility contract. |
| Read-slot exhaustion | Two read slots remain allocated, including a short read | A third read is backpressured even if a table entry is free. Unused bytes in an allocated fixed-size slot are not a new slot. |
| Write-slot / entry exhaustion | Two payloads await injection; separately, two reads plus two writes hold four entries | No third payload is accepted without a slot. Freeing an injected write payload does not free its waiting entry. |
| Concurrent admission offers | AR and AW compete for the last entry; READY is registered | Pending offers reserve distinct resources and count against capacity. Handshake commits the transaction; just-freed capacity is used on a later cycle. This is a stated contract, not an RTL timing result. |
| Target stall | Both target records occupied or the target withholds request acceptance | Data and descriptors remain in their current protected storage. A new head is not removed into nonexistent record space; Local credit accounts for in-flight flits. |
| R backpressure | Complete ReadRsp stored; RREADY low, including on the final beat | RID, data, status, last and the output beat position remain stable. No source entry, domain or read slot retires until the final handshake. |
| B backpressure | WriteRsp received; BREADY low | Status and identity remain stable in the existing entry. A single later handshake retires exactly once; R and B have separate output state. |
| Unmapped read | A legal-shape 256 B AR is admitted and decoded to the local error responder | No NoC request; deliver 16 DECERR R beats, with RLAST only on the last. Retire after all beats are accepted. |
| Unmapped write | A legal-shape 256 B AW is admitted; corresponding W is delayed | Consume all 16 W beats before presenting the one DECERR B. Free the payload after W completion, but keep entry/domain through B acceptance. |
| Target read failure | Target returns an error for the supported read | Preserve the full length. This controlled target uses uniform RRESP; a future mixed-RRESP target requires per-beat metadata rather than silent flattening. |
| Target write failure | Target consumes the write data and reports SLVERR | Return one B with the correct identity. No automatic rollback or transparent retry is inferred. |
| Malformed transport / protocol input | Wrong response identity or length, malformed WLAST, damaged credit | Do not convert unknown state into successful completion. Preserve the boundary to fault isolation/recovery; this round does not claim a complete recovery engine. |

## Executed arithmetic checks

A JavaScript check read the actual 12 rows of the guide's §6.10 table and independently tracked the active transaction set and payload ownership through the stated events. All published E/R/W triples matched, remained within 4/2/2, and ended at zero. Events that merely arrive, wait or free a write payload did not implicitly retire a transaction.

Expected triples by event e0–e11:

```text
(0,0,0), (1,1,0), (2,2,0), (2,2,0), (2,2,0), (3,2,1),
(3,2,0), (2,1,0), (1,0,0), (2,1,0), (1,1,0), (0,0,0)
```

The calculation also checked full-width byte coverage for both example bases (0x1000 and 0x8000) at each length from 1 through 16 beats: **32 cases**. Beat k covers `[A+16k, A+16k+15]`; adjacent ranges meet without overlap or gaps, and the final byte is `A+16N-1`.

The six independent shape/boundary checks were:

| Address | Bytes | Expected within the selected address/length shape | Result |
| --- | ---: | --- | --- |
| 0x0ff0 | 16 | yes | matched |
| 0x0ff0 | 32 | no: crosses 4 KB | matched |
| 0x1008 | 16 | no: unaligned | matched |
| 0x1000 | 272 | no: exceeds selected maximum | matched |
| 0x1000 | 0 | no: empty transfer | matched |
| 0x1000 | 256 | yes | matched |

These shape checks do not validate target mapping, permissions, every AXI attribute or protocol compliance. Additional arithmetic: each source has 1024 B of declared raw payload/response storage; each target has 512 B of record data storage, excluding metadata and interface queues. A 256 B data packet is 17 flits; ReadReq and WriteRsp are each one flit under the retained format.

This execution checks table accounting and formulas only. It is not a cycle-accurate NI model, a Router/NI integration run, exhaustive exploration, RTL simulation or a deadlock proof. No throughput/latency results were generated for the new NI.

## Integration and reader review

The architecture and interface descriptions now lead into the ordinary read/write walkthrough, followed by the NI resource and concurrency mechanisms. Public rules, project teaching choices and unknown target facts are kept separate. Common English terms are consistent in the modified text and diagrams. Round history remains in the progress record rather than a new appended technical chapter.

Two cross-section corrections are part of the NI revision: accepted but not-yet-injected transactions must remain able to progress during a normal drain; and the small correctness example's two read slots cannot be used to claim the separate 219 ns / 11-outstanding performance budget. The latter also lacks the newly explicit per-beat upstream-delivery timing, so it remains a historical budget with its own boundaries.

The final workspace check covered 15 documents, 563 local links and 36 heading anchors, including exact Git path casing; no missing target or anchor was found. Code fences were balanced. The eight Mermaid blocks received a structural/manual review; no rendered-diagram verification is claimed. The whitespace diff check passed.

Sections 7–10 and 12 (Router mechanisms) and section 14 (the existing D2D baseline) matched the pre-edit workspace snapshot after line-ending normalization. SHA-256 checks of the Router script and saved result file also matched their pre-edit workspace hashes. These preservation checks are separate from executing the model.

Completion state is recorded in [RESEARCH_PROGRESS.md](../SWITCH/RESEARCH_PROGRESS.md). The next research task is round 4: compose the now-explicit NI, target, Router and consumer resources into an end-to-end dependency analysis and a defined drain/reset/epoch recovery contract.
