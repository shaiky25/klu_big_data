# Session Prep: Hadoop Architecture & MapReduce
**Audience:** undergrads · **When:** Saturday 2026-09-19 · **Format:** ~75 min + lab

## Learning objectives
By the end, students can:
1. Explain why single-machine processing breaks down (volume + the Google 2003 story)
2. Describe HDFS: NameNode, DataNodes, blocks, replication
3. Describe YARN: ResourceManager, NodeManagers, ApplicationMaster
4. Trace a MapReduce job (map → shuffle/sort → reduce) on paper
5. Name one strength and one real limitation of MapReduce

## Session arc

### 1. Hook — "Why can't one computer handle it?" (5 min)
- Data growth: a single machine hits limits on storage *and* on time-to-process.
- Google, 2003–2004: needed to index the web. Two papers — GFS (2003), MapReduce (2004) — became HDFS + MapReduce in the open-source Hadoop project (Doug Cutting, Yahoo).
- The punchline you'll return to all session: **bring the compute to the data, not the data to the compute.** Moving petabytes to CPUs is the bottleneck; moving a small program to where the data lives is cheap.

### 2. HDFS — the storage layer (15 min)
**Talking points:**
- Files are split into **blocks** (default 128 MB — ask *why so big?* before answering: fewer blocks → less NameNode bookkeeping; it's optimized for streaming large reads, not random access).
- Each block is **replicated 3×** across different DataNodes (and racks — "rack awareness": survive a whole rack failing).
- **NameNode** = the librarian: holds only *metadata* (which blocks live where). It never stores data.
- **DataNodes** = the shelves: store the actual blocks, heartbeat to the NameNode.
- **Library analogy:** the librarian doesn't keep the books — she keeps the card catalog. Books (blocks) are photocopied 3× and shelved on different floors (racks). If a shelf collapses, the copies survive.
- Failure story: a DataNode dies → NameNode notices missed heartbeats → re-replicates the under-replicated blocks. Nobody pages a human.

**Preempt:** "Isn't the NameNode a single point of failure?" — Yes, in classic Hadoop (that's the honest answer; HA NameNode / federation came later). Good engineers name the weakness.

### 3. YARN — the resource layer (10 min)
- Problem YARN solved: in Hadoop 1, MapReduce *was* the scheduler — nothing else could run on the cluster.
- **ResourceManager** (one per cluster): the foreman — knows all available CPU/RAM, hands out containers.
- **NodeManager** (one per machine): the worker supervisor — runs containers, reports health.
- **ApplicationMaster** (one per job): the job's personal manager — negotiates resources from the RM, supervises its own tasks, restarts failures.
- **Construction-site analogy:** foreman (RM) assigns crews to buildings; each building gets a site manager (AM) who runs their own crew day-to-day.
- Payoff line: YARN is why Spark, Hive, and others can all run on the same Hadoop cluster.

### 4. MapReduce — the programming model (25 min)
**The core idea (say it three times in different words):** you write two functions; the framework handles distribution, shuffling, and failure.

**Worked example — word count, traced on the board:**
- Input: 3 splits. Split 1: "big data big", Split 2: "data is big", Split 3: "big big data".
- **Map** emits (word, 1) pairs per split:
  - M1: (big,1),(data,1),(big,1) · M2: (data,1),(is,1),(big,1) · M3: (big,1),(big,1),(data,1)
- **Shuffle/sort** (the framework's magic, not your code): groups by key —
  - big → [1,1,1,1,1], data → [1,1,1], is → [1]
- **Reduce** sums: big → 5, data → 3, is → 1.
- Hammer home: *you never wrote the grouping or the distribution.* The shuffle is the part beginners underestimate — it's where the network cost lives.

**Why it works (the three superpowers):**
1. **Data locality** — mappers run where the blocks are.
2. **Fault tolerance** — a failed task just gets re-executed elsewhere; deterministic functions make this safe.
3. **Simple contract** — map and reduce are easy to reason about, easy to parallelize.

**Honest limitations (teaching these builds credibility):**
- Terrible for **iterative** algorithms (each iteration re-reads from disk — this is exactly why Spark won ML workloads).
- High **latency** — batch only, not interactive.
- The shuffle can dominate cost ("more nodes isn't always faster").

**"MapReduce is dead, why learn it?"** — preempt directly: the *engine* faded, the *mental model* runs the world. Spark, Beam, Flink all inherit map → shuffle → reduce. And batch embedding pipelines for AI are MapReduce-shaped (map: chunk+embed, reduce: index). Learning the pattern > learning the tool.

### 5. Bridge segment — where this shows up in AI (10 min)
*(This is your FDE-prep segment too.)*
- Modern embedding pipeline = map (chunk documents, compute embeddings) → shuffle (route by partition) → reduce (build index shards).
- Same tuning instincts: block/chunk size trade-offs, shuffle cost dominating, re-execution on failure.
- One-liner to close: "You just learned the architecture underneath half of today's AI infrastructure."

### 6. Check for understanding (10 min)
1. A DataNode dies mid-job. Walk me through exactly what happens — who notices, what gets re-created, does the job fail?
2. Why 128 MB blocks instead of 4 KB blocks? What's the trade-off?
3. In word count, what does the shuffle phase actually *do*, and who wrote the code for it?
4. 10 mappers running, 2 fail. What does the framework do, and why is it safe to just re-run them?
5. Why is MapReduce a bad fit for training a model that needs 100 passes over the data?

## Likely confusions to watch for
- **Hadoop ≠ MapReduce.** Hadoop is the ecosystem (HDFS + YARN + ...); MapReduce is one processing engine on it. Students will conflate them — correct early.
- **The NameNode stores no data.** Repeat until it sticks.
- **Shuffle is not free.** Beginners think map+reduce is the whole story; the network shuffle is where jobs go to die.

## Lab idea (for the .Rmd)
No cluster needed: simulate the model locally in R or Python. Give them a text file and have them implement `map()` emitting (word,1), then implement the shuffle (group-by) themselves, then `reduce()`. The aha moment: *they* write the shuffle this time and feel how much the framework was doing for them. Bonus: time it on a bigger file and discuss where it would parallelize.

## Practice plan
Dry-run with an audience surrogate (that's me): present any 10-minute slice, I'll play the confused undergrad and interrupt with the questions above. Or flip it — I quiz you rapid-fire on the five check questions until the answers are crisp.
