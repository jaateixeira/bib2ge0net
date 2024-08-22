# bib2ge0net
From a given list of references (.bib format), extracts a geographical collaboration map

# How it works 

If the entry have a doi, it uses  DOI REST API allows programmatic access information about affiliation. 
If the entry does not have a doi, it it will look for the affiliation key. 

Here are two examples of entries with a affiliation key

'''
@book{key1,
  author = {Author, A.},
  year = {2021},
  title = {Title of the Book},
  publisher = {Publisher},
  address = {Address of the Publisher},
  affiliation = {University of XYZ}
}

@book{key2,
  author = {Author, A. and Author, B.},
  year = {2021},
  title = {Title of the Book},
  publisher = {Publisher},
  address = {Address of the Publisher},
  affiliation = {University of XYZ, University of CBA}
}


'''
