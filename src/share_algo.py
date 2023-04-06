import numpy as np
from PIL import Image
path = "C:/Users/user/PycharmProjects/Data_hiding/Data_hiding/images/"
def generate_shares(data, n,name):
    data = np.array(data, dtype='u1')
    src =[]
    # Generate images of same size
    shares = [np.zeros(data.shape).astype('u1') for i in range(n)]
    # Set random factors
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(data.shape[2]):
                remaining = data[i, j, k]
                for m in range(n - 1):
                    # Choose a random share value for this pixel
                    share_value = np.random.randint(0, remaining + 1)
                    shares[m][i, j, k] = share_value
                    remaining -= share_value
                # The last share gets the remaining value
                shares[-1][i, j, k] = remaining
    # Saving shares
    for i in range(n):
        img = Image.fromarray(shares[i])
        img.save(f"{path}/{name}-{i+1}.png", "PNG")
        src.append(f"{name}-{i+1}.png")
    return src

def compress_n_join_shares(shares,name):
    # Read in all the share images
    share_arrays = []
    for share_file in shares:
        share_arrays.append(np.asarray(Image.open(f"{path}/{share_file}")).astype('int16'))
    # Sum the share arrays element-wise to reconstruct the original data
    data = np.zeros(share_arrays[0].shape)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(data.shape[2]):
                pixel_sum = sum(share[i, j, k] for share in share_arrays)
                data[i, j, k] = pixel_sum
    # Save compressed image
    data = data.astype(np.dtype('u1'))
    img = Image.fromarray(data)
    img.save(f"{path}/compress-{name}.png", "PNG")
