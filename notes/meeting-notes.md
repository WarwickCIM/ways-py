# Meeting notes

# 16 December 2021

## Packaging/deployment

- latest version (0.1.1) uploaded to PyPI -- linked to from GitHub repo
- API documentation (linked from PyPI page and README.md)
- will do a final wrap-release with some final documentation tweaks
- notebooks in Binder (unfortunately Binder takes forever, so not necessarily useful)

## Functionality and examples
- @altair_color_viz decorator which works with any Altair chart with colour-encoded data
- @altair_color_widgets decorator adds widgets for exploring colour settings

## Example notebooks
- `usa-presidential-poll.ipynb` illustrating @altair_color_viz with choropleth
- expository text/walkthrough explaining WAYS motivation
- attaches a "metavisualisation" which shows distribution of data over colour bins
- no "unused colours" functionality -- turns out to be tricky to implement generically
- shows @altair_color_widgets and encourages reader to explore settings
- also shows how to integrate custom widgets (e.g. to control data ranges) with colour widgets

- `simple.ipynb` shows same colour meta-visualisation working with scatterplot

# 15 October 2021

## Progress on choropleth example

- package created, CI/CD infrastructure set up
- test infrastructure for Altair which checks for JSON-equivalence to stored image
- define our own @meta_hist decorator wraps in existing chart in additional (meta-)visualisations
- experiment using @interact decorator in Jupyter to allow user to interact with settings

# 16 September 2021

Present: Greg, James, Ed, Roly

Actions
- Greg to send supporting materials (images, etc)
- James to send example notebooks
- Ed and Roly to look at choropleth example in Altair/Geopandas
