# Reports

Five standing reports. Each runs deterministically against the loaded graph.

| Report | Answers |
|---|---|
| **coverage** | Which layers are populated, how deeply, and what is missing entirely. |
| **report** | The digest — the graph in prose. |
| **audit** | Continuity detectors. *(needs Kùzu)* |
| **deviations** | Where the prose has drifted from the recorded canon. |
| **queue** | What is still provisional, ranked by what it would cost to be wrong. |

## Which to run when

**coverage** first, on any graph you did not build yourself. It tells you what the graph
knows before you start trusting answers from it.

**queue** when you have time to ratify but not much of it. Its ranking is structural, not
popular: a claim that underpins a chain of other claims outranks one that merely has many
believers — because a believer can be revised in place, while a dependent claim has to be
revisited or it quietly becomes false.

**deviations** after a revision pass, to catch the places where you changed the prose and
the graph still describes the old version.

**audit** when something feels wrong and you cannot name it.
