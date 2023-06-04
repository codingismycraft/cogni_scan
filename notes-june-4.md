## Modified the front end of cogni viewer, now it reads 
from the database instead of flat files.

For this we had to manually create the universe of the mris 
for oasis3 and import them to the db using a custom script.

## The tricky part is the health status flag of the MRI that 
currenlty as we have them they do not match the original flags
and this can happen because we are missing cases where the first
clinincal diganosis in not followed by an MRI. We also created 
a jupyter notebook to make it easy to understand. This needs
to be fixed.

## We examined the ADNI data set and we found out that there
are approximately 30 coverted cases.  The related data are stored
in a db called adni.db under the ADNI directory.

## To view the ADNI status changes:

Select PTID, Dx, EXAMDATE from clinical_data  order by PTID, EXAMDATE


Running this select revealed to us the patients who entered 
healthy and exited with dementia:

Select distinct PTID from clinical_data where DX = 'NL' and PTID in
(Select distinct (PTID) from clinical_data where DX='Dementia')

The corresponding patent id are the following:

```
002_S_4262, 003_S_1074, 005_S_0223, 012_S_5121, 014_S_0548, 014_S_0558,
016_S_2007, 021_S_0984, 023_S_0061, 024_S_0985, 029_S_0843, 029_S_4385,
033_S_0920, 033_S_1098, 035_S_0555, 037_S_0467, 037_S_4706, 041_S_0898,
041_S_4041, 051_S_1123, 098_S_4506, 114_S_0166, 116_S_1249, 123_S_0106,
127_S_0112, 127_S_0259, 128_S_0230, 129_S_0778, 131_S_0123, 137_S_0972,
```

## Using the following page:
```
https://ida.loni.usc.edu/pages/access/search.jsp?tab=simpleSearch&project=ADNI&page=DOWNLOADS&subPage=IMAGE_COLLECTIONS
```

we were able to discover the MRIs for the specific patients that we
are interested in.


## TODO LIST

- Finalize the front end that: will allow us to homogeniaze all MRIs
- 
- Download the MRIs from ADNI and imprort them to the database
    
We should download all the scans that we will fit to the converted
patients plus a proportional number of scane for healthy-healty.

- Immport the (few) data from the OASIS2 (if we can find then useful) and 
import them to the database.

- Go through all the scans and adjust axis - orientation using the front end.
























