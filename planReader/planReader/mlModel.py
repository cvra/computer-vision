import cv2


class StatModel(object):
    def load(self, fn):
        self.model.load(fn)

    def save(self, fn):
        self.model.save(fn)


class KNearest(StatModel):
    def __init__(self, k=3):
        self.k = k
        self.model = cv2.ml.KNearest_create()

    def train(self, samples, responses):
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    def predict(self, samples):
        _, results, _, _ = self.model.findNearest(samples, self.k)
        return results.ravel()
