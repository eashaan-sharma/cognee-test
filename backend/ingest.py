"""Step 3: build the knowledge graph from the files in data/raw with Cognee.

Pipeline:  add (register files)  ->  cognify (chunk -> LLM extracts nodes/edges -> merge -> store)
Our part is the schema below: it tells the LLM which entity types exist and how to name things.

Examples:
  uv run python backend/ingest.py --estimate Aragorn Gandalf "Company of the Ring"
  uv run python backend/ingest.py Aragorn Gandalf "Company of the Ring"
  uv run python backend/ingest.py --all
  uv run python backend/ingest.py --reset
"""
import argparse
import asyncio
from typing import Literal

import cognee
from cognee.shared.data_models import Edge, KnowledgeGraph, Node
from pydantic import Field

from config import COGNEE_DIR, DATA_DIR, RAW_DIR

# Keep Cognee's databases in our project (data/cognee), not inside .venv.
cognee.config.system_root_directory(str(COGNEE_DIR / "system"))
cognee.config.data_root_directory(str(COGNEE_DIR / "data"))

DATASET = "middle_earth"


# ---------- Our schema ----------
# Cognee's default KnowledgeGraph lets the LLM invent any node type. We narrow it to six types
# and add instructions in the field descriptions (the LLM sees these descriptions).

class MiddleEarthNode(Node):
    name: str = Field(description=(
        "The entity's most common full name, e.g. 'Aragorn' (not 'Strider' or 'Elessar'), "
        "'Gandalf' (not 'Mithrandir'). Always use the same name for the same entity."))
    type: Literal["Character", "Race", "Place", "Faction", "Event", "Artifact"] = Field(
        description="Character = a person or creature with a name; Race = a people (Elves, Hobbits); "
                    "Place = a location or realm; Faction = a group or order (Fellowship, Istari); "
                    "Event = a battle, war or quest; Artifact = a named object or material (One Ring, Andúril, mithril).")


class MiddleEarthEdge(Edge):
    relationship_name: Literal[
        "member_of", "leader_of", "ruler_of", "serves", "ally_of", "enemy_of",
        "child_of", "sibling_of", "married_to", "belongs_to_race",
        "located_in", "part_of", "created", "wields", "made_of",
        "participated_in", "killed", "also_known_as",
    ] = Field(description="Pick the closest relationship from the list.")


class MiddleEarthGraph(KnowledgeGraph):
    nodes: list[MiddleEarthNode] = Field(
        default_factory=list,
        description="At most 25 of the most important entities in this text.")
    edges: list[MiddleEarthEdge] = Field(
        default_factory=list,
        description="At most 40 of the most important relationships in this text.")


# ---------- Helpers ----------

def pick_files(args):
    if args.all:
        return sorted(RAW_DIR.glob("*.txt"))
    paths = [RAW_DIR / f"{title}.txt" for title in args.titles]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"Not found in {RAW_DIR}: {missing}")
    return paths


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("titles", nargs="*", help="article titles to ingest, e.g. Aragorn Gandalf")
    parser.add_argument("--all", action="store_true", help="ingest every file in data/raw")
    parser.add_argument("--estimate", action="store_true", help="only estimate LLM calls and tokens")
    parser.add_argument("--reset", action="store_true", help="delete the whole graph first")
    args = parser.parse_args()

    if args.reset:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        print("Graph and stored files deleted.")
        if not (args.all or args.titles):
            return

    paths = pick_files(args)
    if not paths:
        raise SystemExit("No files given. Pass titles or --all.")

    # 1. add: copy the files into Cognee's storage and register them in the dataset.
    #    Files that were already added are skipped.
    print(f"Adding {len(paths)} file(s) to dataset '{DATASET}'...")
    await cognee.add([str(p) for p in paths], dataset_name=DATASET)

    # 2a. Estimate only: count chunks and tokens without calling the LLM.
    if args.estimate:
        estimate = await cognee.cognify(datasets=[DATASET], graph_model=MiddleEarthGraph, dry_run=True)
        print(estimate)
        return

    # 2b. cognify: chunk -> extract nodes and edges with our schema -> merge -> store graph + vectors.
    #     Documents that were already processed are skipped (incremental loading).
    print("Building the graph (this calls the LLM; it can take a few minutes)...")
    await cognee.cognify(datasets=[DATASET], graph_model=MiddleEarthGraph)

    # 3. Save an interactive picture of the graph that opens in the browser.
    out = DATA_DIR / "graph.html"
    # max_nodes: the default (500) silently hides part of the graph.
    await cognee.visualize_graph(str(out), dataset=DATASET, max_nodes=3000)
    print(f"Done. Open {out} in your browser to see the graph.")


if __name__ == "__main__":
    asyncio.run(main())
