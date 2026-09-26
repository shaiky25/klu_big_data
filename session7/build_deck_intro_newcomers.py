"""10-slide beginner primer on Hadoop, for viewers new to Big Data.
Content sourced directly from session7/hadoop.txt (5-slide outline),
expanded to 10 slides -- one idea per slide instead of stacking two
pillars together. Companion to session7's main deep-dive deck.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "bda-weekly-deliverables", "scripts"))
from pptx_helpers import (
    new_presentation, new_slide, add_title, add_card, add_stat_callout,
    add_table, add_bullets, notes, finalize_and_save,
)
from pptx.util import Inches

prs = new_presentation()

# 1. Title
s = new_slide(prs)
add_title(s, "Hadoop, Explained in Plain English", kicker="Introduction for newcomers")
add_bullets(s, Inches(0.6), Inches(2.0), Inches(11.5), Inches(3.5), [
    "Why single machines stopped being enough for Big Data",
    "HDFS: how Hadoop stores data across a cluster",
    "MapReduce: how Hadoop processes data across a cluster",
    "YARN: how Hadoop shares cluster resources across jobs",
    "The ecosystem and real companies running it at scale",
])
notes(s, "Framing slide -- five pillars from the source outline, one per section ahead.")

# 2. The Big Data Challenge
s = new_slide(prs)
add_title(s, "From Single Machines to Clusters", kicker="The Big Data challenge")
add_card(s, Inches(0.6), Inches(1.5), Inches(5.9), Inches(5.2), "What used to work",
         ["Traditional single-processor systems easily handled small volumes of structured data stored in neat rows and columns"], body_size=15.5)
add_card(s, Inches(6.7), Inches(1.5), Inches(6.0), Inches(5.2), "What changed",
         ["The rise of unstructured Big Data: emails, images, audio, and video",
          "This created massive semi-structured and unstructured data streams that overwhelmed single machines"], body_size=15.5)
notes(s, "Set up the contrast before introducing the distributed answer on the next slide.")

# 3. The Distributed Solution
s = new_slide(prs)
add_title(s, "The Distributed Solution", kicker="Why Hadoop exists")
add_card(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(3.0),
         "Hadoop solves scaling bottlenecks by using a distributed cluster of commodity hardware to store and process data collectively",
         ["\"Commodity hardware\" -- ordinary, affordable servers, not specialized supercomputers",
          "The cluster works together as one system instead of relying on any single machine"], body_size=16)
add_stat_callout(s, Inches(0.6), Inches(4.9), Inches(5.85), Inches(1.9), "Store", "collectively, across the cluster")
add_stat_callout(s, Inches(6.65), Inches(4.9), Inches(6.05), Inches(1.9), "Process", "collectively, across the cluster")
notes(s, "Bridge slide: names the three pillars (HDFS, MapReduce, YARN) that the next six slides unpack.")

# 4. Pillar 1 -- HDFS: Distributed File Allocation
s = new_slide(prs)
add_title(s, "Pillar 1 — HDFS: Splitting Files Into Blocks", kicker="Data storage")
add_card(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(5.0), "Distributed file allocation",
         ["The Hadoop Distributed File System (HDFS) splits large files into smaller data blocks",
          "Those blocks are distributed across multiple data nodes in the cluster"], body_size=15.5)
add_card(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(5.0), "Default block sizing",
         ["Data is partitioned into default 128 MB blocks",
          "Example: a 600 MB file is split into four 128 MB blocks and one 88 MB block"], body_size=15.5)
notes(s, "Use the 600 MB example concretely -- 4x128MB + 1x88MB = 600MB, it's arithmetic students can verify live.")

# 5. Pillar 1 -- HDFS: Replication
s = new_slide(prs)
add_title(s, "Pillar 1 — HDFS: Replication for Fault Tolerance", kicker="Data storage")
add_card(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(3.2), "3x replication schema",
         ["To ensure fault tolerance, HDFS creates copies of each block",
          "The default replication factor is 3, spread across different nodes",
          "This prevents data loss if a node crashes"], body_size=16)
add_stat_callout(s, Inches(0.6), Inches(5.1), Inches(12.1), Inches(1.7), "3 copies per block",
                  "one node failing costs zero data")
notes(s, "This is the fault-tolerance payoff of the block-splitting design from the previous slide.")

# 6. Pillar 2 -- MapReduce: Divide and Conquer / Mapper
s = new_slide(prs)
add_title(s, "Pillar 2 — MapReduce: Divide and Conquer", kicker="Data processing")
add_card(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(5.0), "Divide-and-conquer execution",
         ["MapReduce avoids processing bottlenecks by splitting datasets into individual parts",
          "Those parts execute in parallel across cluster nodes"], body_size=15.5)
add_card(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(5.0), "Mapper phase",
         ["Input data is split into sections -- for example, text separated by full stops",
          "Mapper functions count or process items locally, on each node's own data"], body_size=15.5)
notes(s, "Mirrors HDFS's own pattern: work is split and kept local to where the data already sits.")

# 7. Pillar 2 -- MapReduce: Shuffle, Sort, Reduce
s = new_slide(prs)
add_title(s, "Pillar 2 — Shuffle, Sort, and Reduce", kicker="Data processing")
add_table(s, Inches(0.6), Inches(1.7), Inches(12.1), Inches(2.6), [
    ["Step", "What happens"],
    ["Shuffle", "Intermediate results from every mapper are collected across the cluster"],
    ["Sort", "Those results are sorted by key so matching keys end up together"],
    ["Reduce", "The reducer phase consolidates sorted results into the aggregated final output"],
])
notes(s, "Pair with the mapper example from the previous slide: same sentences, now the counts get combined into a final total.")

# 8. Pillar 3 -- YARN: Resource Orchestration
s = new_slide(prs)
add_title(s, "Pillar 3 — YARN: Resource Orchestration", kicker="Cluster resource manager")
add_card(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(2.6),
         "YARN (Yet Another Resource Negotiator) manages and allocates physical computing resources",
         ["Covers RAM, CPU, and network bandwidth", "Across all concurrent jobs running on the cluster"], body_size=15.5)
add_table(s, Inches(0.6), Inches(4.5), Inches(12.1), Inches(2.3), [
    ["Component", "Role"],
    ["Resource Manager", "Coordinates overall cluster resource assignments"],
    ["Node Managers", "Monitor resource consumption on individual server nodes"],
])
notes(s, "First two of YARN's core components; Application Master & Containers continue on the next slide.")

# 9. Pillar 3 -- YARN: Application Master & Containers + Ecosystem
s = new_slide(prs)
add_title(s, "Application Master, Containers, and the Ecosystem", kicker="Cluster resource manager")
add_card(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(5.0), "Application Master & Containers",
         ["Application Masters request containers -- allocations of physical resources -- from Node Managers",
          "Those containers execute the actual workload requests"], body_size=15)
add_card(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(5.0), "Modularity & add-ons",
         ["Additional frameworks sit on top of Hadoop to simplify analytics and data ingestion",
          "Hive, Pig, Apache Spark, Flume, and Sqoop are the named examples"], body_size=15)
notes(s, "Closes the YARN component list, then bridges to the ecosystem tools that run as YARN-managed jobs.")

# 10. Real-World Impact & Summary
s = new_slide(prs)
add_title(s, "Real-World Impact", kicker="Enterprise adoption")
add_card(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(2.3), "Who runs it, and for what",
         ["Industry leaders such as Facebook, IBM, eBay, and Amazon deploy Hadoop clusters",
          "Use cases named: data warehousing, fraud detection, and recommendation engines"], body_size=15.5)
add_table(s, Inches(0.6), Inches(4.2), Inches(12.1), Inches(2.6), [
    ["Pillar", "One-line takeaway"],
    ["HDFS", "Splits files into replicated blocks across the cluster"],
    ["MapReduce", "Splits computation into parallel map, shuffle/sort, and reduce steps"],
    ["YARN", "Shares cluster CPU, RAM, and bandwidth across concurrent jobs"],
])
notes(s, "Closing recap of all three pillars in one table before returning to session7's full deep-dive deck.")

finalize_and_save(prs, "session7/session7-hadoop-intro-newcomers.pptx")
print("Saved session7/session7-hadoop-intro-newcomers.pptx")
