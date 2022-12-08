import numpy as np
import matplotlib.pyplot as plt

import helper
import flowrate_hm as fhm


wave_no = 0

# exp_i is the input model (providing plausible model parameters)
# exp_j is the output model (that we using to predict)

# Note the parameters are in the same order in all experiments,
# so only parameter indexes are needed.

f_exit_time, f_coef = 0, 1
method_names = ('exit', 'coef')


def get_plaus_idxs(exp_id, method):
    if method == f_exit_time:
        results = helper.load_results(exp_id)[wave_no]
        plaus_idxs = [x for x in range(200) if results['implaus_scores'][x] < 3]
    elif method == f_coef:
        fhm.exp_id = exp_id
        plaus_idxs = fhm.get_coef_plaus_TS_indexes()
    return plaus_idxs


def five_by_five(method=f_exit_time):
    fig, axs = plt.subplots(5, 5, sharex=True, sharey=False, figsize=(12, 8))
    plaus_idxs = [get_plaus_idxs(helper.EXP_IDS[i], method) for i in range(5)]
    for exp_i in range(5):
        # get the samples that were plausible for model i
        plaus_idxs_i = plaus_idxs[exp_i]
        for exp_j in range(5):
            obs = helper.OBS[helper.EXP_IDS[exp_j]]
            # get the outputs for model j using the parameters that fit model i
            results = helper.load_results(helper.EXP_IDS[exp_j])[wave_no]
            outputs_j_from_i = [results['outputs'][idx] for idx in plaus_idxs_i if results['outputs'][idx] != 120]
            # for comparison, get the outputs for model j using the parameters that fit model j
            plaus_idxs_j = plaus_idxs[exp_j]
            outputs_j_from_j = [results['outputs'][idx] for idx in plaus_idxs_j if results['outputs'][idx] != 120]
            axs[exp_i][exp_j].hist(outputs_j_from_j, alpha=0.8)
            axs[exp_i][exp_j].hist(outputs_j_from_i, alpha=0.5)
            axs[exp_i][exp_j].axvline(x=obs, ymin=0, ymax=1, c='r')
            axs[exp_i][exp_j].set_xlim(20, 120)
    for idx in range(5):
        axs[0][idx].set_title(str(idx+1))
        axs[idx][0].set_ylabel(str(idx+1), rotation=0, size='large', labelpad=8)
    plt.text(-540, 50, 'Input model exp.', rotation=90)
    #plt.text(-230, 175, 'Output model exp.')
    plt.text(-230, -20, 'Exit time')
    plt.show()


def one_by_five(method=f_exit_time):
    fig, axs = plt.subplots(1, 5, figsize=(12, 3))
    plaus_idxs = [get_plaus_idxs(helper.EXP_IDS[i], method) for i in range(5)]
    for exp_j in range(5):
        plaus_idxs_i = []
        # get the samples that were plausible for all models other than j
        for exp_i in (i for i in range(5) if i != exp_j):
            plaus_idxs_i.extend(plaus_idxs[exp_i])
        results = helper.load_results(helper.EXP_IDS[exp_j])[wave_no]
        # get the outputs for model j using the parameters that fit the other models
        outputs_j_from_i = [results['outputs'][idx] for idx in plaus_idxs_i if results['outputs'][idx] != 120]
        # for comparison, get the outputs for model j using the parameters that fit model j
        plaus_idxs_j = plaus_idxs[exp_j]
        outputs_j_from_j = [results['outputs'][idx] for idx in plaus_idxs_j if results['outputs'][idx] != 120]
        axs[exp_j].hist(outputs_j_from_j)
        axs[exp_j].hist(outputs_j_from_i, alpha=0.5)
        obs = helper.OBS[helper.EXP_IDS[exp_j]]
        axs[exp_j].axvline(x=obs, ymin=0, ymax=1, c='r')
        # axs[exp_j].axvline(x=np.mean(outputs_j_from_i), ymin=0, ymax=1, c='orange')
        # axs[exp_j].axvline(x=np.mean(outputs_j_from_j), ymin=0, ymax=1, c='blue')
        axs[exp_j].set_xlim(20, 120)
        axs[exp_j].set_title(str(exp_j+1))
    plt.text(-230, -10, 'Exit time')
    fig.subplots_adjust(bottom=0.2)
    plt.show()


def one_by_five_subset(method=f_exit_time):
    fig, axs = plt.subplots(1, 5)
    plaus_idxs = [None, None, None, None, None]
    for i in (0, 2, 3):
        plaus_idxs[i] = get_plaus_idxs(helper.EXP_IDS[i], method)
    for exp_j in (0, 2, 3):
        plaus_idxs_i = []
        # get the samples that were plausible for all models other than j
        for exp_i in (i for i in (0, 2, 3) if i != exp_j):
            plaus_idxs_i.extend(plaus_idxs[exp_i])
        results = helper.load_results(helper.EXP_IDS[exp_j])[wave_no]
        # get the outputs for model j using the parameters that fit the other models
        outputs_j_from_i = [results['outputs'][idx] for idx in plaus_idxs_i if results['outputs'][idx] != 120]
        # for comparison, get the outputs for model j using the parameters that fit model j
        plaus_idxs_j = plaus_idxs[exp_j]
        outputs_j_from_j = [results['outputs'][idx] for idx in plaus_idxs_j if results['outputs'][idx] != 120]
        axs[exp_j].hist(outputs_j_from_j)
        axs[exp_j].hist(outputs_j_from_i, alpha=0.5)
        obs = helper.OBS[helper.EXP_IDS[exp_j]]
        axs[exp_j].axvline(x=obs, ymin=0, ymax=1, c='r')
        # axs[exp_j].axvline(x=np.mean(outputs_j_from_i), ymin=0, ymax=1, c='orange')
        # axs[exp_j].axvline(x=np.mean(outputs_j_from_j), ymin=0, ymax=1, c='blue')
        axs[exp_j].set_xlim(20, 120)
        axs[exp_j].set_title(str(exp_j+1))
    plt.text(-230, -10, 'Exit time')
    fig.subplots_adjust(bottom=0.2)
    plt.title(method_names[method])
    plt.show()


if __name__ == '__main__':
    #five_by_five(f_exit_time)
    #one_by_five(f_exit_time)
    one_by_five_subset(f_coef)
