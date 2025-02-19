from numpy import array, float64, reshape, zeros
from numpy.random import shuffle
from PIL import Image
# if use_sklearn_kmeans:
#    from sklearn.cluster import KMeans
# else:
from scipy.cluster.vq import kmeans2 as kmeans

# from sklearn.utils import shuffle

# use_sklearn_kmeans = False


# from scipy.cluster.vq import vq

RANDOM_SAMPLE = 100


class ColorPalette:
    def __init__(self, image_path="", n_colors=64):
        self.colorbook = None
        self.kmeans = None

        if image_path:
            self.quantize(image_path, n_colors=n_colors)

    @staticmethod
    def recreate_image(codebook, labels, w, h):
        """Recreate the (compressed) image from the code book & labels"""
        d = codebook.shape[1]
        image = zeros((w, h, d))
        label_idx = 0
        for i in range(w):
            for j in range(h):
                image[i][j] = codebook[labels[label_idx]]
                label_idx += 1
        return image

    def apply_palette_to_image(self, image):
        # moi_image = image
        # moi_image = moi_image / float(255)
        # w2, h2, d2 = original_shape = tuple(moi_image.shape)
        # assert d2 == 3
        # moi_array = reshape(moi_image, (w2 * h2, d2))
        # labels = self.kmeans.predict(moi_array)
        # Display all results, alongside original image
        # plt.figure(1)
        # plt.clf()
        # ax = plt.axes([0, 0, 1, 1])
        # plt.axis('off')
        # plt.title('Original image (96,615 colors)')
        # plt.imshow(moi_image)

        # plt.figure(2)
        # plt.clf()
        # ax = plt.axes([0, 0, 1, 1])
        # plt.axis('off')
        # plt.title('Quantized image (64 colors, K-Means)')
        # plt.imshow(ColorPalette.recreate_image(self.kmeans.cluster_centers_, labels, w2, h2))

        # plt.show()
        pass

    @staticmethod
    def quantize_img(img, n):
        result = img.quantize(colors=n, kmeans=n).convert("RGB").getcolors()
        if len(result) == 2:
            return [result[0][1], result[1][1]]
        else:
            return [result[0][1], result[0][1]]
        # return (ColorPalette.average_colors(img,n)*255).astype(int)

    # deprecated:
    @staticmethod
    def average_colors(img, n_colors=2):
        sample_image = array(img, dtype=float64) / 255
        w, h, d = original_shape = tuple(sample_image.shape)
        assert d == 3
        image_array = reshape(sample_image, (w * h, d))

        # xxx:  use percentage of total pixs instead?
        image_array_sample = shuffle(image_array, random_state=0)[:RANDOM_SAMPLE]

        # if use_sklearn_kmeans:
        #    kmeans = KMeans(n_clusters=n_colors, random_state=0,n_init="auto").fit(image_array_sample)
        #    colorbook = kmeans.cluster_centers_
        # else:
        colorbook, _ = kmeans2(image_array_sample, n_colors, minit="points")

        return colorbook

    # should be able to take just io.imread images too:
    @staticmethod
    def quantize_pil_image(img, n_colors=2):
        sample_image = array(img, dtype=float64) / 255
        w, h, d = original_shape = tuple(sample_image.shape)
        assert d == 3
        image_array = reshape(sample_image, (w * h, d))

        # xxx:  use percentage of total pixs instead?
        image_array_sample = shuffle(image_array, random_state=0)[:RANDOM_SAMPLE]

        # if use_sklearn_kmeans:
        #    kmeans = KMeans(n_clusters=n_colors, random_state=0,n_init="auto").fit(image_array_sample)
        #    colorbook = kmeans.cluster_centers_
        #    labels = kmeans.predict(image_array)
        #    recreated_img = ColorPalette.recreate_image(kmeans.cluster_centers_, labels, w, h)
        # else:
        colorbook, labels = kmeans2(image_array_sample, n_colors, minit="points")
        recreated_img = ColorPalette.recreate_image(colorbook, labels, w, h)

        return recreated_img, colorbook

    def quantize(self, image_path, n_colors=64):
        sample_image = Image.open(image_path)

        # Convert to floats instead of the default 8 bits integer coding. Dividing by
        # 255 is important so that plt.imshow behaves works well on float data (need to
        # be in the range [0-1])
        sample_image = array(sample_image, dtype=float64) / 255

        w, h, d = original_shape = tuple(sample_image.shape)
        assert d == 3
        image_array = reshape(sample_image, (w * h, d))

        # xxx:  use percentage of total pixs instead?
        image_array_sample = shuffle(image_array, random_state=0)[:RANDOM_SAMPLE]
        # if use_sklearn_kmeans:
        #    self.kmeans = KMeans(n_clusters=n_colors, random_state=0,n_init="auto").fit(image_array_sample)
        #    self.colorbook = self.kmeans.cluster_centers_
        # else:
        self.colorbook, _ = kmeans2(image_array_sample, n_colors, minit="points")

        # Get labels for all points in the image
        # self.labels = self.kmeans.predict(image_array)
