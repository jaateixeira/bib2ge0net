import argparse
import networkx as nx
import matplotlib.pyplot as plt
import bibtexparser
from geopy.geocoders import Nominatim
import requests
from mpl_toolkits.basemap import Basemap
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.traceback import install

# Install rich traceback handler
install()

def parse_bib_file(file_path):
    logger.info(f"Parsing BibTeX file: {file_path}")
    with open(file_path) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return bib_database.entries

def get_affiliations_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        authors = data.get('message', {}).get('author', [])
        affiliations = {}
        for author in authors:
            name = f"{author.get('given', '')} {author.get('family', '')}".strip()
            if name:
                affiliations[name] = author.get('affiliation', [])
        return affiliations
    logger.warning(f"Failed to retrieve affiliations from DOI: {doi}")
    return {}

def extract_authors_and_affiliations(entries):
    authors_affiliations = {}
    for entry in entries:
        doi = entry.get('doi', '')
        if doi:
            affiliations = get_affiliations_from_doi(doi)
            if not affiliations:
                affiliations = extract_affiliations_from_bibtex(entry)
        else:
            affiliations = extract_affiliations_from_bibtex(entry)

        for author, affs in affiliations.items():
            if author not in authors_affiliations:
                authors_affiliations[author] = set()
            authors_affiliations[author].update(affs)
    return authors_affiliations

def extract_affiliations_from_bibtex(entry):
    authors = entry.get('author', '').split(' and ')
    affiliations = entry.get('affiliation', '').split(', ')
    author_affiliations = {}
    for author in authors:
        author_affiliations[author] = affiliations[:3]  # Limit to max 3 affiliations
    return author_affiliations

def get_coordinates(affiliation):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(affiliation)
    if location:
        return (location.latitude, location.longitude)
    logger.warning(f"Failed to geocode affiliation: {affiliation}")
    return None

def plot_geographical_network(authors_affiliations):
    G = nx.Graph()
    coordinates = {}

    for author, affiliations in authors_affiliations.items():
        for affiliation in affiliations:
            coord = get_coordinates(affiliation)
            if coord:
                coordinates[author] = coord
                G.add_node(author, pos=coord)

    for author1, affiliations1 in authors_affiliations.items():
        for author2, affiliations2 in authors_affiliations.items():
            if author1 != author2 and set(affiliations1) & set(affiliations2):
                G.add_edge(author1, author2)

    # Create a world map background
    fig, ax = plt.subplots(figsize=(12, 8))
    m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=85,
                llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='c')
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='lightgray', lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # Convert coordinates to map projection coordinates
    pos = {node: m(*data['pos']) for node, data in G.nodes(data=True)}

    # Draw the network on the map
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=50, node_color='blue')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='red')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)

    plt.show()

def main(bib_file_path):
    logger.info(f"Starting script with BibTeX file: {bib_file_path}")
    entries = parse_bib_file(bib_file_path)
    authors_affiliations = extract_authors_and_affiliations(entries)

    console = Console()
    table = Table(title="Authors and Affiliations")
    table.add_column("Author", justify="left", style="cyan")
    table.add_column("Affiliations", justify="left", style="magenta")

    for author, affiliations in authors_affiliations.items():
        table.add_row(author, ", ".join(affiliations))

    console.print(table)

    plot_geographical_network(authors_affiliations)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot geographical social networks from a BibTeX file.")
    parser.add_argument("bib_file", type=str, help="Path to the BibTeX file")
    args = parser.parse_args()

    main(args.bib_file)


