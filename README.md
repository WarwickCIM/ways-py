<!-- badges: start -->

[![Release build](https://github.com/WarwickCIM/ways-py/actions/workflows/build-publish.yml/badge.svg?branch=release)](https://github.com/WarwickCIM/ways-py/actions/workflows/build-publish.yml)
[![Develop build](https://github.com/WarwickCIM/ways-py/actions/workflows/build-publish.yml/badge.svg?branch=develop)](https://github.com/WarwickCIM/ways-py/actions/workflows/build-publish.yml)
[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- badges: end -->

# _WAYS: What Aren't You Seeing_

Python package for the [WAYS](https://www.turing.ac.uk/research/research-projects/ways-what-arent-you-seeing) project.

[Turing Research Engineering Group Hut23 issue](https://github.com/alan-turing-institute/Hut23/issues/407)

“As you can see in figure 1…” may well be the most frequently made claim in science. But unlike claims concerning data, statistics, models and algorithms, those relating to visualisations are rarely evaluated or verified. So how can data scientists understand visualisations’ effectiveness and expressiveness? What is the visualisation equivalent of q-q plots, R^2 and K-folds tests?

Designing effective visualisations goes far beyond selecting a graph, scales and a ‘pretty’ style. Effective visualisations must negotiate sensitivities and interactions between visual elements (e.g. encodings, coordinate systems, guides, annotations), data (e.g. characteristics, transformations, partitions), and the discriminator function, which in this case is the perceptual and cognitive systems of humans. Despite their criticality, these methodological and design considerations are rarely surfaced, limiting the value extracted from visualisations. What does figure 1 actually visualise?

The ‘What Aren’t You Seeing’ (WAYS) project addresses 1) what we aren’t seeing in visualisations by 2) revealing the relevant knowledge, theory and practices that we are not seeing at the site of visualisation production. Our final goal is the WAYS package/library in which the properties, outcomes and affordances of visualisation designs are depicted through visualisations; a concept we term ‘Precursor Visualisations’. WAYS then addresses the challenge of generating a productive interplay between everyday visualisation work and the epistemology, practice, communication techniques and evaluation methods that should inform visualisation design at source (Robinson). To achieve this, we propose three work packages (WP1-3).

# Quick start

Install from [PyPI](https://pypi.org/project/ways-py/) using `pip install ways-py`.

# Emojis on commit messages

We use the following `git` aliases (add to `[alias]` section of your `.gitconfig` to have these):

```
doc      = "!f() { git commit -a -m \"📚 : $1\"; }; f"
fix      = "!f() { git commit -a -m \"🐛 : $1\"; }; f"
lint     = "!f() { git commit -a -m \"✨ : $1\"; }; f"
modify   = "!f() { git commit -a -m \"❗ : $1\"; }; f"
refactor = "!f() { git commit -a -m \"♻️ : $1\"; }; f"
```
