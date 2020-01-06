#!/usr/bin/env python

"""Tests for ImagesDataset."""

import random
import tempfile
import unittest
from pathlib import Path
import numpy as np
import nibabel as nib
import torchio
from torchio import INTENSITY, LABEL


class TestRandomElasticDeformation(unittest.TestCase):
    """Tests for `RandomElasticDeformation`."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.dir = Path(tempfile.mkdtemp())
        random.seed(42)
        np.random.seed(42)

        subject_a = {
            't1': dict(path=self.get_image_path('t1_a'), type=INTENSITY),
        }
        subject_b = {
            't1': dict(path=self.get_image_path('t1_b'), type=INTENSITY),
            'label': dict(path=self.get_image_path('label_b'), type=LABEL),
        }
        subject_c = {
            'label': dict(path=self.get_image_path('label_c'), type=LABEL),
        }
        subject_d = {
            't1': dict(path=self.get_image_path('t1_d'), type=INTENSITY),
            't2': dict(path=self.get_image_path('t2_d'), type=INTENSITY),
            'label': dict(path=self.get_image_path('label_d'), type=LABEL),
        }
        self.paths_list = [
            subject_a,
            subject_b,
            subject_c,
            subject_d,
        ]

    def tearDown(self):
        """Tear down test fixtures, if any."""
        import shutil
        shutil.rmtree(self.dir)

    def get_image_path(self, stem):
        data = np.random.rand(10, 20, 30)
        affine = np.eye(4)
        suffix = random.choice(('.nii.gz', '.nii'))
        path = self.dir / f'{stem}{suffix}'
        nib.Nifti1Image(data, affine).to_filename(str(path))
        path = str(path) if np.random.rand() > 0.5 else path
        return path

    def test_images(self):
        self.iterate_dataset(self.paths_list)

    def test_wrong_paths_list(self):
        with self.assertRaises(ValueError):
            self.iterate_dataset([])
        with self.assertRaises(ValueError):
            self.iterate_dataset(())
        with self.assertRaises(TypeError):
            self.iterate_dataset(0)
        with self.assertRaises(TypeError):
            self.iterate_dataset([0])
        with self.assertRaises(ValueError):
            self.iterate_dataset([{}])
        with self.assertRaises(ValueError):
            self.iterate_dataset([{}, {}])
        with self.assertRaises(FileNotFoundError):
            self.iterate_dataset(
                [{'t1': dict(path='notpath', type=INTENSITY)}, ])
        with self.assertRaises(ValueError):
            path = self.dir / 'test.txt'
            path.touch()
            self.iterate_dataset([{'t1': dict(path=path, type=INTENSITY)}, ])
        with self.assertRaises(KeyError):
            self.iterate_dataset([{'t1': dict(path='notpath')}, ])
        with self.assertRaises(KeyError):
            self.iterate_dataset([{'t1': dict(type=INTENSITY)}, ])
        with self.assertRaises(KeyError):
            self.iterate_dataset(
                [{'t1': dict(test='notpath', type=INTENSITY)}, ])
        with self.assertRaises(TypeError):
            self.iterate_dataset([{'t1': 6}, ])

    def test_others(self):
        dataset = torchio.ImagesDataset(
            self.paths_list, verbose=True, transform=lambda x: x)
        length = len(dataset)
        sample = dataset[0]
        paths_dict = {'t1': self.dir / 'test.nii.gz'}
        dataset.save_sample(sample, paths_dict)

    def iterate_dataset(self, paths_list):
        dataset = torchio.ImagesDataset(paths_list)
        for sample in dataset:
            pass
