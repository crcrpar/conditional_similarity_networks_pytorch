import os
from PIL import Image


def default_image_loader(path):
    return Image.open(path).convert('RGB')


class ZapposDataset(torch.utils.data.Dataset):

    def __init__(self, root, base_path, files_json_path, split='train',
                 conditions=None, transform=None, loader=default_image_loader):
        self.root = root
        self.base_path = base_path
        self.img_root = os.path.join(self.root, self.base_path)
        with open(os.path.join(self.root, files_json_path)) as f:
            self.all_files = [line.rstrip('\n') for line in f]
        if split == 'train':
            fnames = self.all_files['train']
        elif split == 'val':
            fnames = self.all_files['val']
        elif split == 'test':
            fnames = self.all_files['test']
        else:
            raise ValueError('invalid parameter for split.')
        self.files = fnames

        self.transform = transform
        self.loader = loader

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        path = os.path.join(self.img_root, self.files[index])
        if os.path.exists(path):
            img = self.loader(path)
            return img
        else:
            return None

    def split(self, split):
        return self.all_files[split]


def make_data_loader(root='data', base_path='ut-zap50k-images',
                     files_json_path='filenames.json', split='train',
                     batch_size=64, shuffle=False, **kwargs):
    """Make a loader of ZapposDataset.

    Args:
        root: path to directory including files_json.
        base_path: directory name of ut-zap50k-images.
        files_json_path: file contains all images' relative path from
            base_path.
        split: Dataset split to load, train, val, or test.
        batch_size: default size is 64. crcrpar confirmed that 256 is too
            large for 8GB memory.
        shuffle: default is False because I assume this loader is used
            for feature extranciton, not training.
    """
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    loader = torch.utils.data.DataLoader(
        AllZaposDataset(root, base_path, files_json_path, split,
                        transform=transforms.Compose([
                            transforms.Scale(112),
                            transforms.CenterCrop(112),
                            transforms.ToTensor(),
                            normalize,
                        ])),
        batch_size=batch_size, shuffle=shuffle, **kwargs)
    return loader
