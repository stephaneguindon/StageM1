##### BEAST analysis

We reconstructed time-calibrated epidemic histories using a Bayesian statistical framework implemented in the BEAST software (version 1.10.4, Suchard et al., 2018). BEAST uses Markov Chain Monte Carlo integration to average over all plausible evolutionary histories for the data, as reflected by the posterior probability. All analyses were performed using the BEAGLE library to enhance computation speed (Suchard and Rambaut 2009; Ayres et al., 2012). We specified an HKY85 substitution model with a discretized gamma distribution (four categories) to model rate heterogeneity across sites. To accommodate variation of rates across lineages an uncorrelated relaxed molecular clock that models the branch rate variation according to a lognormal distribution was specified (Drummond et al., 2006). The flexible nonparametric demographic skygrid prior was selected to accommodate for variation in the rate of coalescence (Gill et al., 2013). Stationarity and mixing (e.g. based on effective sample sizes >200 for the continuous parameters) were examined using Tracer version 1.7 (Rambaut et al., 2018). The MCC trees were summarized using TreeAnnotator version 1.10.4 (Suchard et al., 2018). 

To study the geographical spread of RYMV in continuous space in West Africa and to quantify its tempo and dispersal, we fitted a continuous phylogenetic diffusion model to the West African data set, modelling the changes in coordinates (latitude and longitude) along each branch in the evolutionary history as a bivariate normal random deviate (Lemey et al., 2010). As a more realistic alternative to homogeneous Brownian motion, we adopted a relaxed random walk (RRW) extension that models variation in dispersal rates across branches by independently drawing branch-specific rate scalers of the RRW precision matrix from a Cauchy distribution to relax the assumption of a constant spatial diffusion rate throughout the whole tree (Lemey et al., 2010). Bayesian inference using continuous diffusion models yields a posterior distribution of the phylogenetic trees, each having ancestral nodes annotated with location estimates. The WA261 data set was used to reconstruct the dispersal of RYMV throughout West Africa and Central Africa. A spatial jitter of 10 km was applied to the locations of the isolates. This degree of noise for identical coordinates was needed to avoid improper posteriors under the RRW model and associated inference problems (Fernandez and Steel 2000, Lemey et al., 2010). 

##### MCC Tree BEAST submission:

1. Parse a Nexus file MCC Tree, with: augur import beast (--tip-date-regex \[0\-9\]{4})
```
This command is used to transform a nexus file to a displayable format under auspice.
It will provide 2 JSON files, one contains MCC Tree topology and the other one gets every node data. 
\--tip-date-regex [0-9]{4} is used to extract isolates dates from sample names. It will then be stored in the node data JSON file.
```
2. Use of [find.py](https://github.com/KelianP/StageM1/blob/dcb8a101f88024d7ec72cbd2e97f4fc3b36ab774/data/find.py) to complete WA261 metadata
```
In our case, dating and discretized locations are still encoded within sample names.
This script takes a 3 columns tabulated separated values (TSV) file which includes sample names, latitudes and longitudes for each isolates.
It returns this file in which are added 2 columns, one refers to the country and the other refers to the date extracted from the sample names.
```
3. Discretize the OUTPUT_NODE_DATA file using [DiscretizeMCC](https://github.com/KelianP/StageM1/blob/dcb8a101f88024d7ec72cbd2e97f4fc3b36ab774/scripts/Discretize_MCC.py)
```
DiscretizeMCC is a tool that discretize uncertain and continuous geographical node data.
It will keep the node data JSON file structure to make it usable in augur export v2.
In this way, we can use MCC BEAST Tree in Nextstrain and we allow auspice to display it.
```
4. Correction of "locations" induced by BEAST's Jitter using [ignore\_jitter.py](https://github.com/KelianP/StageM1/blob/dcb8a101f88024d7ec72cbd2e97f4fc3b36ab774/scripts/ignore_jitter.py)
```
BEAST's Jitter induced an unwarranted change of the country of sequence collection.
So ignore\_jitter.py will solve these changes using a reverse geocoding method on exact sample coordinates.
The resulting file will be a node data JSON file with corrects locations.
```
5. Writing of auspice\_config.json according to the desired displays and filters
```
This JSON allows the maintainer to setup displays, filters and parameters under auspice.
```
6. Transformation into a file interpretable by Auspice with augur export v2
```
augur export v2 is used to concatenate every needed metadata (TSV), display configurations (JSON), node data (JSON), tree topology (JSON).
And so, to create an auspice displayable abstract (JSON).
```
##### Discretization methods

As mentionned above, the analysis of that data set was conducted under a RRW model
where the habitat is considered as continuous rather than discretized into distinct
demes. Bayesian inference under RRW models reconstructs the most probable location of
ancestral lineages. These ancestral locations define polygons where the area within
each polygon correspond to a (posterior) probability of 0.8 that the ancestral lineage
occupied this area (with probability 0.2 the lineage lived outside that particular
area). In order to transform these polygons into the corresponding probabilities of
different countries, we counted, for each internal node and each country, the number
of vertices of each polygon associate to this node. The probability associated to
each country for then obtained by dividing this count by the total number of vertices
defining the polygon(s) characterizing the ancestral node of interest.

##### References

>Ayres, D. et al. (2012) ‘BEAGLE: An Application Programming Interface and High-performance Computing Library for Statistical Phylogenetics’, Systematic Biology, 61: 170–3.

>Drummond, A. et al. (2006) ‘Relaxed Phylogenetics and Dating with Confidence’, PLoS Biology, 4: e88

>Fernandez, C., and Steel, M. (2000) ‘Bayesian Regression Analysis with Scale Mixtures of Normals’, Econometric Theory, 16: 80–101.

>Gill, M. et al. (2013) ‘Improving Bayesian Population Dynamics Inference: A Coalescent-based Model for Multiple Loci’, Molecular Biology and Evolution, 30: 713–24.
