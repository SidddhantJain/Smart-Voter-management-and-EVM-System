from pathlib import Path

from pyvis.network import Network


def build_graph(output_path: Path) -> None:
    net = Network(
        height="800px",
        width="1200px",
        directed=True,
        bgcolor="#ffffff",
        font_color="#222",
    )

    # Nodes
    net.add_node(
        "Voter",
        shape="icon",
        icon={"face": "user", "code": "f007"},
        color="#8fd3f4",
        title="Actor: Voter",
    )
    net.add_node(
        "Encrypt", shape="box", color="#4db6ac", title="Fernet encryption step"
    )
    net.add_node(
        "Vote TX", shape="ellipse", color="#f9a825", title="Encrypted vote transaction"
    )
    net.add_node("Mempool", shape="box", color="#e0e0e0", title="Pending pool")
    net.add_node("Block #102", shape="box", color="#9575cd", title="New block")
    net.add_node("Block #101", shape="box", color="#7986cb", title="Previous block")
    net.add_node("Block #100", shape="box", color="#64b5f6", title="Previous block")
    net.add_node("Blockchain", shape="database", color="#90a4ae", title="Ledger")

    # Edges
    net.add_edge("Voter", "Encrypt", title="Prepare payload")
    net.add_edge("Encrypt", "Vote TX", title="Encrypted payload")
    net.add_edge("Vote TX", "Mempool", title="Queued for inclusion")
    net.add_edge("Mempool", "Block #102", title="Included in block")
    net.add_edge("Block #102", "Blockchain", title="Appended to chain")
    net.add_edge("Block #101", "Block #102", title="Prev → Next")
    net.add_edge("Block #100", "Block #101", title="Prev → Next")

    # Styling physics
    net.set_options("""
        {
            "nodes": { "shape": "box", "shadow": true, "font": { "size": 18 } },
            "edges": { "arrows": { "to": { "enabled": true } }, "smooth": { "type": "dynamic" } },
            "physics": { "enabled": true, "solver": "forceAtlas2Based", "stabilization": { "iterations": 50 } }
        }
        """)

    net.write_html(output_path.as_posix())
    print(f"[PyVis] Saved interactive graph: {output_path}")


def main():
    repo_root = Path(__file__).resolve().parents[2]
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    out = docs_dir / "vote_blockchain_graph.html"
    build_graph(out)


if __name__ == "__main__":
    main()
