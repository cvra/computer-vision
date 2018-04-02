import numpy as np
from .mlModel import KNearest


class Colors():
    def __init__(self, colors_group, color_idx):
        self._colors_group = colors_group
        self._color_idx = color_idx

        self.idx2color = dict()
        for color, idx in color_idx.items():
            self.idx2color[idx] = color

        samples_train, labels_train = self._generate_dataset()

        self.model = KNearest(k=3)
        self.model.train(samples_train, labels_train)

    def _generate_dataset(self):
        samples = list()
        labels = list()

        for colorname, colors in self._colors_group.items():
            for (r, g, b) in colors:
                label = self._color_idx[colorname]

                samples.append([r, g, b])
                labels.append(label)

        samples = np.array(samples, dtype=np.float32)
        labels = np.array(labels, dtype=np.int)

        return samples, labels

    def show_colors_group(self):
        for colorname, colors in self._colors_group.items():

            thumbnail = np.zeros([5, 0, 3], dtype=np.uint8)
            for idx, hexcolor in enumerate(colors):
                r, g, b = tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))

                tile = np.ones((5, 5, 3), np.uint8)
                tile[:, :, :] = np.array([r, g, b])

                thumbnail = np.hstack([thumbnail, tile])

            plt.figure(figsize=(15, 1))
            plt.axis('off')
            plt.imshow(thumbnail)
            plt.show()
