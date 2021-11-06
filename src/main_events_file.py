print(__doc__)

#########################################################################
# Define the onset times in seconds. Those are typically extracted
# from the stimulation software used.
import numpy as np
onset = 30.0 * np.arange(100.)

#########################################################################
# Associated trial types: these are numbered between 0 and 9, hence
# correspond to 10 different conditions.
trial_idx = np.mod(np.arange(100), 2)

#########################################################################
# We may want to map these indices to explicit condition names.
# For that, we define a list of 10 strings.
condition_ids = ['rest', 'active']

trial_type = np.array([condition_ids[i] for i in trial_idx])

#########################################################################
# We also define a duration (required by BIDS conventions).
duration = 30*np.ones_like(onset)


#########################################################################
# Form an event dataframe from these information.
import pandas as pd
events = pd.DataFrame({'trial_type': trial_type,
                       'onset': onset,
                       'duration': duration})

#########################################################################
# Export them to a tsv file.
tsvfile = 'ajc_events.tsv'
events.to_csv(tsvfile, sep='\t', index=False)
print("Created the events file in %s " % tsvfile)

#########################################################################
# Optionally, the events can be visualized using the plot_event function.
from matplotlib import pyplot as plt
from nilearn.plotting import plot_event
plot_event(events, figsize=(15, 5))
plt.savefig('events.png')

print('done')

