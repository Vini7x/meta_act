import tempfile
from pathlib import Path

import pandas as pd

from meta_act.ds_gen import dataset_generator, generate_datasets
from meta_act.metadb_craft import create_metadb


def test_createmetadb_onthefly():
    gen = dataset_generator([("HyperplaneGenerator",
                              {"n_features": [5, 10, 15]}),
                             ("LEDGeneratorDrift",
                              {"noise_percentage": [0.0, 0.1, 0.5],
                               "has_noise": [False, True],
                               "n_drift_features": [1, 3, 5]})],
                            max_samples=5000)
    metadb = create_metadb(gen, 5, stop_conditions={"max_datasets": 4},
                           max_failures=1)

    assert metadb is not None
    assert isinstance(metadb, pd.DataFrame)


def test_createmetadb_fixed_windows():
    gen = dataset_generator([("HyperplaneGenerator",
                              {"n_features": [5, 10, 15]}),
                             ("LEDGeneratorDrift",
                              {"noise_percentage": [0.0, 0.1, 0.5],
                               "has_noise": [False, True],
                               "n_drift_features": [1, 3, 5]})],
                            max_samples=5000)
    metadb = create_metadb(gen, 5, stop_conditions={"max_datasets": 4},
                           max_failures=1, fixed_windows_size=1000)

    assert metadb is not None
    assert isinstance(metadb, pd.DataFrame)


def test_createmetadb_limiter():
    gen = dataset_generator([("HyperplaneGenerator",
                              {"n_features": [5, 10, 15]}),
                             ("LEDGeneratorDrift",
                              {"noise_percentage": [0.0, 0.1, 0.5],
                               "has_noise": [False, True],
                               "n_drift_features": [1, 3, 5]})],
                            max_samples=5000)
    limits = (0.05, 0.9)
    metadb = create_metadb(gen, 5, stop_conditions={"max_datasets": 4},
                           max_failures=1, fixed_windows_size=1000,
                           fixed_z_val_threshold=limits)

    assert metadb is not None
    assert isinstance(metadb, pd.DataFrame)


def test_createmetadb_mean_acc():
    gen = dataset_generator([("HyperplaneGenerator",
                              {"n_features": [5, 10, 15]}),
                             ("LEDGeneratorDrift",
                              {"noise_percentage": [0.0, 0.1, 0.5],
                               "has_noise": [False, True],
                               "n_drift_features": [1, 3, 5]})],
                            max_samples=5000)
    metadb = create_metadb(gen, 5, stop_conditions={"max_datasets": 4},
                           max_failures=1, fixed_windows_size=1000,
                           wind_acc_summary="mean")

    assert metadb is not None
    assert isinstance(metadb, pd.DataFrame)


def test_createmetadb_savefile():
    gen = dataset_generator([("HyperplaneGenerator",
                              {"n_features": [5, 10, 15]}),
                             ("LEDGeneratorDrift",
                              {"noise_percentage": [0.0, 0.1, 0.5],
                               "has_noise": [False, True],
                               "n_drift_features": [1, 3, 5]})],
                            max_samples=5000)
    with tempfile.TemporaryDirectory() as tmpdir:
        outpath = f"{tmpdir}/metadb.csv"
        metadb = create_metadb(gen, 5, stop_conditions={"max_datasets": 4},
                               output_path=outpath, max_failures=1)

        assert metadb
        assert Path(outpath).exists()
        assert pd.read_csv(outpath).shape[1] > 1


def test_createmetadb_static():
    generators = [("HyperplaneGenerator",
                   {"n_features": [5, 10, 15]}),
                  ("LEDGeneratorDrift",
                   {"noise_percentage": [0.0, 0.1, 0.5],
                    "has_noise": [True],
                    "n_drift_features": [5]})]
    with tempfile.TemporaryDirectory() as tmpdir:
        for generator in generators:
            generate_datasets(generator[0],
                              tmpdir,
                              max_samples=10000,
                              **generator[1])

        dataset_files = [path.as_posix()
                         for path in Path(tmpdir).glob("*.csv")]
        metadb = create_metadb(dataset_files, 5)

        print(metadb)

        assert metadb is not None
        assert isinstance(metadb, pd.DataFrame)
