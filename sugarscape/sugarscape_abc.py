import numpy as np
import pickle
import shelve
import matplotlib.pyplot as plt

import pyabc

from sugarscape_cg.model import SugarscapeCg


# Run ID generated from history matching to store the results
id = '210129_114432'

max_iterations = 4

# Domain of possible discrete values explored
vision_domain = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
metab_domain = (2, 3, 4)
v = len(vision_domain)
m = len(metab_domain)

# For plotting
xticks = [x - 0.5 for x in vision_domain]
xticks.append(xticks[-1] + 1)
yticks = [y - 0.5 for y in metab_domain]
yticks.append(yticks[-1] + 1)


def model(x):
    """ Run the Sugarscape model. """
    SS = SugarscapeCg(max_metabolism=x['metab'], max_vision=x['vision'])
    SS.verbose = False
    y =  SS.run_model(step_count=30)
    return {'y': y}


def run():
    """ Run ABC-SMC. """
    distance = lambda a, b: abs(a['y'] - b['y'])
    obs = {'y': 66}

    # priors
    # let each value in the domain have an equal prior probability
    prior = pyabc.Distribution(
              metab=pyabc.RV('rv_discrete', values=(metab_domain, [1/m] * m)),
              vision=pyabc.RV('rv_discrete', values=(vision_domain, [1/v] * v))
              )

    # transition kernels
    transition = pyabc.AggregatedTransition(mapping={
        'metab': pyabc.DiscreteJumpTransition(domain=metab_domain, p_stay=0.7),
        'vision': pyabc.DiscreteJumpTransition(domain=vision_domain, p_stay=0.7)})

    abc = pyabc.ABCSMC(model, prior, distance, transitions=transition, population_size=1000)
    history = abc.new(pyabc.create_sqlite_db_id(), obs)
    run_id = history.id
    print("Run ID:", run_id)
    history = abc.run(max_nr_populations=max_iterations)

    # Save abc history using shelve...
    db = shelve.open('%s/abc_history.shelf' % id)
    db['history'] = history
    db.close()
    # ... and save the distribution and weights using pickle
    # as there are sometimes issues saving the history object
    for t in range(max_iterations):
        df, w = history.get_distribution(t=t)
        with open('%s/df_%d.pkl' % (id, t), 'wb') as f:
            pickle.dump(df, f)
        with open('%s/w_%d.pkl' % (id, t), 'wb') as f:
            pickle.dump(w, f)
    return history


def plot_all(show=True):
    """ Plot each iteration of the ABC runs. """
    fig, axes = plt.subplots(max_iterations, 1, figsize=(6, 12))
    for t in range(max_iterations):
        with open('%s/df_%d.pkl' % (id, t), 'rb') as f:
            df = pickle.load(f)
        with open('%s/w_%d.pkl' % (id, t), 'rb') as f:
            w = pickle.load(f)
        axes[t].hist2d(x=df['vision'], y=df['metab'], weights=w, density=True,
                       bins=((xticks, yticks)), cmap='magma')
        axes[t].set_ylabel('max metabolism')
        axes[t].set_xticks(vision_domain)
        axes[t].set_yticks((2, 3, 4))
    axes[3].set_xlabel('max vision')
    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig('%s/abc_results.pdf' % id)


def plot_last(show=True):
    """ Plot the final iteration of the ABC runs. """
    with open('%s/df_%d.pkl' % (id, max_iterations-1), 'rb') as f:
        df = pickle.load(f)
    with open('%s/w_%d.pkl' % (id, max_iterations-1), 'rb') as f:
        w = pickle.load(f)
    fig, axes = plt.subplots(1, 1, figsize=(9, 3))
    p = plt.hist2d(x=df['vision'], y=df['metab'], weights=w, density=True,
                   bins=((xticks, yticks)), cmap='magma')
    plt.xlabel('max vision')
    plt.ylabel('max metabolism')
    plt.yticks((2, 3, 4))
    plt.colorbar(p[3])
    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig('%s/abc_results.pdf' % id)

if __name__ == '__main__':
    #run()
    #plot_all()
    plot_last()
