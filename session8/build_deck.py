#!/usr/bin/env python3
"""Build session8's Apple-style deck from the shared template.
Run from the project root: python3 session8/build_deck.py
"""
import copy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / ".claude" / "skills" / "bda-weekly-deliverables"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pptx_helpers as ph
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE = SKILL_DIR / "assets" / "session-template-apple-style.pptx"
OUT_PATH = PROJECT_ROOT / "session8" / "Hive_Pig_Hadoop_Ecosystem.pptx"

# Layout catalog indices (0-based, matches pptx-template-agent-guide.md)
COVER, SECTION, STATEMENT, KEYPOINTS, TWOCOL, STAT, IMAGE, QUOTE, DIAGRAM, CODE, STEPS, CLOSING = range(12)

# Template's own dark-card / accent palette, reused (not invented) for the
# hand-built diagram nodes so they match the surrounding slides exactly.
NODE_FILL = RGBColor(0x1D, 0x1D, 0x1F)
NODE_BORDER = RGBColor(0x00, 0x71, 0xE3)
NODE_TEXT = RGBColor(0xF5, 0xF5, 0xF7)
ARROW_TEXT = RGBColor(0x86, 0x86, 0x8B)


def set_lines(shape, lines, font_name=None):
    """Replace each paragraph's single run text in order, preserving the
    template's own paragraph-level formatting (inherited theme font/color,
    never touched here). Clones the last paragraph's XML when more lines
    are needed than the placeholder has (the Code layout starts with one
    paragraph for a multi-line snippet); drops any leftover template
    paragraphs beyond len(lines). font_name, when given, overrides every
    line's font explicitly -- only the Code layout needs this, since its
    placeholder inherits 'Menlo' (Mac-only, not lint-allowed) at the
    paragraph level and must be swapped to 'Courier New'."""
    tf = shape.text_frame
    paras = list(tf.paragraphs)
    while len(paras) < len(lines):
        last_p_el = paras[-1]._p
        new_p_el = copy.deepcopy(last_p_el)
        last_p_el.addnext(new_p_el)
        paras = list(tf.paragraphs)
    for i, line in enumerate(lines):
        p = paras[i]
        p.runs[0].text = line
        if font_name:
            p.font.name = font_name
    for extra in paras[len(lines):]:
        extra._p.getparent().remove(extra._p)


def add_flow(slide, x, y, w, h, labels, connect=True):
    """A row of bordered nodes, one per label, built from the template's own
    card colors (near-black fill, Apple-blue border) so it reads as part of
    the deck, not a bolted-on chart. connect=True (default) joins them with
    arrow glyphs for a left-to-right sequence; connect=False lays them out
    as parallel, unconnected boxes -- for grouping concepts (e.g. a data
    model's building blocks) rather than showing a pipeline."""
    n = len(labels)
    gap = Emu(int(0.35 * 914400))
    node_w = Emu(int((w - gap * (n - 1)) / n))
    for i, label in enumerate(labels):
        nx = Emu(int(x + i * (node_w + gap)))
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, nx, y, node_w, h)
        box.fill.solid(); box.fill.fore_color.rgb = NODE_FILL
        box.line.color.rgb = NODE_BORDER; box.line.width = Pt(1.25)
        box.adjustments[0] = 0.12
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = label
        p.alignment = PP_ALIGN.CENTER
        p.font.size, p.font.bold, p.font.color.rgb = Pt(14), True, NODE_TEXT
        if connect and i < n - 1:
            ax = Emu(int(x + (i + 1) * node_w + i * gap))
            arrow = slide.shapes.add_textbox(ax, y, gap, h)
            atf = arrow.text_frame
            atf.vertical_anchor = MSO_ANCHOR.MIDDLE
            ap = atf.paragraphs[0]
            ap.text = "→"
            ap.alignment = PP_ALIGN.CENTER
            ap.font.size, ap.font.color.rgb = Pt(18), ARROW_TEXT


def build():
    prs = Presentation(str(TEMPLATE))

    # 1. Cover
    s = ph.duplicate_slide(prs, COVER)
    set_lines(s.shapes[0], ["BDA POP · SESSION 8", "Hive & Pig",
                             "SQL and scripting on data that never leaves HDFS"])
    set_lines(s.shapes[1], ["Faiz  ·  09/22/2026"])
    ph.notes(s, "Open by naming the gap from last week: we named Hive and Pig, but never showed what "
                 "typing a query or a cleanup script actually looks like. That's today.")

    # 2. Section — Part 1: Hive
    s = ph.duplicate_slide(prs, SECTION)
    set_lines(s.shapes[0], ["PART 1", "Hive"])
    ph.notes(s, "Frame Hive as the SQL front end over data that was always going to live in HDFS.")

    # 3. Statement
    s = ph.duplicate_slide(prs, STATEMENT)
    set_lines(s.shapes[0], ["SQL on data that never left HDFS."])
    ph.notes(s, "Hive doesn't move the data anywhere new -- it gives it a schema and a query language.")

    # 4. Key Points — 4 pieces
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["Four pieces run every Hive query"])
    set_lines(s.shapes[2], ["—  Driver — owns the session",
                             "—  Compiler — plans against the Metastore",
                             "—  Execution Engine — runs it on the cluster"])
    ph.notes(s, "The Metastore is the piece people forget: it's a separate small database holding "
                 "table schema and file locations. Hive never touches HDFS bytes until a query needs them.")

    # 5. Diagram — query flow
    s = ph.duplicate_slide(prs, DIAGRAM)
    set_lines(s.shapes[0], ["How a HiveQL query actually runs"])
    for shp in list(s.shapes):
        if shp.has_text_frame and shp.text_frame.text.startswith("[DIAGRAM"):
            shp._element.getparent().remove(shp._element)
    add_flow(s, Emu(914400), Emu(2700000), Emu(10362895), Emu(1400000),
             ["HiveQL query", "Driver", "Compiler +\nMetastore", "Execution\nEngine", "HDFS"])
    ph.notes(s, "Walk left to right: the query never touches HDFS directly -- the Compiler checks "
                 "the Metastore's schema first, then the Execution Engine runs the compiled plan.")

    # 6. Two Column — managed vs external
    s = ph.duplicate_slide(prs, TWOCOL)
    set_lines(s.shapes[0], ["Managed vs. external tables"])
    set_lines(s.shapes[2], ["Managed", "Hive owns the data — DROP TABLE deletes the HDFS files too."])
    set_lines(s.shapes[4], ["External", "Hive owns only the schema — the files stay another pipeline's."])
    ph.notes(s, "Real incident pattern: pointing a managed table at a shared raw-log directory, then "
                 "one DROP TABLE takes out data another pipeline still needed.")

    # 7. Diagram — Hive's data model (parallel boxes, no arrows)
    s = ph.duplicate_slide(prs, DIAGRAM)
    set_lines(s.shapes[0], ["Hive's data model"])
    for shp in list(s.shapes):
        if shp.has_text_frame and shp.text_frame.text.startswith("[DIAGRAM"):
            shp._element.getparent().remove(shp._element)
    add_flow(s, Emu(2286000), Emu(2700000), Emu(7620000), Emu(1400000),
             ["Tables", "Partitions", "Buckets"], connect=False)
    ph.notes(s, "Tables split into partitions (one HDFS folder per column value, e.g. order_date); "
                 "partitions split further into buckets (a fixed hash split) for even finer-grained reads. "
                 "Both exist for the same reason -- avoid reading data a query doesn't need.")

    # 8. Code — building and loading a Hive table
    s = ph.duplicate_slide(prs, CODE)
    set_lines(s.shapes[0], ["Building and loading a Hive table"])
    set_lines(s.shapes[2], [
        "CREATE DATABASE IF NOT EXISTS",
        "  delivery_ops;",
        "",
        "CREATE TABLE orders (",
        "  order_id INT, restaurant_id INT,",
        "  delivery_time_minutes INT",
        ")",
        "PARTITIONED BY (order_date STRING);",
        "",
        "LOAD DATA INPATH '/raw/orders.csv'",
        "INTO TABLE orders",
        "PARTITION (order_date='2026-09-06');",
    ], font_name="Courier New")
    ph.notes(s, "This is the full lifecycle before anyone queries anything. LOAD DATA doesn't copy the "
                 "file twice -- it moves it from its raw HDFS path straight into the partition directory "
                 "the Metastore expects. Nothing is validated until a query actually reads it back.")

    # 9. Code — querying and joining in HiveQL
    s = ph.duplicate_slide(prs, CODE)
    set_lines(s.shapes[0], ["Querying and joining in HiveQL"])
    set_lines(s.shapes[2], [
        "SELECT r.price_range,",
        "  ROUND(AVG(o.delivery_time_minutes), 1)",
        "    AS avg_delivery",
        "FROM orders o",
        "JOIN restaurants r",
        "  ON o.restaurant_id = r.restaurant_id",
        "WHERE o.order_date = '2026-09-06'",
        "GROUP BY r.price_range;",
    ], font_name="Courier New")
    ph.notes(s, "The JOIN looks exactly like a SQL join because it is one -- HiveQL borrows SQL's syntax "
                 "rather than inventing its own. ROUND() is one of Hive's built-in functions, alongside "
                 "FLOOR() and CEILING().")

    # 10. Stat — rows scanned
    s = ph.duplicate_slide(prs, STAT)
    set_lines(s.shapes[0], ["5,401 → 361", "rows scanned, naive vs. partition-pruned"])
    ph.notes(s, "This week's simulated order log: 5,401 rows across 14 days. One day's partition is 361 "
                 "rows -- roughly 15x fewer read for a question that only ever needed one day's answer.")

    # 11. Statement
    s = ph.duplicate_slide(prs, STATEMENT)
    set_lines(s.shapes[0], ["Partition pruning: scan today, not everything."])
    ph.notes(s, "This is the Hive-level version of last week's 'bring the compute to the data.'")

    # 12. Key Points — business payoff of partition pruning
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["What partition pruning saves at scale"])
    set_lines(s.shapes[2], ["—  Less cluster time paying for scans nobody needed",
                             "—  Faster answers for an analyst waiting on a query",
                             "—  Lower compute cost per question asked"])
    ph.notes(s, "Tie this back to money and time -- a platform-scale cluster's cost is measured in "
                 "compute-hours, and an unpruned scan burns them for no extra insight.")

    # 13. Section — Part 2
    s = ph.duplicate_slide(prs, SECTION)
    set_lines(s.shapes[0], ["PART 2", "The Mess Underneath"])
    ph.notes(s, "Bridge: Hive can query dirty data, it just shouldn't have to. Where does the dirt come from?")

    # 14. Key Points — what raw logs look like
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["What raw order logs actually look like"])
    set_lines(s.shapes[2], ["—  Missing delivery times",
                             "—  Negative, nonsensical values",
                             "—  No error raised, just a quietly wrong AVG()"])
    ph.notes(s, "This is 'unstructured' in the sense that matters here -- not free text, just fields you can't trust yet.")

    # 15. Key Points — why this happens at scale
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["Why this happens at real platform scale"])
    set_lines(s.shapes[2], ["—  Millions of app events a day, many code paths writing them",
                             "—  Retries, crashes, and partial writes create garbage rows",
                             "—  Small scale: noise. Platform scale: a biased average"])
    ph.notes(s, "This is why cleaning can't be a one-off script -- it has to be a pipeline step that runs every time.")

    # 16. Stat — 4% invalid
    s = ph.duplicate_slide(prs, STAT)
    set_lines(s.shapes[0], ["4%", "of raw order-log rows are invalid"])
    ph.notes(s, "216 of 5,401 simulated rows this week -- small-looking, but it's biasing every average silently.")

    # 17. Section — Part 3: Pig
    s = ph.duplicate_slide(prs, SECTION)
    set_lines(s.shapes[0], ["PART 3", "Pig"])
    ph.notes(s, "Pig is the tool for exactly the cleanup job the last section just diagnosed.")

    # 18. Statement
    s = ph.duplicate_slide(prs, STATEMENT)
    set_lines(s.shapes[0], ["Pig Latin cleans the mess before Hive."])
    ph.notes(s, "Pig is procedural on purpose -- a pipeline of steps, not a single question.")

    # 19. Key Points — what Pig is built for
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["What Pig is built for"])
    set_lines(s.shapes[2], ["—  A readable, step-by-step pipeline",
                             "—  LOAD, FILTER, GROUP, JOIN, STORE",
                             "—  Compiles down to MapReduce, like Hive"])
    ph.notes(s, "Same underlying engine as Hive -- the difference is entirely in who writes it and why.")

    # 20. Diagram — Pig Latin's data model (parallel boxes, no arrows)
    s = ph.duplicate_slide(prs, DIAGRAM)
    set_lines(s.shapes[0], ["Pig Latin's data model"])
    for shp in list(s.shapes):
        if shp.has_text_frame and shp.text_frame.text.startswith("[DIAGRAM"):
            shp._element.getparent().remove(shp._element)
    add_flow(s, Emu(685800), Emu(2600000), Emu(11048400), Emu(1500000),
             ["34\nAtom", "(1042, 7, 34)\nTuple", "{(1042,..),\n(1043,..)}\nBag",
              "[city#Blr,\nmins#34]\nMap"], connect=False)
    ph.notes(s, "Atom -- one value (a delivery time in minutes). Tuple -- one ordered row (order_id, "
                 "restaurant_id, delivery_time_minutes) -- same as one row in an RDBMS. Bag -- a "
                 "collection of tuples, same as a table; a Pig relation like raw_orders IS a bag. "
                 "Map -- key-value pairs, keyed by field name, always a string key.")

    # 21. Diagram — what running a Pig script actually does
    s = ph.duplicate_slide(prs, DIAGRAM)
    set_lines(s.shapes[0], ["What running a Pig script actually does"])
    for shp in list(s.shapes):
        if shp.has_text_frame and shp.text_frame.text.startswith("[DIAGRAM"):
            shp._element.getparent().remove(shp._element)
    add_flow(s, Emu(914400), Emu(2700000), Emu(10362895), Emu(1400000),
             ["Pig Latin\nscript", "Local or\nMapReduce mode", "Compiled\nMR job", "Clean\noutput"])
    ph.notes(s, "Mirror of the HiveQL flow from Part 1 -- same shape, different starting point. The mode "
                 "chosen in the second box is exactly the Local vs. MapReduce choice on the next slide.")

    # 22. Steps — 3-stage pipeline
    s = ph.duplicate_slide(prs, STEPS)
    set_lines(s.shapes[0], ["A cleanup pipeline in three stages"])
    set_lines(s.shapes[1], ["1", "LOAD", "Read the raw order log as-is"])
    set_lines(s.shapes[2], ["2", "FILTER", "Drop rows with missing or negative times"])
    set_lines(s.shapes[3], ["3", "STORE", "Write the clean table Hive queries"])
    ph.notes(s, "This maps directly onto the Pig Latin script on the next slide -- same three verbs.")

    # 23. Code — Pig Latin
    s = ph.duplicate_slide(prs, CODE)
    set_lines(s.shapes[0], ["The Pig Latin for that pipeline"])
    set_lines(s.shapes[2], [
        "raw = LOAD 'orders_raw.csv'",
        "     USING PigStorage(',')",
        "     AS (order_id:int,",
        "         delivery_time_minutes:int);",
        "",
        "clean = FILTER raw BY",
        "        delivery_time_minutes > 0;",
        "",
        "STORE clean INTO",
        "      '/warehouse/orders_clean';",
    ], font_name="Courier New")
    ph.notes(s, "Narrate FILTER specifically -- that's the line doing the work the 4% stat just showed we need.")

    # 24. Stat — before/after
    s = ph.duplicate_slide(prs, STAT)
    set_lines(s.shapes[0], ["4% → 0%", "invalid rows, before and after the FILTER"])
    ph.notes(s, "Same dataset, same rows counted the same way -- the FILTER step is the only thing that changed.")

    # 25. Two Column — execution modes (both tools)
    s = ph.duplicate_slide(prs, TWOCOL)
    set_lines(s.shapes[0], ["Execution modes: local vs. MapReduce"])
    set_lines(s.shapes[2], ["Local mode",
                             "One data node, small input -- Pig reads/writes the plain Linux "
                             "filesystem, not HDFS. Used to test a script before it runs at scale."])
    set_lines(s.shapes[4], ["MapReduce mode",
                             "The default for both tools -- multiple nodes, large input. HiveQL and "
                             "Pig Latin both compile down to MapReduce jobs run on the cluster."])
    ph.notes(s, "Same choice, both tools -- the one difference to flag is that Pig's local mode talks "
                 "to the ordinary filesystem, which is why it's for a quick dry run, not production.")

    # 26. Two Column — Hive vs Pig
    s = ph.duplicate_slide(prs, TWOCOL)
    set_lines(s.shapes[0], ["Hive vs. Pig"])
    set_lines(s.shapes[2], ["Hive", "Declarative SQL — for someone who already knows the question."])
    set_lines(s.shapes[4], ["Pig", "Procedural script — for someone who has to clean the answer first."])
    ph.notes(s, "Both compile to the same batch engine underneath -- this is a 'who' and 'when' distinction, not a 'how'.")

    # 27. Two Column — Hive vs Pig, continued
    s = ph.duplicate_slide(prs, TWOCOL)
    set_lines(s.shapes[0], ["Hive vs. Pig, continued"])
    set_lines(s.shapes[2], ["Hive",
                             "Structured data only. Runs server-side via HiveServer2, with a web "
                             "interface — but no native Avro support."])
    set_lines(s.shapes[4], ["Pig",
                             "Structured, semi-structured, and unstructured data. Runs client-side, "
                             "no web interface, but supports Avro for handing output to another language."])
    ph.notes(s, "The 'data types' line is the one that actually matters for this week's topic: Hive "
                 "can't touch the unstructured slice of the log, Pig can -- that's the whole reason "
                 "both tools exist side by side instead of Hive alone.")

    # 28. Section — Part 4
    s = ph.duplicate_slide(prs, SECTION)
    set_lines(s.shapes[0], ["PART 4", "The Rest Of The Stack"])
    ph.notes(s, "Hive and Pig assume the data already landed in HDFS and that something scheduled the job. Two more gaps to close.")

    # 29. Key Points — getting data in and keeping it running
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["Getting data in, and keeping it running"])
    set_lines(s.shapes[2], ["—  Sqoop & Flume — batch and streaming ingestion into HDFS",
                             "—  Oozie — schedules and chains the jobs in order",
                             "—  ZooKeeper — keeps cluster services agreeing who's in charge"])
    ph.notes(s, "Sqoop: nightly batch pulls from a production database. Flume: a live event stream. "
                 "Oozie is the 'every night at 2am, in this order' piece. ZooKeeper is infrastructure "
                 "plumbing, not a data tool -- none of the four touch the data itself.")

    # 30. Diagram — nightly pipeline
    s = ph.duplicate_slide(prs, DIAGRAM)
    set_lines(s.shapes[0], ["A realistic nightly pipeline"])
    for shp in list(s.shapes):
        if shp.has_text_frame and shp.text_frame.text.startswith("[DIAGRAM"):
            shp._element.getparent().remove(shp._element)
    add_flow(s, Emu(457200), Emu(2700000), Emu(11277495), Emu(1400000),
             ["Sqoop /\nFlume", "HDFS\n(raw)", "Pig\n(clean)", "Hive\n(query)", "Answers"])
    ph.notes(s, "Oozie is what actually ran all five steps in order, unattended, every night -- it's not a box "
                 "in the data path, it's the thing scheduling the whole row.")

    # 31. Statement
    s = ph.duplicate_slide(prs, STATEMENT)
    set_lines(s.shapes[0], ["Every unstructured-data problem already has its tool."])
    ph.notes(s, "None of these compete with Hive or Pig -- each one fills a gap neither was built to cover.")

    # 32. Quote
    s = ph.duplicate_slide(prs, QUOTE)
    set_lines(s.shapes[0], ["“Distributed systems don't remove the mess in your data — "
                             "they just give you a place big enough to clean it up.”",
                             "— Big Data engineering maxim"])
    ph.notes(s, "Land this as the session's one-liner before the recap.")

    # 33. Statement — recap
    s = ph.duplicate_slide(prs, STATEMENT)
    set_lines(s.shapes[0], ["Raw logs in. Pig cleans. Hive answers."])
    ph.notes(s, "The whole session in six words -- use this as the anchor before the takeaways slide.")

    # 34. Key Points — takeaways
    s = ph.duplicate_slide(prs, KEYPOINTS)
    set_lines(s.shapes[0], ["What to remember"])
    set_lines(s.shapes[2], ["—  Partition and bucket, or scan everything every time",
                             "—  Clean before you query, not inside every query",
                             "—  Hive and Pig still run on MapReduce underneath"])
    ph.notes(s, "Closing recap -- three points, no new information.")

    # 35. Closing
    s = ph.duplicate_slide(prs, CLOSING)
    set_lines(s.shapes[0], ["Thank you.", "Next: scaling analytics beyond batch."])
    ph.notes(s, "Assumption flagged for review: next week's exact topic isn't in topics.txt yet as of this "
                 "build, so this teaser is deliberately generic rather than naming a specific tool.")

    # Drop the 12 original LAYOUT pattern slides (always the first 12 at this point)
    for _ in range(12):
        ph.delete_slide(prs, 0)

    ph.finalize_and_save(prs, str(OUT_PATH))
    print(f"Saved {OUT_PATH} with {len(prs.slides)} slides")


if __name__ == "__main__":
    build()
