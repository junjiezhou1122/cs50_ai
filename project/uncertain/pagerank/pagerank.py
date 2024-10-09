import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prop_dist = {}

    dict_len = len(corpus)
    page_len = len(corpus[page])

    if page_len < 1:
        for key in corpus.keys():
            prop_dist[key] = 1 / dict_len

    else:
        random_factor = (1 - damping_factor) / dict_len
        even_factor = damping_factor / page_len

        for key in corpus.keys():
            if key in corpus[page]:
                prop_dist[key] = random_factor + even_factor
            else:
                prop_dist[key] = random_factor

    return prop_dist

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize sample_dict with zero counts for each page
    sample_dict = {page: 0 for page in corpus}

    sample = None

    for _ in range(n):
        if sample:
            dist = transition_model(corpus, sample, damping_factor)
            dist_lst = list(dist.keys())
            dist_weights = [dist[i] for i in dist_lst]
            sample = random.choices(dist_lst, weights=dist_weights, k=1)[0]
        else:
            # For the first iteration, choose a random page
            sample = random.choice(list(corpus.keys()))

        sample_dict[sample] += 1

    # Convert counts to probabilities
    total_samples = sum(sample_dict.values())
    return {page: count / total_samples for page, count in sample_dict.items()}

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = corpus.keys()
    N = len(pages)
    
    # Initialize PageRank values
    pagerank = {page: 1 / N for page in pages}
    
    while True:
        new_pagerank = {}
        max_change = 0
        
        for page in pages:
            new_rank = (1 - damping_factor) / N
            for linking_page in pages:
                if page in corpus[linking_page]:
                    new_rank += damping_factor * pagerank[linking_page] / len(corpus[linking_page])
                elif not corpus[linking_page]:
                    # If page has no outgoing links, it should be treated as having one link to every page (including itself)
                    new_rank += damping_factor * pagerank[linking_page] / N
            
            new_pagerank[page] = new_rank
            max_change = max(max_change, abs(new_pagerank[page] - pagerank[page]))
        
        pagerank = new_pagerank
        
        if max_change < 0.001:
            break
    
    # Normalize the PageRank values
    total = sum(pagerank.values())
    return {page: rank / total for page, rank in pagerank.items()}

if __name__ == "__main__":
    main()
