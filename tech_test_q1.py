import pprint
import random
import argparse
import multiprocessing

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.utils import resample
from scipy.stats import gaussian_kde
from statsmodels.nonparametric.bandwidths import bw_silverman, bw_scott


pp = pprint.PrettyPrinter(depth=4)

# Reduces variance in results but won't eliminate it :-(
random.seed(42)
np.random.seed(42)


def print_df_summary(df):
    '''Calculate and print basic summary of dataframe'''

    print("Shape:", df.shape)

    total_nas = df.isna().sum().sum()
    rows_nas = df.isnull().any(axis=1).sum()
    cols_nas = df.isnull().any().sum()
    print('\nTotal NAs:', total_nas)
    print('Rows with NAs:', rows_nas)
    print('Cols with NAs:', cols_nas)

    print("\nInfo:")
    df.info()

    print("\nSummary stats:")
    print(df.describe())

    print("\nRaw data:")
    print(df)
    print("\n")


def sin_transformer(x, period=3600 * 24):
    '''Encode periodic features in non-monotonic way so no jump between
    first and last value of periodic range'''
    return np.sin(x / period * 2 * np.pi)


def cos_transformer(x, period=3600 * 24):
    '''Encode periodic features in non-monotonic way so no jump between
    first and last value of periodic range'''
    return np.cos(x / period * 2 * np.pi)


def kde_bandwidth(df, feature, bw_method='scott', verbose=False):
    '''In order to compare the kde's, they need to be calculated with the
    same bandwidth.  The default bandwidth depends on the number of
    observations, which can be different for each surgeon.  Here I
    calculate Scott's factor for each surgeon.  Then find the median of
    these values.
    num_dims - number of dimensions (1 for univariate data)
    '''

    # stastmodels
    # https://github.com/statsmodels/statsmodels/blob/main/statsmodels/nonparametric/bandwidths.py
    df_gb = df.groupby('surgeon').agg({feature: ['nunique', 'count', bw_scott, bw_silverman]})
    df_gb.columns = ['nunique', 'count', 'bw_scott', 'bw_silverman']

    # sklearn/scipy - bandwidths too wide
    num_dims = df.shape[1]
    df_gb['scott'] = df_gb['count'] ** (-1. / (num_dims + 4))
    df_gb['silverman'] = (df_gb['count'] * (num_dims + 2) / 4) ** (-1. / (num_dims + 4))

    # Note: bw='cv_ls' produces some very low estimates - NOT recommended
    #       bw='cv_ml' produces some errors
    sm_bws = []
    for i in range(8):
        df_i = df.loc[df['surgeon'] == 'user' + str(i), feature]
        dens_u = sm.nonparametric.KDEMultivariate(data=df_i, var_type='c', bw='cv_ls')
        sm_bws.append(dens_u.bw[0])
    df_gb['cv_ls'] = sm_bws

    if verbose:
        print('\n', feature)
        print(df_gb)

    return np.median(df_gb[bw_method])


def get_surgeon_data(df, i, feature, bandwidth=0.3, xs=np.linspace(-2, 2, 200)):
    '''Get kernel density estimate for surgeon'''

    ser_i = df.loc[df['surgeon'] == 'user' + str(i), feature]

    kde_i = gaussian_kde(ser_i, bw_method=bandwidth)
    y_i = kde_i(xs)

    return y_i


def kde_intersection(xs, y_i, y_j):
    '''Percent overlap between two kdes'''

    inters_y = np.minimum(y_i, y_j)
    area_inters_y = np.trapz(inters_y, xs)

    return area_inters_y * 100


def get_xs(xmin, xmax, n):
    '''Get x values used with kernel density estimates'''

    return np.linspace(xmin, xmax, n)


def bootstrap_sample(df):
    '''Resample data for bootstrap analysis'''

    strata_samples = []
    num_surgs = df['surgeon'].nunique()

    for i in range(num_surgs):
        X = df.loc[df['surgeon'] == 'user' + str(i), :]
        strata_sample = resample(X, n_samples=X.shape[0], replace=True)
        strata_samples.append(strata_sample)

    df_sample = pd.concat(strata_samples)

    return df_sample


def _inner_bootstrap(df, feature, bw_median, xs, i):
    '''Bootstrap function for multiprocessing'''

    df_sample = bootstrap_sample(df)
    sim = get_similarities(df_sample, feature, bw_median, xs)
    sim['sample'] = i

    return sim


def bootstrap_similarities(df, bw_median, xs, argv):
    '''Run bootstrap analysis'''

    feature = argv.feature
    samples = argv.samples
    verbose = argv.verbose
    sims = []

    num_cores = multiprocessing.cpu_count()

    if verbose:
        print('\nRunning bootstrap(samples=%d) using %d cores' % (samples, num_cores))

    if num_cores > 1:
        arg_iterable = [(df, feature, bw_median, xs, sample) for sample in range(samples)]
        with multiprocessing.Pool(num_cores) as pool:
            sims = pool.starmap(_inner_bootstrap, arg_iterable)
    else:
        for i in range(samples):
            sim = _inner_bootstrap(df, feature, bw_median, xs, i)
            sims.append(sim)

    bs_sims = pd.concat(sims)

    return bs_sims


def summarise_similarities(sims, feature):
    '''Summarise bootstrap similarities'''

    sims_gb = sims.groupby(['i', 'j'])[feature].describe(percentiles=[0.025, 0.975])
    sims_gb.drop('count', axis=1, inplace=True)

    return sims_gb.sort_values('mean', ascending=False)


def get_similarities(df, feature, bw_median, xs):
    '''Calculate similarities between surgeons'''

    ys = {}
    num_surgs = df['surgeon'].nunique()

    # Don't repeat inside nested loop
    for i in range(num_surgs):
        ys[i] = get_surgeon_data(df, i, feature, bandwidth=bw_median)

    sims = []

    for i in range(num_surgs):
        for j in range(num_surgs):
            if j > i:
                inters = kde_intersection(xs, ys[i], ys[j])
                sims.append([i, j, round(inters, 6)])

    similarity = pd.DataFrame(sims, columns=['i', 'j', 'intersection'])

    return similarity


def main(argv):
    '''main function'''

    df = pd.read_csv(argv.filename,
                     header=None,
                     names=['surgeon', 'notification_time'],
                     dtype={'surgeon': 'str', 'notification_time': 'str'})

    df['ds'] = pd.to_datetime(df['notification_time'], format='%H:%M:%S')
    df['secs'] = (df['ds'] - df['ds'].dt.normalize()).dt.total_seconds().astype(int)

    df['secs.sin'] = sin_transformer(df['secs'])
    df['secs.cos'] = cos_transformer(df['secs'])

    if argv.verbose:
        print_df_summary(df)

    df_gb = df.groupby('surgeon').agg({'secs': ['nunique', 'describe', 'skew', pd.Series.kurt]})
    df_gb.columns = ['nunique', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max',
                     'skew', 'kurtosis']
    df_gb['count'] = df_gb['count'].astype(int)
    if argv.verbose:
        print(df_gb)

    bw_medians = {}
    for feat in ['secs', 'secs.sin', 'secs.cos']:
        bw_medians[feat, argv.bw_method] = kde_bandwidth(df, feat, argv.bw_method, verbose=argv.verbose)

    if argv.verbose:
        print('\nbw_medians = ')
        pp.pprint(bw_medians)

    bw_median = bw_medians[argv.feature, argv.bw_method]
    if argv.verbose:
        print(f'{bw_median = }')
    xs = get_xs(-2, 2, 200)

    bs_similarity = bootstrap_similarities(df, bw_median, xs, argv)
    bs_sims_sum = summarise_similarities(bs_similarity, 'intersection')
    print('\nPercent overlap between users i and j:\n', bs_sims_sum)

    print("\nThe two most similar surgeons are: user%d and user%d\n" % (bs_sims_sum.index[0]))


def int_range(imin=None, imax=None):
    '''Check argparse integer range'''

    def check_range(x):
        x = int(x)

        if x < imin and imin is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]" % (x, imin, imax))

        if x > imax and imax is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]" % (x, imin, imax))

        return x

    return check_range


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find two most similar users from CSV file')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-fn', '--filename',
                          required=True,
                          help='File name for CSV input', type=str)

    opts = parser.add_argument_group('optional arguments')
    opts.add_argument('-v',  '--verbose',
                      help='Print additional information - default=%(default)s',
                      default=False, action="store_true")
    opts.add_argument('-bs', '--samples',
                      help='Bootstrap samples - default=%(default)s',
                      default=5000, type=int_range(10, 100000),
                      metavar="[10, 100000]")
    opts.add_argument('-ft', '--feature',
                      help='Feature name - default=%(default)s',
                      default='secs.cos', type=str,
                      choices=['secs', 'secs.sin', 'secs.cos'])
    opts.add_argument('-bw', '--bw_method',
                      help='Bandwidth method - default=%(default)s',
                      default='bw_scott', type=str,
                      choices=['bw_scott', 'bw_silverman', 'scott', 'silverman', 'cv_ls'])

    args = parser.parse_args()

    main(args)
