#!/usr/bin/env python
#coding=utf-8

import os
import numpy as np
import spike_sort as sort
import spike_sort.io.hdf5
from spike_sort.ui.manual_detect import find_spikes

if __name__ == "__main__":
    
    DATAPATH = os.environ.get("DATAPATH")
    h5_fname = os.path.join(DATAPATH, "hdf5/gollum_test.h5")
    sp_win = [-0.3, 0.8]
    response_win = [8., 13.]
    
    dataset = "/Gollum/s39gollum01/el1/cell2"
    spike_type = "positive"
    stim_node = "/".join(dataset.split('/')[:3]+['stim'])
    
    sp = sort.io.hdf5.read_sp(h5_fname, dataset)
    spt = sort.io.hdf5.read_spt(h5_fname, dataset)
    stim = sort.io.hdf5.read_spt(h5_fname, stim_node)
    if spike_type=='positive':
        spt = sort.extract.align_spikes(sp, spt, sp_win, 'max')
    elif spike_type == "negative":
        spt = sort.extract.align_spikes(sp, spt, sp_win, 'min')
   
    spike_waves = sort.extract.extract_spikes(sp, spt, sp_win)
    spt_noise = sort.evaluate.detect_noise(sp, spt, sp_win,
            spike_type, 3000)
    noise_waves = sort.extract.extract_spikes(sp, spt_noise, sp_win)

    isolation_score = sort.evaluate.calc_isolation_score(spike_waves,
            noise_waves, spike_type, lam=10,max_spikes=2000.)
    snr_spike =  sort.evaluate.snr_spike(spike_waves)

    
    spt_all, clust_idx = sort.extract.merge_spiketimes(spt, spt_noise)
    all_spikes = sort.extract.extract_spikes(sp, spt_all, sp_win)
    

    features = sort.features.combine(
            (
            sort.features.fetSpIdx(all_spikes),
            sort.features.fetP2P(all_spikes),
            sort.features.fetPCs(all_spikes)))

    sort.plotting.plot_spikes(all_spikes, clust_idx, plot_avg=True, n_spikes=800.)

    sort.plotting.figure()
    sort.plotting.plot_features(features, clust_idx)



    print "N/spikes = ", spike_waves['data'].shape, "N/noise =", noise_waves['data'].shape
    print "SNR_{spk} (spike) =", sort.evaluate.snr_spike(spike_waves)
    print "SNR_{spk} (noise) =", sort.evaluate.snr_spike(noise_waves)
    print "Isolation Score = ", isolation_score


    sort.plotting.show()


