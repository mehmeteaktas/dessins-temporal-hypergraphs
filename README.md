# Dessins d'Enfants as a Topological Lens on Temporal Hypergraphs

Code for the paper *Dessins d'Enfants as a Topological Lens on Temporal Hypergraphs* by Mehmet Emin Aktas and Esra Akbas.

A hypergraph whose incidences carry a cyclic order at every vertex and inside every hyperedge is a dessin d'enfant (a hypermap), and therefore a surface with faces and a genus. Its cycle rank splits exactly into local cycles, which bound faces, and global cycles, which run around handles: β₁ = (F − c) + 2g. The **growing dessin** builds this surface from the history of a temporal hypergraph. Incidences are inserted one at a time in time order, each next to the earlier incidence it is related to (its *anchor*), and every insertion is classified exactly as *new*, *pendant*, *bridge*, *local* or *handle*.

## Repository layout

```
dessins/                 the method (no dependency on the data)
  online_dessin.py       growing dessin: incremental rotation system, faces, event classification
  growth.py              insertion rules (reply, hub, random), event traces, order-free statistics
  facemax.py             offline face maximization (heuristic minimum-genus embedding, the "ceiling")
  stackexchange.py       Stack Exchange dump -> temporal hypergraph; static (timestamp) rotations
experiments/             scripts that produce the paper's results
  config.py              data and results locations, the five communities
  get_data.py            download and extract the Stack Exchange data
  toy_example.py         Tables 1 and 3 (the toy hypergraph and the worked example)
  run_growth.py          main experiment: three insertion rules, shuffled ablation, bracketing
  negative_control.py    rotations read directly from the data (Section 6.3)
  make_figures.py        Figures 3, 5, 6, 7 and the numbers of Tables 6-8
matlab/                  MATLAB versions of the paper's figures (data embedded in each script)
tests/                   randomized correctness tests
```

## Installation

Python 3.9 or later.

```bash
pip install -r requirements.txt
```

The method itself (`dessins/`) uses only the Python standard library and NumPy.

## Using the growing dessin on your own data

The input is a time-ordered list of events `(vertex, hyperedge, anchor_vertex)`, one per first incidence of a vertex in a hyperedge. `anchor_vertex` is the earlier member of the hyperedge that the new incidence relates to, or `None`.

```python
from dessins.growth import run_rule

events = [(1, "a", None), (2, "a", 1), (3, "a", 1), (1, "b", None),
          (2, "b", 1), (4, "b", 1), (3, "c", None), (4, "c", 3)]
D, trace, _ = run_rule(events, "reply-pendant", seed=0)   # or "hub-pendant", "random-pendant"
print(trace)                    # ['new', 'pendant', 'pendant', 'pendant', 'local', 'pendant', 'pendant', 'handle']
print(D.F, D.c, D.genus())      # faces, components, genus: 1 1 1
```

At any time, β₁ equals the number of local plus handle events, the genus equals the number of handle events, and F − c equals local minus handle events (Corollary 4.3). The net local faces per 100 cycles used in the paper is λ = 100 (F − c) / β₁.

## Reproducing the paper

**1. Data.** The experiments use five communities from the public [Stack Exchange data dump](https://archive.org/details/stackexchange) (data until 31 March 2024; CC BY-SA 4.0): Data Science, Artificial Intelligence, Biology, Astronomy and Academia. Only `Posts.xml` and `Comments.xml` of each site are needed.

```bash
python -m experiments.get_data
```

This downloads `<site>.7z` from the Internet Archive and extracts the two files into `data/<Community>/`. If the download fails, download the archives manually from the Internet Archive into `data/` and run the command again. To keep the data elsewhere, set `DESSINS_DATA=/path/to/data`. Results go to `results/`, or to `DESSINS_RESULTS` if set.

**2. Toy example** (Tables 1 and 3, instant):

```bash
python -m experiments.toy_example
```

**3. Main experiment and figures:**

```bash
python -m experiments.run_growth        # all five communities; resumable
python -m experiments.make_figures      # results/figures/*.pdf and results/numbers.json
```

A single run over the full history takes about 15 seconds for Data Science (99,140 events) and about two minutes for Academia (308,289 events) on one CPU core. The face-maximization ceiling on the bracketing samples takes most of the remaining time. Use `--sites AI` to run a single community, and `--seeds` and `--samples` to run fewer repetitions (the paper uses 2 and 5).

**4. Negative control** (Section 6.3):

```bash
python -m experiments.negative_control  # Data Science and Biology, samples of 250-2,000 threads
```

All random choices are seeded, so the scripts reproduce the paper's numbers exactly.

**5. Tests:**

```bash
python -m pytest tests          # or: python -m tests.test_facemax
```

The tests check, on thousands of random event sequences, that the incrementally maintained faces equal a full recount and that the conservation law holds exactly. They also check that face maximization finds the exact optimum on the 40 small hypergraphs whose optimum is computed by enumerating all rotation systems.

## MATLAB figures

Each script in `matlab/` contains the plotted numbers and the plotting code for one figure of the paper. Running a script writes a PDF of the figure. The scripts need MATLAB R2020b or later (`tiledlayout`, `exportgraphics`).

## Citation

If you use this code, please cite the paper (see `CITATION.cff`):

```bibtex
@article{AktasAkbas2026dessins,
  author  = {Aktas, Mehmet Emin and Akbas, Esra},
  title   = {Dessins d'Enfants as a Topological Lens on Temporal Hypergraphs},
  journal = {arXiv preprint},
  year    = {2026}
}
```

## License

Code: MIT License (see `LICENSE`). The Stack Exchange data are licensed under CC BY-SA 4.0 by Stack Exchange, Inc. and are not redistributed here.
